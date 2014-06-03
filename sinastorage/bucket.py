#-*- coding:UTF-8 -*-
"""Bucket manipulation"""

from __future__ import absolute_import

import time
import hmac
import hashlib
import httplib
import urllib2
import datetime
import warnings
from contextlib import contextmanager
from urllib import quote_plus
from base64 import b64encode
import json
import sinastorage

from sinastorage.utils import (_amz_canonicalize, metadata_headers, metadata_remove_headers, 
                    rfc822_fmtdate, aws_md5, aws_urlquote, guess_mimetype, 
                    info_dict, expire2datetime, getSize, rfc822_parsedate)

from sinastorage.multipart import MultipartUpload,Part

sinastorage_domain = "sinastorage.com"

class ACL(object):
    ACL_GROUP_ANONYMOUSE    = 'GRPS000000ANONYMOUSE'        #匿名用户组 
    ACL_GROUP_CANONICAL     = 'GRPS0000000CANONICAL'        #全部认证通过的用户
    
    #full_control | write | write_acp | read | read_acp
    ACL_FULL_CONTROL        = 'full_control'
    ACL_WRITE               = 'write'
    ACL_WRITE_ACP           = 'write_acp'
    ACL_READ                = 'read'
    ACL_READ_ACP            = 'read_acp'

class SCSError(Exception):
    fp = None

    def __init__(self, message, **kwds):
        self.args = message, kwds.copy()
        self.msg, self.extra = self.args

    def __str__(self):
        rv = self.msg
        if self.extra:
            rv += " ("
            rv += ", ".join("%s=%r" % i for i in self.extra.iteritems())
            rv += ")"
        return rv

    @classmethod
    def from_urllib(cls, e, **extra):
        self = cls("HTTP error", **extra)
        self.hdrs = e.hdrs
        self.url = e.url
        for attr in ("reason", "code", "filename"):
            if attr not in extra and hasattr(e, attr):
                self.extra[attr] = getattr(e, attr)
        self.fp = getattr(e, "fp", None)
        if self.fp:
            # The except clause is to avoid a bug in urllib2 which has it read
            # as in chunked mode, but SCS gives an empty reply.
            try:
                self.data = data = self.fp.read()
            except (httplib.HTTPException, urllib2.URLError), e:
                self.extra["read_error"] = e
            else:
                data = data.decode("utf-8")
                begin, end = data.find("<Message>"), data.find("</Message>")
                if min(begin, end) >= 0:
                    self.msg = data[begin + 9:end]
        return self

    @property
    def code(self): return self.extra.get("code")

class KeyNotFound(SCSError, KeyError):
    @property
    def key(self): return self.extra.get("key")
    
class BadRequest(SCSError, KeyError):
    @property
    def key(self): return self.extra.get("key")

class StreamHTTPHandler(urllib2.HTTPHandler):
    pass

class StreamHTTPSHandler(urllib2.HTTPSHandler):
    pass

class AnyMethodRequest(urllib2.Request):
    def __init__(self, method, *args, **kwds):
        self.method = method
        urllib2.Request.__init__(self, *args, **kwds)

    def get_method(self):
        return self.method

def _upload_part(bucket_name, key_name, upload_id, part, source_path, offset, 
                 chunk_bytes, cb, num_cb, amount_of_retries=0, debug=1):
    from filechunkio import FileChunkIO
    
    """
    Uploads a part with retries.
    """
    if debug == 1:
        print "_upload_part(%s, %s, %s, %s, %s)" % (source_path, offset, bytes, upload_id, part.part_num)

    def _upload(retries_left=amount_of_retries):
        try:
            if debug == 1:
                print 'Start uploading part #%d ...' % part.part_num
            
            bucket = SCSBucket(bucket_name)
            with FileChunkIO(source_path, 'r', offset=offset,
                             bytes=chunk_bytes) as fp:
                headers={"Content-Length":str(chunk_bytes)}
                headers = bucket.put(key_name, fp, headers=headers, args={'partNumber':'%i'%part.part_num,
                                                         'uploadId':upload_id})
                part.etag = headers.getheader('ETag')
                return part
        except Exception, exc:
            if retries_left:
                return _upload(retries_left=retries_left - 1)
            else:
                print 'Failed uploading part #%d' % part.part_num
                raise exc
        else:
            if debug == 1:
                print '... Uploaded part #%d' % part.part_num

    return _upload()

class SCSRequest(object):
    urllib_request_cls = AnyMethodRequest
    subresource_need_to_sign = ('acl', 'location', 'torrent', 'website', 'logging', 'relax', 'meta', 'uploads', 'part', 'copy', 'multipart')
    subresource_kv_need_to_sign = ('uploadId', 'ip', 'partNumber')

    def __init__(self, bucket=None, key=None, method="GET", headers={},
                 args=None, data=None, subresource=None):
        headers = headers.copy()
        if data and "s-sina-sha1" not in headers:
            headers["s-sina-sha1"] = aws_md5(data)
        if "Date" not in headers:
            headers["Date"] = rfc822_fmtdate()
        if hasattr(bucket, "name"):
            bucket = bucket.name
        self.bucket = bucket
        self.key = key
        self.method = method
        self.headers = headers
        if not args:
            args = {}
        self.args = args
        self.args.setdefault('formatter','json')
        self.data = data
        self.subresource = subresource

    def __str__(self):
        return "<SCS %s request bucket %r key %r>" % (self.method, self.bucket, self.key)

    def descriptor(self):
        lines = (self.method,
                 self.headers.get("s-sina-sha1", ""),
                 self.headers.get("Content-Type", ""),
                 self.headers.get("Date", ""))
        preamb = "\n".join(str(line) for line in lines) + "\n"
        headers = _amz_canonicalize(self.headers)       #CanonicalizedAmzHeaders
        res = self.canonical_resource                   #CanonicalizedResource
        return "".join((preamb, headers, res))

    @property
    def canonical_resource(self):
        '''
            详见：http://sinastorage.sinaapp.com/developer/interface/aws/auth.html
        '''
        res = "/"
        if self.bucket:
            res += '%s/'%aws_urlquote(self.bucket)
        if self.key is not None:
            res += "%s" % aws_urlquote(self.key)
        if self.subresource:
            if self.subresource in self.subresource_need_to_sign:
                res += "?%s" % aws_urlquote(self.subresource)
        if self.args:
            rv = {}
            for key, value in self.args.iteritems():
#                 key = key.lower()
                if key in self.subresource_kv_need_to_sign:
                    rv[key] = value
            
            if len(rv) > 0 :
                parts = []
                for key in sorted(rv):
                    parts.append("%s=%s" % (key, rv[key]))
                res += "%s%s" % ('&' if self.subresource and self.subresource in self.subresource_need_to_sign else '?', "&".join(parts))
        return res

    def sign(self, cred):
        '''
            对stringToSign进行签名
            http://sinastorage.sinaapp.com/developer/interface/aws/auth.html
        '''
        stringToSign = self.descriptor()
        print stringToSign
        key = cred.secret_key.encode("utf-8")
        hasher = hmac.new(key, stringToSign.encode("utf-8"), hashlib.sha1)
        sign = b64encode(hasher.digest())[5:15]     #ssig
        '''
            Authorization=SINA product:/PL3776XmM
            Authorization:"SINA"+" "+"accessKey":"ssig"
        '''
        self.headers["Authorization"] = "SINA %s:%s" % (cred.access_key, sign)
        return sign

    def urllib(self, bucket):
        if hasattr(self.data,'offset') and hasattr(self.data,'bytes'):      #filechunkio
            data = self.data
        elif hasattr(self.data,'fileno'):                                   #file like
            data = self.data
        else:
            data = self.data
            
        print self.headers
        return self.urllib_request_cls(self.method, self.url(bucket.base_url),
                                       data=data, headers=self.headers)

    def url(self, base_url, arg_sep="&"):
        url = base_url + "/"
        if self.key:
            url += aws_urlquote(self.key)
        if self.subresource or self.args:
            ps = []
            if self.subresource:
                ps.append(self.subresource)
            if self.args:
                args = self.args
                if hasattr(args, "iteritems"):
                    args = args.iteritems()
                args = ((quote_plus(k), quote_plus(v)) for (k, v) in args)
                args = arg_sep.join("%s=%s" % i for i in args)
                ps.append(args)
            url += "?" + "&".join(ps)
        return url

class SCSFile(str):
    def __new__(cls, value, **kwds):
        return super(SCSFile, cls).__new__(cls, value)

    def __init__(self, value, **kwds):
        kwds["data"] = value
        self.kwds = kwds

    def put_into(self, bucket, key):
        return bucket.put(key, **self.kwds)

class SCSListing(object):
    """Representation of a single pageful of SCS bucket listing data."""

    truncated = None

    def __init__(self, jsonObj):
        self.resultDict = jsonObj
        self.truncated = self.resultDict['IsTruncated']             #Specifies whether (true) or not (false) all of the results were returned.
        self.marker = self.resultDict['Marker']
        self.prefix = self.resultDict['Prefix']
        self.delimiter = self.resultDict['Delimiter']
        self.contents_quantity = self.resultDict['ContentsQuantity']
        self.common_prefixes_quantity = self.resultDict['CommonPrefixesQuantity']
        self.next_marker = self.resultDict['NextMarker']             #下一页第一条游标

    def __iter__(self):
        
        commonPrefixes = self.resultDict['CommonPrefixes']
        for entry in commonPrefixes:
            item = self._json2item(entry,True)
            yield item
        
        contents = self.resultDict['Contents']
        for entry in contents:
            item = self._json2item(entry)
            yield item

    @classmethod
    def parse(cls, resp):
        return cls(json.loads(resp.read()))

    def _json2item(self, entry, prefix=False):
        
        if prefix :
            ''' 目录 
                {
                    "Prefix": "10000/"
                },
            '''
            isPrefix=True
            return (entry['Prefix'], isPrefix)
        else:
            ''' 文件
                {
                    "SHA1": "61bb70865c151ee0d7ed49ccafd509",
                    "Name": "aa.pdf",
                    "Expiration-Time": null,
                    "Last-Modified": "Tue, 25 Mar 2014 11:16:06 UTC",
                    "Owner": "SINA00000",
                    "MD5": "8ce3e6c0a9818162151",
                    "Content-Type": "application/pdf",
                    "Size": 2430
                },
            '''
            get = lambda tag: entry[tag]
            sha1 = get("SHA1")
            name = get("Name")
            expiration_time = rfc822_parsedate(get("Expiration-Time")) if get("Expiration-Time") else None
            modify = rfc822_parsedate(get("Last-Modified"))
            owner = get("Owner")
            md5 = get("MD5")
            content_type = get("Content-Type")
            size = int(get("Size"))
            isPrefix=False
            return (name, isPrefix, sha1, expiration_time, modify, owner, md5, content_type, size)

class SCSBucket(object):
    default_encoding = "utf-8"
    n_retries = 10

    def __init__(self, name=None, base_url=None, timeout=None, secure=False):
        scheme = ("http", "https")[int(bool(secure))]
        if not base_url:
            base_url = "%s://%s" % (scheme, sinastorage_domain)
            if name:
                base_url += "/%s" % aws_urlquote(name)
        elif secure is not None:
            if not base_url.startswith(scheme + "://"):
                raise ValueError("secure=%r, url must use %s"
                                 % (secure, scheme))
        self.opener = self.build_opener()
        self.name = name
        if sinastorage.getDefaultAppInfo() is None :
            raise ValueError("access_key and secret_key must not be None! Please set sinastorage.setDefaultAppInfo('access_key', 'secret_key') first!")
        self.access_key = sinastorage.getDefaultAppInfo().access_key
        self.secret_key = sinastorage.getDefaultAppInfo().secret_key
        
        self.base_url = base_url
        self.timeout = timeout

    def __str__(self):
        return "<%s %s at %r>" % (self.__class__.__name__, self.name, self.base_url)

    def __repr__(self):
        return self.__class__.__name__ + "(%r, access_key=%r, base_url=%r)" % (
            self.name, self.access_key, self.base_url)

    def __getitem__(self, name): return self.get(name)
    def __delitem__(self, name): return self.delete(name)
    def __setitem__(self, name, value):
        if hasattr(value, "put_into"):
            return value.put_into(self, name)
        else:
            return self.put(name, value)
    def __contains__(self, name):
        try:
            self.info(name)
        except KeyError:
            return False
        else:
            return True

    @contextmanager
    def timeout_disabled(self):
        (prev_timeout, self.timeout) = (self.timeout, None)
        try:
            yield
        finally:
            self.timeout = prev_timeout

    @classmethod
    def build_opener(cls):
        return urllib2.build_opener(StreamHTTPHandler, StreamHTTPSHandler)

    def request(self, *a, **k):
        k.setdefault("bucket", self.name)
        return SCSRequest(*a, **k)

    def send(self, scsreq):
        scsreq.sign(self)
        for retry_no in xrange(self.n_retries):
            req = scsreq.urllib(self)
            try:
                if self.timeout:
                    response = self.opener.open(req, timeout=self.timeout)
                else:
                    response = self.opener.open(req)
                
                return response
            except (urllib2.HTTPError, urllib2.URLError), e:
                # If SCS gives HTTP 500, we should try again.
                ecode = getattr(e, "code", None)
                if ecode == 500:
                    print '=======500========'
                    continue
                elif ecode == 404:
                    exc_cls = KeyNotFound
                elif ecode == 400:
                    exc_cls = BadRequest
                else:
                    exc_cls = SCSError
                raise exc_cls.from_urllib(e, key=scsreq.key)
        else:
            raise RuntimeError("ran out of retries")  # Shouldn't happen.

    def make_request(self, *a, **k):
        warnings.warn(DeprecationWarning("make_request() is deprecated, "
                                         "use request() and send()"))
        return self.send(self.request(*a, **k))

    def get(self, key):
        response = self.send(self.request(key=key))
        response.scs_info = info_dict(dict(response.info()))
        return response

    def info(self, key):
        response = self.send(self.request(method="HEAD", key=key))
        rv = info_dict(dict(response.info()))
        response.close()
        return rv
<<<<<<< HEAD
    
    def meta(self, key=None):
        response = self.send(self.request(method="GET", key=key, subresource='meta'))
        metaResult = json.loads(response.read())
        response.close()
        return metaResult
=======
>>>>>>> 23510f5a09ce5379825ccbcb8968e5895ff04c5e

    def put(self, key, data=None, acl=None, metadata={}, mimetype=None,
            transformer=None, headers={},args=None,subresource=None):
        if isinstance(data, unicode):
            data = data.encode(self.default_encoding)
        headers = headers.copy()
        if mimetype:
            headers["Content-Type"] = str(mimetype)
        elif "Content-Type" not in headers:
            headers["Content-Type"] = guess_mimetype(key)
        headers.update(metadata_headers(metadata))
        if acl: headers["X-AMZ-ACL"] = acl
        if transformer: data = transformer(headers, data)
        if "Content-Length" not in headers:
#             if isinstance(data, file)  isinstance(data, FileChunkIO):
            if hasattr(data,'fileno'):
                headers["Content-Length"] = str(getSize(data.name))
            else:
                headers["Content-Length"] = str(len(data))
        if "s-sina-sha1" not in headers:
            headers["s-sina-sha1"] = aws_md5(data)
        scsreq = self.request(method="PUT", key=key, data=data, headers=headers, 
                              args=args, subresource=subresource)
        response = self.send(scsreq)
        headers = response.info()
        response.close()
        return headers
                
    
    def put_relax(self,key,sina_sha1, s_sina_length, acl=None, 
                  metadata={}, mimetype=None,headers={}):
        '''
            上传接口Relax
            REST型PUT上传，但不上传具体的文件内容。而是通过SHA-1值对系统内文件进行复制。
        '''
        if isinstance(sina_sha1, unicode):
            sina_sha1 = sina_sha1.encode(self.default_encoding)
        headers = headers.copy()
        if mimetype:
            headers["Content-Type"] = str(mimetype)
        elif "Content-Type" not in headers:
            headers["Content-Type"] = guess_mimetype(key)
        if sina_sha1 == None:
            raise ValueError("sina_sha1 must not None!!")
        if "s-sina-sha1" not in headers:
            headers["s-sina-sha1"] = sina_sha1
        if s_sina_length == 0:
            raise ValueError("s_sina_length must bigger than 0!!")
        if "s-sina-length" not in headers:
            headers["s-sina-length"] = s_sina_length
        headers.update(metadata_headers(metadata))
        if acl: headers["X-AMZ-ACL"] = acl
        if "Content-Length" not in headers:
            headers["Content-Length"] = 0
        scsreq = self.request(method="PUT", key=key, headers=headers,subresource='relax')
        self.send(scsreq).close()
        
    def update_meta(self, key, metadata={}, remove_metadata=[], acl=None, 
                    mimetype=None, headers={}):
        '''
            更新文件meta信息
            删除meta功能暂时不可用
        '''
        headers = headers.copy()
        if mimetype:
            headers["Content-Type"] = str(mimetype)
        elif "Content-Type" not in headers:
            headers["Content-Type"] = guess_mimetype(key)
        headers.update(metadata_headers(metadata))
        headers.update(metadata_remove_headers(remove_metadata))
        if acl: headers["X-AMZ-ACL"] = acl
        if "Content-Length" not in headers:
            headers["Content-Length"] = 0
        scsreq = self.request(method="PUT", key=key, headers=headers, subresource='meta')
        self.send(scsreq).close()   

    def acl_info(self, key, mimetype=None, headers={}):
        '''
            获取文件的acl信息
        '''
        headers = headers.copy()
        if mimetype:
            headers["Content-Type"] = str(mimetype)
        elif "Content-Type" not in headers:
            headers["Content-Type"] = guess_mimetype(key)
        if "Content-Length" not in headers:
            headers["Content-Length"] = 0
        scsreq = self.request(key=key, args={'formatter':'json'}, headers=headers, subresource='acl')
        response = self.send(scsreq)
        aclResult = json.loads(response.read())
        response.close()
        return aclResult
    
    def update_acl(self, key, acl={}, mimetype=None, headers={}):
        '''
            设置文件、bucket的acl
            组：
            GRPS0000000CANONICAL : 全部认证通过的用户
            GRPS000000ANONYMOUSE : 匿名用户
            
            ID：
            SINA0000001001HBK3UT、......
            
            权限(小写):
            FULL_CONTROL | WRITE | WRITE_ACP | READ | READ_ACP
            
            格式:
            {  
                'SINA0000000000000001' :  [ "read", "read_acp" , "write", "write_acp" ],
                'GRPS000000ANONYMOUSE' :  [ "read", "read_acp" , "write", "write_acp" ],
                'GRPS0000000CANONICAL' :  [ "read", "read_acp" , "write", "write_acp" ],
            }
        '''
        headers = headers.copy()
        if mimetype:
            headers["Content-Type"] = str(mimetype)
        elif "Content-Type" not in headers:
            headers["Content-Type"] = 'text/json'
        aclJson = json.dumps(acl)
        if "Content-Length" not in headers:
            headers["Content-Length"] = str(len(aclJson))
        scsreq = self.request(method="PUT", key=key, data=aclJson, headers=headers, subresource='acl')
        self.send(scsreq).close()

    def delete(self, key):
        try:
            resp = self.send(self.request(method="DELETE", key=key))
        except KeyNotFound, e:
            e.fp.close()
            return False
        else:
            return 200 <= resp.code < 300

    def copy(self, source, key, acl=None, metadata=None,
             mimetype=None, headers={}):
        """
            注意：
            source    必须从bucket开始，如：'/cloud0/aaa.txt'
        """
        headers = headers.copy()
        headers.update({"Content-Type": mimetype or guess_mimetype(key)})
        if "Content-Length" not in headers:
            headers["Content-Length"] = 0
        headers["X-AMZ-Copy-Source"] = source
        if acl: headers["X-AMZ-ACL"] = acl
        if metadata is not None:
            headers["X-AMZ-Metadata-Directive"] = "REPLACE"
            headers.update(metadata_headers(metadata))
        else:
            headers["X-AMZ-Metadata-Directive"] = "COPY"
        self.send(self.request(method="PUT", key=key, headers=headers)).close()

    def _get_listing(self, args):
        return SCSListing.parse(self.send(self.request(key='', args=args)))

    def listdir(self, prefix=None, marker=None, limit=None, delimiter=None):
        """
        List bucket contents.

        return a generator SCSListing
        Yields tuples of (name, isPrefix, sha1, expiration_time, modify, owner, md5, content_type, size).

        *prefix*, if given, predicates `key.startswith(prefix)`.
        *marker*, if given, predicates `key > marker`, lexicographically.
        *limit*, if given, predicates `len(keys) <= limit`.

        *key* will include the *prefix* if any is given.

        .. note:: This method can make several requests to SCS if the listing is
                  very long.
        """
        m = (("prefix", prefix),
             ("marker", marker),
             ("max-keys", limit),
             ("delimiter", delimiter),
             ("formatter","json"))
        args = dict((str(k), str(v)) for (k, v) in m if v is not None)
        
        listing = self._get_listing(args)
        return listing
#         while listing:
#             for item in listing:
#                 yield item
#  
#             if limit is None and listing.truncated:
#                 args["marker"] = listing.next_marker
#                 listing = self._get_listing(args)
#             else:
#                 break
    
    def list_buckets(self):
        """
            List buckets.
            Yields tuples of (Name, CreationDate).
        """
        response = self.send(self.request(key=''))
        bucketJsonObj = json.loads(response.read())
        response.close()
        
        for item in bucketJsonObj['Buckets']:
            entry = (item['Name'],rfc822_parsedate(item['CreationDate']))
            yield entry

    def make_url(self, key, args=None, arg_sep="&"):
        scsreq = self.request(key=key, args=args)
        return scsreq.url(self.base_url, arg_sep=arg_sep)

    def make_url_authed(self, key, expire=datetime.timedelta(minutes=5), 
                        ip=None, cheese=None, fn=None):
        """Produce an authenticated URL for scs object *key*.

        *expire* is a delta or a datetime on which the authenticated URL
        expires. It defaults to five minutes, and accepts a timedelta, an
        integer delta in seconds, or a datetime.

        To generate an unauthenticated URL for a key, see `B.make_url`.
        """
        expire = expire2datetime(expire)
        expire = time.mktime(expire.timetuple()[:9])
        expire = str(int(expire))
        scsreq = self.request(key=key, headers={"Date": expire})
        sign = scsreq.sign(self)
        args_list = {"KID": 'sina,%s'%self.access_key,
                      "Expires": expire,
                      "ssig": sign}
        if ip:
            args_list['ip'] = ip
        if cheese:
            args_list['cheese'] = cheese
        if fn:
            args_list['fn'] = fn
        scsreq.args = args_list.items()
        return scsreq.url(self.base_url, arg_sep="&")

    def url_for(self, key, authenticated=False,
                expire=datetime.timedelta(minutes=5)):
        msg = "use %s instead of url_for(authenticated=%r)"
        dep_cls = DeprecationWarning
        if authenticated:
            warnings.warn(dep_cls(msg % ("make_url_authed", True)))
            return self.make_url_authed(key, expire=expire)
        else:
            warnings.warn(dep_cls(msg % ("make_url", False)))
            return self.make_url(key)

    def put_bucket(self, config_xml=None, acl=None):
        if config_xml:
            if isinstance(config_xml, unicode):
                config_xml = config_xml.encode("utf-8")
            headers = {"Content-Length": len(config_xml),
                       "Content-Type": "text/xml"}
        else:
            headers = {"Content-Length": "0"}
        if acl:
            headers["X-AMZ-ACL"] = acl
        resp = self.send(self.request(method="PUT", key=None,
                                      data=config_xml, headers=headers))
        resp.close()
        return resp.code == 200

    def delete_bucket(self):
        return self.delete(None)
        
        
    '''
    multiple upload
    '''
    def initiate_multipart_upload(self, key_name, acl=None, metadata={}, mimetype=None,
            headers={}):
        ''' 初始化分片上传 
        
            return type : dict
                {
                    u'UploadId': u'535dd723761d4f14a7210945cd7dea11', 
                    u'Key': u'test-python.zip', 
                    u'Bucket': u'create-a-bucket'
                }
        '''
        headers = headers.copy()
        if mimetype:
            headers["Content-Type"] = str(mimetype)
        elif "Content-Type" not in headers:
            headers["Content-Type"] = guess_mimetype(key_name)
        headers.update(metadata_headers(metadata))
        if acl: headers["X-AMZ-ACL"] = acl
        headers["Content-Length"] = "0"
        scsreq = self.request(method="POST", key=key_name, headers=headers, subresource='multipart')
        response = self.send(scsreq)
        initMultipartUploadResult = json.loads(response.read())
        response.close()
        multipart = MultipartUpload(self)
        multipart.upload_id = initMultipartUploadResult["UploadId"]
        multipart.bucket_name = initMultipartUploadResult["Bucket"]
        multipart.key_name = initMultipartUploadResult["Key"]
        return multipart
    
    def complete_multipart_upload(self, multipart):
        
        jsonArray = []
        for part in multipart.parts:
            jsonDict = {}
            jsonDict['PartNumber']=part.part_num
            jsonDict['ETag']=part.etag
            jsonArray.append(jsonDict)
        
        data = json.dumps(jsonArray)
        
        headers = {}
        headers["Content-Type"] = guess_mimetype(multipart.key_name)
        headers["Content-Length"] = str(len(data))
        if "s-sina-sha1" not in headers:
            headers["s-sina-sha1"] = aws_md5(data)
        
        scsreq = self.request(method="POST", data=data, headers=headers, key=multipart.key_name, args={'uploadId':multipart.upload_id})
        response = self.send(scsreq)
        response.close()
        
    
    def list_parts(self,upload_id,key_name):
        ''' 列出已经上传的所有分块 '''
        headers = {}
        headers["Content-Type"] = 'text/xml'
        headers["Content-Length"] = 0
        
        scsreq = self.request(method="GET", headers=headers, key=key_name, args={'uploadId':upload_id})
        response = self.send(scsreq)
        parts = json.loads(response.read())
        response.close()
        return parts
    
        
    def multipart_upload(self, key_name, source_path, acl=None, metadata={}, mimetype=None,
            headers={}, cb=None, num_cb=None):
        try:
            # multipart portions copyright Fabian Topfstedt
            # https://pypi.python.org/pypi/filechunkio/1.5
        
            import math
            import mimetypes
            from multiprocessing import Pool
            from filechunkio import FileChunkIO
            multipart_capable = True
            parallel_processes = 4
            min_bytes_per_chunk = 5 * 1024 * 1024                     #每片分片最大文件大小
            usage_flag_multipart_capable = """ [--multipart]"""
            usage_string_multipart_capable = """
                multipart - Upload files as multiple parts. This needs filechunkio.
                            Requires ListBucket, ListMultipartUploadParts,
                            ListBucketMultipartUploads and PutObject permissions."""
        except ImportError as err:
            multipart_capable = False
            usage_flag_multipart_capable = ""
            usage_string_multipart_capable = '\n\n     "' + \
                err.message[len('No module named '):] + \
                '" is missing for multipart support '
            
            raise err
            
        """
        Parallel multipart upload.
        """
        multipart = self.initiate_multipart_upload(key_name, acl, metadata, mimetype, headers)
        source_size = getSize(source_path)
        bytes_per_chunk = max(int(math.sqrt(min_bytes_per_chunk) * math.sqrt(source_size)),
                              min_bytes_per_chunk)
        chunk_amount = int(math.ceil(source_size / float(bytes_per_chunk)))
        multipart.bytes_per_part = bytes_per_chunk
        multipart.parts_amount = chunk_amount
        
        pool = Pool(processes=parallel_processes)
        i = 0
        for part in multipart.get_next_part():
            offset = i * bytes_per_chunk
            remaining_bytes = source_size - offset
            chunk_bytes = min([bytes_per_chunk, remaining_bytes])

            pool.apply_async(_upload_part, [self.name, key_name, multipart.upload_id, part, source_path, offset, chunk_bytes,
                                            cb, num_cb], callback = lambda part : multipart.parts.append(part))
#             _upload_part(self.name, key_name, multipart.upload_id, part, source_path, offset, chunk_bytes,
#                                             cb, num_cb)
            i = i + 1
            
        pool.close()
        pool.join()
    
        if len(multipart.parts) == chunk_amount:
            self.complete_multipart_upload(multipart)
#             multipart.complete_upload()
#             key = bucket.get_key(keyname)
#             key.set_acl(acl)
        else:
#             mp.cancel_upload()
            raise RuntimeError("multipart upload is failed!!")
        

class ReadOnlySCSBucket(SCSBucket):
    """Read-only SCS bucket.

    Mostly useful for situations where urllib2 isn't available (e.g. Google App
    Engine), but you still want the utility functions (like generating
    authenticated URLs, and making upload HTML forms.)
    """

    def build_opener(self):
        return None
