#Sina storage SDK

##概述
新浪云存储 Python平台SDK为第三方应用提供了简单易用的API调用服务，使第三方客户端无需了解复杂的验证机制即可进行授权、上传、下载等文件操作。
>本文档详细内容请查阅：[SinaStorage’s documentation][1]

##SDK 环境要求

要求**Python 2.5+** ，不支持Python 3。
完全由Python标准库开发。

##快速上手

###1.利用S3Bucket类对bucket进行访问。需要的参数有：
```python
from sinastorage.bucket import S3Bucket

s = S3Bucket(bucket_name,
             access_key=access_key,
             secret_key=secret_key)
 
print s  
#<S3Bucket ... at 'https://s3.amazonaws.com/...'>
```
###2.bucket 操作:
创建bucket
```python
s = S3Bucket('bucket_name',access_key=access_key,secret_key=secret_key)
s.put_bucket()
```
删除bucket:
```python
s = S3Bucket('as1111dasdasdasd',access_key=access_key,secret_key=secret_key)
s.delete_bucket()
```
列bucket目录:
```python
s = S3Bucket('as1111dasdasdasd',access_key=access_key,secret_key=secret_key)
s.delete_bucket()
```

###3.object 操作:









上传文件：
```python
s.put("my file", "my content")
```
下载文件：
```python
f = s.get("my file")
print f.read()
#my content
```
To retrieve information about a file, do
```python
print f.s3_info["mimetype"]
#'application/octet-stream'

print f.s3_info.keys()
#['mimetype', 'modify', 'headers', 'date', 'size', 'metadata']
```
To delete a file, do
```python
del s["my file!"]
```

For more detailed documentation, refer [here](http://sendapatch.se/projects/simples3)

##Contributing

###IRC
``#sendapatch`` on ``chat.freenode.net``.


[1]:http://sinastorage.sinaapp.com/developer/index.html