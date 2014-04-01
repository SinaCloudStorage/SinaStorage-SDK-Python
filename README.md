#Sina storage SDK

##概述
新浪云存储 Python平台SDK为第三方应用提供了简单易用的API调用服务，使第三方客户端无需了解复杂的验证机制即可进行授权、上传、下载等文件操作。
>本文档详细内容请查阅：[SinaStorage’s documentation](http://sinastorage.sinaapp.com/developer/index.html)

##SDK 环境要求

要求**Python 2.5+** ，不支持Python 3。
完全由Python标准库开发。

##快速上手

###1.利用S3Bucket类对bucket进行访问：
```python
from sinastorage.bucket import S3Bucket

s = S3Bucket(bucket_name,
             access_key=access_key,
             secret_key=secret_key)
 
print s  
#<S3Bucket ... at 'https://s3.amazonaws.com/...'>
```
###2.bucket 操作:
*创建bucket
```python
s = S3Bucket('bucket_name',access_key=access_key,secret_key=secret_key)
s.put_bucket()
```
*删除bucket:
```python
s = S3Bucket('as1111dasdasdasd',access_key=access_key,secret_key=secret_key)
s.delete_bucket()
```
*列bucket目录:
```python
s = S3Bucket('as1111dasdasdasd',access_key=access_key,secret_key=secret_key)
s.delete_bucket()
```

###3.object 操作:
*上传文件/内容:
```python
#文件内容
s = S3Bucket('test11',access_key=access_key,secret_key=secret_key)
s.put('dage/dage1.txt',u'测试测试testtest')

#文件
s = S3Bucket('test11',access_key=access_key,secret_key=secret_key)
f = open("/Users/hanchao/Desktop/Android.NDK.Beginner's.Guide.pdf",'rb')
s.put("11111Android.NDK.Beginner's.Guide.pdf",f)
f.close()
```
*秒传文件:
```python
s = S3Bucket('test11',access_key=access_key,secret_key=secret_key)
s.put_relax('testpdf.pdf', '61bb70865c15729def3fb61ee0d7ed49ccafd509', 2433230)
```
*复制文件:
```python
s = S3Bucket('test11',access_key=access_key,secret_key=secret_key)
"""
    注意：
    source    必须从bucket开始，如：'/cloud0/aaa.txt'
"""
s.copy('/cloud0/aa.pdf', 'aaabbb.pdf')
```
*下载文件:
```python
s = S3Bucket('test11',access_key=access_key,secret_key=secret_key)
f = s['dage/dage1.txt']

#获取文件相关信息
print f.s3_info["mimetype"]
#'application/octet-stream'

print f.s3_info.keys()
#['mimetype', 'modify', 'headers', 'date', 'size', 'metadata']

#下载文件至本地
CHUNK = 16 * 1024
with open('dage1.txt', 'wb') as fp:
    while True:
        chunk = response.read(CHUNK)
        if not chunk: break
        fp.write(chunk)
```
*删除文件:
```python
s = S3Bucket('test11',access_key=access_key,secret_key=secret_key)
del s["my file!"]
```
*获取文件信息:
```python
s = S3Bucket('test11',access_key=access_key,secret_key=secret_key)
print s.info('testpdf.pdf')
#
```
*修改文件meta信息:
```python
s = S3Bucket('test11',access_key=access_key,secret_key=secret_key)
s.update_meta('testpdf.pdf', {'aaa':'bbbb','dage':'sbsb'})
```
*获取文件acl信息:
```python
s = S3Bucket('test11',access_key=access_key,secret_key=secret_key)
print s.acl_info('testpdf.pdf')
#
```
*修改文件acl信息:
```python
from sinastorage.bucket import S3Bucket,ACL
s = S3Bucket('test11',access_key=access_key,secret_key=secret_key)
acl = {}
acl[ACL.ACL_GROUP_ANONYMOUSE] = [ACL.ACL_READ]
acl[ACL.ACL_GROUP_CANONICAL] = [ACL.ACL_READ_ACP,ACL.ACL_WRITE_ACP]

s.update_acl('testpdf.pdf', acl)
```
###3.URL签名工具:
*无签名信息URL:
```python
s = S3Bucket('test11',access_key=access_key,secret_key=secret_key)
return s.make_url('testpdf.pdf')
```
*含签名信息URL:
```python
s = S3Bucket('test11',access_key=access_key,secret_key=secret_key)
return s.make_url_authed('testpdf.pdf')
```

For more detailed documentation, refer [here](http://sinastorage.sinaapp.com/developer/index.html)
