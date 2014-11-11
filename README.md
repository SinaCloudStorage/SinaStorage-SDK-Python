#SinaStorage SDK

[![Build Status](https://travis-ci.org/SinaCloudStorage/SinaStorage-SDK-Python.png?branch=master)](https://travis-ci.org/SinaCloudStorage/SinaStorage-SDK-Python)
[![Coverage Status](https://coveralls.io/repos/SinaCloudStorage/SinaStorage-SDK-Python/badge.png)](https://coveralls.io/r/SinaCloudStorage/SinaStorage-SDK-Python)
[![Build Status](https://pypip.in/v/scs-sdk/badge.png)](https://pypi.python.org/pypi/scs-sdk/)
[![Egg Status](https://pypip.in/egg/scs-sdk/badge.svg)](https://pypi.python.org/pypi/scs-sdk/)


##概述
新浪云存储Python平台SDK为第三方应用提供了简单易用的API调用服务，使第三方客户端无需了解复杂的验证机制即可进行授权、上传、下载等文件操作。

##SDK 环境要求

* Python 2.6
* Python 2.7
* Python 3.3
* Python 3.4


##SDK 安装

* 通过pip安装:

```
$ pip install scs-sdk
```

* 下载源码安装

```
$ git clone https://github.com/SinaCloudStorage/SinaStorage-SDK-Python.git
$ cd SinaStorage-SDK-Python
$ python setup.py install
```

##快速上手

###1. 创建bucket访问对象：
```python
from sinastorage.bucket import SCSBucket
import sinastorage

#设置access_key,secret_key
sinastorage.setDefaultAppInfo('你的accesskey', '你的secretkey')
s = SCSBucket('bucket的名称',secure=False)	# secure=True 采用https访问方式
print s  
#<SCSBucket ... at 'http://sinastorage.com/...'>
```

###2. bucket 操作:
* 创建bucket
```python
s = SCSBucket('需要创建的bucket名称')
s.put_bucket()
```
* 删除bucket:
```python
s = SCSBucket('需要删除的bucket名称')
s.delete_bucket()
```
* 列出所有bucket:
```python
s = SCSBucket()							#此处不要填写任何bucket名称
buckets_generator = s.list_buckets()	#返回generator，直接迭代即可
for bucket in buckets_generator:
    print bucket

#(bucketName,creationDate)				#tuple类型
```

* 获取bucket Meta信息:
```python
s = SCSBucket('bucket的名称')
metaDict = s.meta()
print metaDict
#{u'DeleteQuantity': 186, u'DeleteCapacity': 1699524638, u'Capacity': 2657406529, u'PoolName': u'plSAE', u'ProjectID': 4174, u'SizeC': 0, u'DownloadCapacity': 7327841538, u'UploadQuantity': 240, u'CapacityC': 0, u'ACL': {u'GRPS000000ANONYMOUSE': [u'read', u'write_acp'], u'SINA0000001001NHT3M7': [u'read', u'write', u'read_acp', u'write_acp'], u'GRPS0000000CANONICAL': [u'read', u'write', u'read_acp', u'write_acp']}, u'Project': u'test11', u'UploadCapacity': 4356931167, u'RelaxUpload': True, u'DownloadQuantity': 2546, u'Last-Modified': u'Fri, 28 Mar 2014 09:07:45 UTC', u'QuantityC': 0, u'Owner': u'SINA000000xxxxxxx', u'Quantity': 54}

```

###3. object 操作:
* 上传文件/内容:
```python
#文件内容
s = SCSBucket('bucket的名称')
scsResponse = s.put('文件上传路径',u'文件内容')

#文件
s = SCSBucket('bucket的名称')
s.putFile('文件上传路径', '本地文件路径', 上传回调函数)

```
* 秒传文件:
```python
s = SCSBucket('bucket的名称')
s.put_relax('文件上传路径', '被秒传文件的sina_sha1值', 被秒传文件的文件长度s_sina_length)
```
* 复制文件:
```python
s = SCSBucket('bucket的名称')
#注意：source    必须从bucket开始，如：'/bucketname/file.txt'
s.copy(source='/源文件bucket名称/源文件uri地址', key='文件上传路径')
```
* 列文件目录:
```python
s = SCSBucket('bucket的名称')
#返回generator对象
files_generator = s.listdir(prefix='文件名前缀', marker='Key的初始位置', limit=返回条数, delimiter='折叠字符')

#相关信息，通过generator属性获得
print ('truncated : %r\n'
'marker:%r\n'
'prefix:%r\n'
'delimiter:%r\n'
'contents_quantity:%r\n'
'common_prefixes_quantity:%r\n'
'next_marker:%r'%(files_generator.truncated, 
                  files_generator.marker,
                  files_generator.prefix,
                  files_generator.delimiter,
                  files_generator.contents_quantity,
                  files_generator.common_prefixes_quantity,
                  files_generator.next_marker))
#列目录
for item in files_generator:
    print item

#(name, isPrefix, sha1, expiration_time, modify, owner, md5, content_type, size)
```

* 下载文件:
```python
s = SCSBucket('bucket的名称')
response = s['a/asdf/新建 文本文档.txt']
#保存文件至本地
CHUNK = 16 * 1024
with open('本地目标文件地址', 'wb') as fp:
    while True:
        chunk = response.read(CHUNK)
        if not chunk: break
        fp.write(chunk)
            
```

* 删除文件:
```python
s = SCSBucket('bucket的名称')
del s["需要删除的文件路径"]
```
* 获取文件信息:
```python
s = SCSBucket('bucket的名称')
info = s.info('服务器端文件路径')
print info['mimetype']
#application/pdf
print info['size']
#2433230
print info
#{'mimetype': 'application/pdf', 'modify': datetime.datetime(2014, 4, 1, 6, 58, 58), 'headers': {'content-length': '2433230', ...}, 'date': datetime.datetime(2014, 4, 1, 9, 14, 57), 'metadata': {'crc32': 'DDEF42FA', ...}, 'size': 2433230}
```
* 修改文件meta信息:
```python
s = SCSBucket('bucket的名称')
s.update_meta('服务器端文件路径', {'自定义属性名':'自定义属性值','file_meta_key':'meta_value'})
```
* 获取文件acl信息:
```python
s = SCSBucket('bucket的名称')
print s.acl_info('服务器端文件路径')
#{u'Owner': u'SINA000000...', u'ACL': {u'GRPS000000ANONYMOUSE': [u'read'], u'GRPS0000000CANONICAL': [u'read_acp', u'write_acp']}}
```
* 修改文件acl信息:
```python
from sinastorage.bucket import SCSBucket,ACL
s = SCSBucket('bucket的名称')
acl = {}
acl[ACL.ACL_GROUP_ANONYMOUSE] = [ACL.ACL_READ]
acl[ACL.ACL_GROUP_CANONICAL] = [ACL.ACL_READ_ACP,ACL.ACL_WRITE_ACP]

s.update_acl('服务器端文件路径', acl)
```

* 获取文件Meta信息:
```python
s = SCSBucket('bucket的名称')
metaDict = s.meta('服务器端文件路径')
print metaDict
#{u'Info': None, u'File-Name': u'aaaa.txt', u'Info-Int': None, u'Content-MD5': u'86924f3b03cc23f04bcb3f3c1e13e57e', u'Last-Modified': u'Fri, 04 Jul 2014 06:49:03 UTC', u'Content-SHA1': u'9b8c7c8b7654339d3301d95945a6933212bb50b0', u'Owner': u'SINA000000xxxxxxx', u'Type': u'application/octet-stream', u'File-Meta': {u'Content-Type': u'application/octet-stream', u'x-amz-meta-crc32': u'75414E4E'}, u'Size': 5253200}

```

* 分片上传:

```python
from sinastorage.bucket import SCSBucket,ACL
s = SCSBucket('bucket的名称')
s.multipart_upload('服务器端文件路径', '本地文件路径')
```

* 列出已经上传的所有分块:

```python
from sinastorage.bucket import SCSBucket,ACL
s = SCSBucket('bucket的名称')
print s.list_parts('upload_id', '服务器端文件路径')
```


###4. URL签名工具:
* 无签名信息URL:
```python
s = SCSBucket('bucket的名称')
print s.make_url('待生成url地址的文件路径')
```
* 含签名信息URL:
```python
s = SCSBucket('bucket的名称')
print s.make_url_authed('待生成url地址的文件路径')
```

