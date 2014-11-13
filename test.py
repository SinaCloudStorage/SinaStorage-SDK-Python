#-*- coding:UTF-8 -*-
'''
Created on 2014年10月15日

@author: hanchao
'''
import unittest
import datetime
import time

from sinastorage.bucket import SCSBucket, ACL

class Test(unittest.TestCase):

    bucket_name = 'py-test'
    object_key = 'py-test-object-key'
    local_file_name = 'py_test_file'
    
    def setUp(self):
        timestamp = time.time()
        self.bucket_name = '%s%s'%(self.bucket_name,timestamp)

    def tearDown(self):
        scs = SCSBucket(self.bucket_name)
        if scs.exist() :
            try:
                file_gen = scs.listdir()
                for item in file_gen:
                    if not item[1]:
                        scs.delete(item[0])
                scs.delete_bucket()
            except Exception as err:
                self.fail('empty bucket failed.Error is %s'%err)
        
    def test_create_bucket(self):
        scs = SCSBucket(self.bucket_name)
        try:
            scs.put_bucket()
        except:
            self.fail('create bucket:%s is failed'%self.bucket_name)
          
    def test_create_bucket_with_acl(self):
        scs = SCSBucket(self.bucket_name)
        try:
            scs.put_bucket('public-read-write')
        except:
            self.fail('create bucket:%s is failed'%self.bucket_name)
              
        metaResult = scs.meta()
        self.assertTrue(ACL.ACL_GROUP_ANONYMOUSE in metaResult['ACL'], 'The bucket:%s acl dose not contains GRPS000000ANONYMOUSE group'%self.bucket_name)
        self.assertTrue(ACL.ACL_READ in metaResult['ACL'][ACL.ACL_GROUP_ANONYMOUSE], 'The bucket:%s acl GRPS000000ANONYMOUSE group hasn\'t read right'%self.bucket_name)
        self.assertTrue(ACL.ACL_WRITE in metaResult['ACL'][ACL.ACL_GROUP_ANONYMOUSE], 'The bucket:%s acl GRPS000000ANONYMOUSE group hasn\'t write right'%self.bucket_name)
          
    def test_bucket_exist(self):
        scs = SCSBucket(self.bucket_name)
        scs.put_bucket()
        self.assertTrue(scs.exist(), 'not true')
          
    def test_list_bucket(self):
        scs = SCSBucket()
        bucket_gen = scs.list_buckets()
        self.assertTrue(bucket_gen is not None, 'List bucket result is None')
        for bucket in bucket_gen:
            bucketStr = str(bucket)
            self.assertTrue(bucket[0] is not None, 'bucket:%s name is None'%bucketStr)
            self.assertTrue(bucket[1] is not None, 'bucket:%s CreationDate is None'%bucketStr)
          
          
    def test_remove_bucket(self):
        scs = SCSBucket(self.bucket_name)
        scs.put_bucket()
          
        try:
            scs.delete_bucket()
        except:
            self.fail('Remove bucket:%s is failed'%self.bucket_name)
          
      
    def test_list_bucket_files(self):
        scs = SCSBucket(self.bucket_name)
        scs.put_bucket()
          
        content = u'this is a file content text!!'
        scs.put(self.object_key,content)
      
        file_gen = scs.listdir()
          
        self.assertTrue(file_gen is not None, 'List bucket files result is None')
        for item in file_gen:
            #(name, isPrefix, sha1, expiration_time, modify, owner, md5, content_type, size)
            self.assertTrue(item[0] is not None, 'file name is None')
            self.assertTrue(item[1] is not None, 'file isPrefix is None')
            self.assertTrue(item[2] is not None, 'file sha1 is None')
#             self.assertIsNotNone(item[3], 'file expiration_time is None')
            self.assertTrue(item[4] is not None, 'file modify is None')
            self.assertTrue(item[5] is not None, 'file owner is None')
            self.assertTrue(item[6] is not None, 'file md5 is None')
            self.assertTrue(item[7] is not None, 'file content_type is None')
            self.assertTrue(item[8] is not None, 'file size is None')
          
    def test_list_bucket_file_by_conditions(self):
        scs = SCSBucket(self.bucket_name)
        scs.put_bucket()
          
        content = u'this is a file content text!!'
        scs.put(self.object_key,content)
      
        file_gen = scs.listdir(prefix=self.object_key, limit=1)
          
        self.assertTrue(file_gen is not None, 'List bucket files result is None')
        self.assertTrue(file_gen.contents_quantity==1, 'The result length is not equal 1')
        for item in file_gen:
            #(name, isPrefix, sha1, expiration_time, modify, owner, md5, content_type, size)
            self.assertTrue(item[0] is not None, 'file name is None')
            self.assertTrue(item[1] is not None, 'file isPrefix is None')
            self.assertTrue(item[2] is not None, 'file sha1 is None')
#             self.assertIsNotNone(item[3], 'file expiration_time is None')
            self.assertTrue(item[4] is not None, 'file modify is None')
            self.assertTrue(item[5] is not None, 'file owner is None')
            self.assertTrue(item[6] is not None, 'file md5 is None')
            self.assertTrue(item[7] is not None, 'file content_type is None')
            self.assertTrue(item[8] is not None, 'file size is None')
          
      
    def test_get_bucket_meta(self):
        scs = SCSBucket(self.bucket_name)
        try:
            scs.put_bucket('public-read-write')
        except:
            self.fail('create bucket:%s is failed'%self.bucket_name)
              
        metaResult = scs.meta()
        self.assertTrue(ACL.ACL_GROUP_ANONYMOUSE in metaResult['ACL'], 'The bucket:%s acl dose not contains GRPS000000ANONYMOUSE group'%self.bucket_name)
        self.assertTrue(ACL.ACL_READ in metaResult['ACL'][ACL.ACL_GROUP_ANONYMOUSE], 'The bucket:%s acl GRPS000000ANONYMOUSE group hasn\'t read right'%self.bucket_name)
        self.assertTrue(ACL.ACL_WRITE in metaResult['ACL'][ACL.ACL_GROUP_ANONYMOUSE], 'The bucket:%s acl GRPS000000ANONYMOUSE group hasn\'t write right'%self.bucket_name)
          
        self.assertEqual(self.bucket_name, metaResult['Project'], 'The metaResult[\'Project\'] is not equal %s'%self.bucket_name)
        self.assertTrue(metaResult['Owner'] is not None, 'The metaResult[\'Owner\'] is None')
        self.assertTrue(metaResult['Last-Modified'] is not None, 'The metaResult[\'Last-Modified\'] is None')
  
  
    def test_put_content(self):
        scs = SCSBucket(self.bucket_name)
        try:
            scs.put_bucket('public-read-write')
        except:
            self.fail('create bucket:%s is failed'%self.bucket_name)
        content = u'this is a file content text!!'
        scs.put(self.object_key, content)
  
        scsResponse = scs.get(self.object_key)
        CHUNK = 16 * 1024
        file_content = ''
        from sinastorage.vendored import six
        while True:
            chunk = scsResponse.read(CHUNK)
            if not chunk: break
            if isinstance(chunk, six.text_type):
                file_content += chunk
            else:
                file_content += chunk.decode("utf-8")
        self.assertEqual(content, file_content, 'The uploaded file content is not match local.%s'%file_content)
  
    def test_put_content_with_conditions(self):
        scs = SCSBucket(self.bucket_name)
        try:
            scs.put_bucket('public-read-write')
        except:
            self.fail('create bucket:%s is failed'%self.bucket_name)
              
        content = u'this is a file content text!!'      #文件内容
        canned_acl = 'public-read-write'                #快捷ACL
        metadata = {}                                   #自定义文件属性信息
        metadata['author'] = 'dage'
        metadata['home'] = 'tianjin'
        metadata['age'] = '18'
        mimetype = 'text/plain'
        scs.put(self.object_key, content, acl=canned_acl, metadata=metadata, mimetype=mimetype)
  
        scsResponse = scs.get(self.object_key)
        CHUNK = 16 * 1024
        file_content = ''
        from sinastorage.vendored import six
        while True:
            chunk = scsResponse.read(CHUNK)
            if not chunk: break
            if isinstance(chunk, six.text_type):
                file_content += chunk
            else:
                file_content += chunk.decode("utf-8")
        #assert file_content
        self.assertEqual(content, file_content, 'The uploaded file content is not metch local.%s'%file_content)
        #assert metadata
        self.assertEqual(metadata['author'], scsResponse.responseHeaders['x-amz-meta-author'], 'The response metadata[\'author\'] is not match')
        self.assertEqual(metadata['home'], scsResponse.responseHeaders['x-amz-meta-home'], 'The response metadata[\'home\'] is not match')
        self.assertEqual(metadata['age'], scsResponse.responseHeaders['x-amz-meta-age'], 'The response metadata[\'age\'] is not match')
        #assert content-type
        self.assertEqual(mimetype, scsResponse.responseHeaders['content-type'], 'The response content-type is not match')
        #assert acl
        aclResult = scs.acl_info(self.object_key)
        self.assertTrue(ACL.ACL_GROUP_ANONYMOUSE in aclResult['ACL'], 'The acl dose not contains GRPS000000ANONYMOUSE group')
        self.assertTrue(ACL.ACL_READ in aclResult['ACL'][ACL.ACL_GROUP_ANONYMOUSE], 'The acl GRPS000000ANONYMOUSE group hasn\'t read right')
        self.assertTrue(ACL.ACL_WRITE in aclResult['ACL'][ACL.ACL_GROUP_ANONYMOUSE], 'The acl GRPS000000ANONYMOUSE group hasn\'t write right')
          
          
    def test_put_file(self):
        scs = SCSBucket(self.bucket_name)
        try:
            scs.put_bucket('public-read-write')
        except:
            self.fail('create bucket:%s is failed'%self.bucket_name)
              
        canned_acl = 'public-read-write'                #快捷ACL
        metadata = {}                                   #自定义文件属性信息
        metadata['author'] = 'dage'
        metadata['home'] = 'tianjin'
        metadata['age'] = '18'
        mimetype = 'text/plain'
          
        scs.putFile(key=self.object_key, filePath=self.local_file_name, acl=canned_acl
                    , metadata=metadata, mimetype=mimetype)
  
        scsResponse = scs.get(self.object_key)
        CHUNK = 16 * 1024
        file_content = ''
        from sinastorage.vendored import six
        while True:
            chunk = scsResponse.read(CHUNK)
            if not chunk: break
            if isinstance(chunk, six.text_type):
                file_content += chunk
            else:
                file_content += chunk.decode("utf-8")
        #assert file_content
#         self.assertEqual(content, file_content, 'The uploaded file content is not metch local.%s'%file_content)
        #assert metadata
        self.assertEqual(metadata['author'], scsResponse.responseHeaders['x-amz-meta-author'], 'The response metadata[\'author\'] is not match')
        self.assertEqual(metadata['home'], scsResponse.responseHeaders['x-amz-meta-home'], 'The response metadata[\'home\'] is not match')
        self.assertEqual(metadata['age'], scsResponse.responseHeaders['x-amz-meta-age'], 'The response metadata[\'age\'] is not match')
        #assert content-type
        self.assertEqual(mimetype, scsResponse.responseHeaders['content-type'], 'The response content-type is not match')
        #assert acl
        aclResult = scs.acl_info(self.object_key)
        self.assertTrue(ACL.ACL_GROUP_ANONYMOUSE in aclResult['ACL'], 'The acl dose not contains GRPS000000ANONYMOUSE group')
        self.assertTrue(ACL.ACL_READ in aclResult['ACL'][ACL.ACL_GROUP_ANONYMOUSE], 'The acl GRPS000000ANONYMOUSE group hasn\'t read right')
        self.assertTrue(ACL.ACL_WRITE in aclResult['ACL'][ACL.ACL_GROUP_ANONYMOUSE], 'The acl GRPS000000ANONYMOUSE group hasn\'t write right')
          
         
    def test_put_file_relax(self):
        scs = SCSBucket(self.bucket_name)
        try:
            scs.put_bucket('public-read-write')
        except:
            self.fail('create bucket:%s is failed'%self.bucket_name)
             
        scs.put(self.object_key, 'fileContent...fileContent...fileContent...fileContent...fileContent...')
         
        orign_file_metaResult = scs.meta(self.object_key)
         
        canned_acl = 'public-read-write'                #快捷ACL
        metadata = {}                                   #自定义文件属性信息
        metadata['author'] = 'dage'
        metadata['home'] = 'tianjin'
        metadata['age'] = '18'
        mimetype = 'text/plain'
        scs.put_relax(key=self.object_key+'_relax', sina_sha1=orign_file_metaResult['Content-SHA1'], 
                      s_sina_length=orign_file_metaResult['Size'], acl=canned_acl, 
                      metadata=metadata, mimetype=mimetype)
         
        relax_file_aclInfo = scs.acl_info(self.object_key+'_relax')
        self.assertTrue(ACL.ACL_GROUP_ANONYMOUSE in relax_file_aclInfo['ACL'], 'The acl dose not contains GRPS000000ANONYMOUSE group')
        self.assertTrue(ACL.ACL_READ in relax_file_aclInfo['ACL'][ACL.ACL_GROUP_ANONYMOUSE], 'The acl GRPS000000ANONYMOUSE group hasn\'t read right')
        self.assertTrue(ACL.ACL_WRITE in relax_file_aclInfo['ACL'][ACL.ACL_GROUP_ANONYMOUSE], 'The acl GRPS000000ANONYMOUSE group hasn\'t write right')
         
        relax_file_info = scs.info(self.object_key+'_relax')
        #assert metadata
        self.assertEqual(metadata['author'], relax_file_info['metadata']['author'], 'The response metadata[\'author\'] is not match')
        self.assertEqual(metadata['home'], relax_file_info['metadata']['home'], 'The response metadata[\'home\'] is not match')
        self.assertEqual(metadata['age'], relax_file_info['metadata']['age'], 'The response metadata[\'age\'] is not match')
        #assert content-type
        self.assertEqual(mimetype, relax_file_info['headers']['content-type'], 'The response content-type is not match')
         
         
    def test_get_file(self):
        scs = SCSBucket(self.bucket_name)
        try:
            scs.put_bucket('public-read-write')
        except:
            self.fail('create bucket:%s is failed'%self.bucket_name)
              
        scs.putFile(self.object_key, self.local_file_name)
          
        scsResponse = scs.get(self.object_key)
        CHUNK = 16 * 1024
        with open(self.local_file_name+'.downloaded', 'wb') as fp:
            while True:
                chunk = scsResponse.read(CHUNK)
                if not chunk: break
                fp.write(bytes(chunk) )
          
        import os
        self.assertTrue(os.path.exists(self.local_file_name+'.downloaded'), 'The download file dose not exists')
        self.assertEqual(str(os.stat(self.local_file_name).st_size), 
                         scsResponse.responseHeaders['content-length'], 'The download file size dose not match local file')
  
      
    def test_copy_file(self):
        scs = SCSBucket(self.bucket_name)
        try:
            scs.put_bucket('public-read-write')
        except:
            self.fail('create bucket:%s is failed'%self.bucket_name)
              
        scs.putFile(self.object_key, self.local_file_name)
          
        canned_acl = 'public-read'                #快捷ACL
        metadata = {}                             #自定义文件属性信息
        metadata['author'] = 'copied'
        metadata['home'] = 'beijing'
        metadata['age'] = '189'
        mimetype = 'text/plain'
        scs.copy(source='/'+self.bucket_name+'/'+self.object_key, 
                 key=self.object_key+'_copied', acl=canned_acl, 
                 metadata=metadata, mimetype=mimetype)
          
        copied_file_aclInfo = scs.acl_info(self.object_key+'_copied')
        self.assertTrue(ACL.ACL_GROUP_ANONYMOUSE in copied_file_aclInfo['ACL'], 'The acl dose not contains GRPS000000ANONYMOUSE group')
        self.assertTrue(ACL.ACL_READ in copied_file_aclInfo['ACL'][ACL.ACL_GROUP_ANONYMOUSE], 'The acl GRPS000000ANONYMOUSE group hasn\'t read right')
          
        copied_file_info = scs.info(self.object_key+'_copied')
        #assert metadata
        self.assertEqual(metadata['author'], copied_file_info['metadata']['author'], 'The response metadata[\'author\'] is not match')
        self.assertEqual(metadata['home'], copied_file_info['metadata']['home'], 'The response metadata[\'home\'] is not match')
        self.assertEqual(metadata['age'], copied_file_info['metadata']['age'], 'The response metadata[\'age\'] is not match')
        #assert content-type
        self.assertEqual(mimetype, copied_file_info['headers']['content-type'], 'The response content-type is not match')
          
      
    def test_get_file_meta(self):
        scs = SCSBucket(self.bucket_name)
        try:
            scs.put_bucket('public-read-write')
        except:
            self.fail('create bucket:%s is failed'%self.bucket_name)
          
        metadata = {}                                   #自定义文件属性信息
        metadata['author'] = 'dage'
        metadata['home'] = 'tianjin'
        metadata['age'] = '18'
        mimetype = 'text/plain'
          
        scs.putFile(key=self.object_key, filePath=self.local_file_name,
                    metadata=metadata, mimetype=mimetype)
              
        metaResult = scs.meta(self.object_key)
          
        self.assertEqual(self.object_key, metaResult['File-Name'], 'The meta[\'File-Name\'] is not equals '+self.object_key)
        self.assertEqual(mimetype, metaResult['Type'], 'The meta[\'Type\'] is not equals '+mimetype)
        self.assertTrue(metaResult['Content-SHA1'] is not None, 'The meta[\'Content-SHA1\'] is None')
        self.assertTrue(metaResult['Content-MD5'] is not None, 'The meta[\'Content-MD5\'] is None')
        self.assertTrue(metaResult['Owner'] is not None, 'The meta[\'Owner\'] is None')
          
        self.assertTrue('x-amz-meta-author' in metaResult['File-Meta'], 'File-Meta dose not contains x-amz-meta-author key')
        self.assertEqual(metadata['author'], metaResult['File-Meta']['x-amz-meta-author'], 'The metaResult[\'File-Meta\'][\'x-amz-meta-author\'] value is not match')
        self.assertTrue('x-amz-meta-home' in metaResult['File-Meta'], 'File-Meta dose not contains x-amz-meta-home key')
        self.assertEqual(metadata['home'], metaResult['File-Meta']['x-amz-meta-home'], 'The metaResult[\'File-Meta\'][\'x-amz-meta-home\'] value is not match')
        self.assertTrue('x-amz-meta-age' in metaResult['File-Meta'], 'File-Meta dose not contains x-amz-meta-age key')
        self.assertEqual(metadata['age'], metaResult['File-Meta']['x-amz-meta-age'], 'The metaResult[\'File-Meta\'][\'x-amz-meta-age\'] value is not match')
          
          
    def test_delete_file(self):
        scs = SCSBucket(self.bucket_name)
        try:
            scs.put_bucket('public-read-write')
        except:
            self.fail('create bucket:%s is failed'%self.bucket_name)
              
        content = u'this is a file content text!!'
        scs.put(self.object_key, content)
          
        try:
            scs.delete(self.object_key)
        except:
            self.fail('Delete file is failed')
      
      
    def test_info_file(self):
        scs = SCSBucket(self.bucket_name)
        try:
            scs.put_bucket('public-read-write')
        except:
            self.fail('create bucket:%s is failed'%self.bucket_name)
              
        content = u'this is a file content text!!'      #文件内容
        canned_acl = 'public-read-write'                #快捷ACL
        metadata = {}                                   #自定义文件属性信息
        metadata['author'] = 'dage'
        metadata['home'] = 'tianjin'
        metadata['age'] = '18'
        mimetype = 'text/plain'
        scs.put(self.object_key, content, acl=canned_acl, metadata=metadata, mimetype=mimetype)
      
        file_info = scs.info(self.object_key)
        #assert metadata
        self.assertEqual(metadata['author'], file_info['metadata']['author'], 'The response metadata[\'author\'] is not match')
        self.assertEqual(metadata['home'], file_info['metadata']['home'], 'The response metadata[\'home\'] is not match')
        self.assertEqual(metadata['age'], file_info['metadata']['age'], 'The response metadata[\'age\'] is not match')
        #assert content-type
        self.assertEqual(mimetype, file_info['headers']['content-type'], 'The response content-type is not match')
      
      
    def test_update_file_meta(self):
        scs = SCSBucket(self.bucket_name)
        try:
            scs.put_bucket('public-read-write')
        except:
            self.fail('create bucket:%s is failed'%self.bucket_name)
        content = u'this is a file content text!!'
        scs.put(self.object_key, content)
          
        canned_acl = 'public-read-write'                #快捷ACL
        metadata = {}                                   #自定义文件属性信息
        metadata['author'] = 'dage'
        metadata['home'] = 'tianjin'
        metadata['age'] = '18'
        mimetype = 'text/plain'
        scs.update_meta(self.object_key, metadata=metadata, acl=canned_acl, mimetype=mimetype)
      
        file_info = scs.info(self.object_key)
        #assert metadata
        self.assertEqual(metadata['author'], file_info['metadata']['author'], 'The response metadata[\'author\'] is not match')
        self.assertEqual(metadata['home'], file_info['metadata']['home'], 'The response metadata[\'home\'] is not match')
        self.assertEqual(metadata['age'], file_info['metadata']['age'], 'The response metadata[\'age\'] is not match')
        #assert content-type
#         print file_info['headers']
#TODO:服务器问题         self.assertEqual(mimetype, file_info['headers']['content-type'], 'The response content-type is not match')
        #acl
        file_aclInfo = scs.acl_info(self.object_key)
        self.assertTrue(ACL.ACL_GROUP_ANONYMOUSE in file_aclInfo['ACL'], 'The acl dose not contains GRPS000000ANONYMOUSE group')
        self.assertTrue(ACL.ACL_READ in file_aclInfo['ACL'][ACL.ACL_GROUP_ANONYMOUSE], 'The acl GRPS000000ANONYMOUSE group hasn\'t read right')
        self.assertTrue(ACL.ACL_WRITE in file_aclInfo['ACL'][ACL.ACL_GROUP_ANONYMOUSE], 'The acl GRPS000000ANONYMOUSE group hasn\'t write right')
      
      
    def test_file_acl_info(self):
        scs = SCSBucket(self.bucket_name)
        try:
            scs.put_bucket('public-read-write')
        except:
            self.fail('create bucket:%s is failed'%self.bucket_name)
        content = u'this is a file content text!!'
        canned_acl = 'public-read-write'                #快捷ACL
        scs.put(key=self.object_key, data=content, acl=canned_acl)
          
        #acl
        file_aclInfo = scs.acl_info(self.object_key)
        self.assertTrue(ACL.ACL_GROUP_ANONYMOUSE in file_aclInfo['ACL'], 'The acl dose not contains GRPS000000ANONYMOUSE group')
        self.assertTrue(ACL.ACL_READ in file_aclInfo['ACL'][ACL.ACL_GROUP_ANONYMOUSE], 'The acl GRPS000000ANONYMOUSE group hasn\'t read right')
        self.assertTrue(ACL.ACL_WRITE in file_aclInfo['ACL'][ACL.ACL_GROUP_ANONYMOUSE], 'The acl GRPS000000ANONYMOUSE group hasn\'t write right')
  
  
    def test_update_file_acl(self):
        scs = SCSBucket(self.bucket_name)
        try:
            scs.put_bucket('public-read-write')
        except:
            self.fail('create bucket:%s is failed'%self.bucket_name)
        content = u'this is a file content text!!'
        canned_acl = 'private'                #快捷ACL
        scs.put(key=self.object_key, data=content, acl=canned_acl)
          
        #设置ACL
        acl = {}
        acl[ACL.ACL_GROUP_ANONYMOUSE] = [ACL.ACL_READ, ACL.ACL_WRITE, ACL.ACL_READ_ACP]
        acl[ACL.ACL_GROUP_CANONICAL] = [ACL.ACL_READ_ACP,ACL.ACL_WRITE_ACP, ACL.ACL_READ]
        user_id = 'SINA0000001001AABBCC'
        acl[user_id] = [ACL.ACL_WRITE, ACL.ACL_READ]
        scs.update_acl(self.object_key, acl)
        #assert
        file_aclInfo = scs.acl_info(self.object_key)
        #ACL_GROUP_ANONYMOUSE
        self.assertTrue(ACL.ACL_GROUP_ANONYMOUSE in file_aclInfo['ACL'], 'The acl dose not contains GRPS000000ANONYMOUSE group')
        self.assertTrue(ACL.ACL_READ in file_aclInfo['ACL'][ACL.ACL_GROUP_ANONYMOUSE], 'The acl GRPS000000ANONYMOUSE group hasn\'t read right')
        self.assertTrue(ACL.ACL_WRITE in file_aclInfo['ACL'][ACL.ACL_GROUP_ANONYMOUSE], 'The acl GRPS000000ANONYMOUSE group hasn\'t write right')
        self.assertTrue(ACL.ACL_READ_ACP in file_aclInfo['ACL'][ACL.ACL_GROUP_ANONYMOUSE], 'The acl GRPS000000ANONYMOUSE group hasn\'t read_acp right')
        #ACL_GROUP_CANONICAL
        self.assertTrue(ACL.ACL_GROUP_CANONICAL in file_aclInfo['ACL'], 'The acl dose not contains GRPS0000000CANONICAL group')
        self.assertTrue(ACL.ACL_READ in file_aclInfo['ACL'][ACL.ACL_GROUP_CANONICAL], 'The acl GRPS0000000CANONICAL group hasn\'t read right')
        self.assertTrue(ACL.ACL_WRITE_ACP in file_aclInfo['ACL'][ACL.ACL_GROUP_CANONICAL], 'The acl GRPS0000000CANONICAL group hasn\'t write_acp right')
        self.assertTrue(ACL.ACL_READ_ACP in file_aclInfo['ACL'][ACL.ACL_GROUP_CANONICAL], 'The acl GRPS0000000CANONICAL group hasn\'t read_acp right')
        #user_id
        self.assertTrue(user_id in file_aclInfo['ACL'], 'The acl dose not contains user_id group')
        self.assertTrue(ACL.ACL_READ in file_aclInfo['ACL'][user_id], 'The acl user_id group hasn\'t read right')
        self.assertTrue(ACL.ACL_WRITE in file_aclInfo['ACL'][user_id], 'The acl user_id group hasn\'t write right')
          
  
    def test_make_url(self):
        scs = SCSBucket(self.bucket_name)
        try:
            scs.put_bucket('public-read-write')
        except:
            self.fail('create bucket:%s is failed'%self.bucket_name)
        content = u'this is a file content text!!'
        canned_acl = 'public-read'                #快捷ACL
        scs.put(key=self.object_key, data=content, acl=canned_acl)
          
        url = scs.make_url(self.object_key)
        #下载文件
#         import urllib2
#         response = urllib2.urlopen(url)
        from sinastorage.compat import urllib
        response = urllib.request.urlopen(url)
        self.assertEqual(len(content), int(response.info()['Content-Length']), 'The response header Content-Length is not match')
         
 
    def test_make_url_authed(self):
        scs = SCSBucket(self.bucket_name)
        try:
            scs.put_bucket('private')
        except:
            self.fail('create bucket:%s is failed'%self.bucket_name)
        content = u'this is a file content text!!'
        canned_acl = 'private'                #快捷ACL
        scs.put(key=self.object_key, data=content, acl=canned_acl)
         
        url = scs.make_url_authed(key=self.object_key,expire=datetime.timedelta(minutes=5))
        #下载文件
#         import urllib2
#         response = urllib2.urlopen(url)
        from sinastorage.compat import urllib
        response = urllib.request.urlopen(url)
        self.assertEqual(len(content), int(response.info()['Content-Length']), 'The response header Content-Length is not match')
         
#     def test_multipart_upload(self):
#         pass
#     def test_list_all_part(self):
#         pass

if __name__ == "__main__":
    unittest.main()

