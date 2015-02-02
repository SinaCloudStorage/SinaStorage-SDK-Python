#-*- coding:UTF-8 -*-
#!/usr/bin/env python

'''
Created on 2014年3月24日

@author: hanchao
'''
import sys
import os
sys.path.insert(0, (os.path.join(os.path.dirname(__file__),"..")))

import sinastorage
from sinastorage.bucket import SCSBucket,ACL, SCSError, KeyNotFound, BadRequest

sinastorage.setDefaultAppInfo('accessKey', 'secretKey')

uploadedAmount = 0.0
def putFileCallback(total, uploadAmount):
    global uploadedAmount
    uploadedAmount += uploadAmount*1.0
    print '=====', 'complete percent : %d%%'%(uploadedAmount/total*100)

def put_content():
    content = u'this is a file content text!!'
    s = SCSBucket('create-a-bucket11')
    print s.put('sss.txt',content)

def put_file():
    s = SCSBucket('create-a-bucket11')
#     print s.put('sss.txt',u'测试测试testtest')
    print s.putFile('111111qt-opensource-mac-4.8.6.dmg', 
                    '/Users/hanchao/Desktop/qt-opensource-mac-4.8.6.dmg', 
                    putFileCallback)

def put_file_relax():
    s = SCSBucket('test11')
    s.put_relax('testpdf.pdf', '61bb70865c15729def3fb61ee0d7ed49ccafd509', 2433230)

def list_bucket_files():
    s = SCSBucket('test11')
    files_generator = s.listdir()#delimiter='/')
    print '-----list_bucket_files---------'
    print '-----detail---------'
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
    print '-----file list---------'
#     for item in files_generator:
#         print item

def list_bucket():
    s = SCSBucket()
    buckets_generator = s.list_buckets()
    for bucket in buckets_generator:
        print bucket
        
def get_bucket_meta():
    s = SCSBucket('test11')
    metaDict = s.meta()
    print metaDict

def get_file():
    s = SCSBucket('asdasdasdasd')
    response = s['a/asdf/新建 文本文档.txt']
    CHUNK = 16 * 1024
    with open('111', 'wb') as fp:
        while True:
            chunk = response.read(CHUNK)
            if not chunk: break
            fp.write(chunk)
    
    
def copy_file():
    s = SCSBucket('asdasdasdasd')
    """
        注意：
        source    必须从bucket开始，如：'/cloud0/aaa.txt'
    """
    s.copy('/asdasdasdasd/aaaa.txt', 'aaaa22111.txt')

def get_file_meta():
    s = SCSBucket('test11')
    metaDict = s.meta('InstoreApp.ipa')
    print metaDict

def delete_file():
    s = SCSBucket('test11')
    s.delete('testpdf.pdf')
    
def info_file():
    s = SCSBucket('test11')
    info = s.info('sss.txt')
    print info['mimetype']
    print info['size']
    print info

def update_file_meta():
    s = SCSBucket('test11')
    s.update_meta('sss.txt', {'aaa':'bbbb','dage':'sbsb'})
    
def make_url():
    s = SCSBucket('test11')
    return s.make_url('testpdf.pdf')

def make_url_authed():
    s = SCSBucket('test11')
    return s.make_url_authed('testpdf.pdf')

def file_acl_info():
    s = SCSBucket('test11')
    acl = s.acl_info('sss.txt')
    print acl

def update_file_acl():
    s = SCSBucket('test11')
    acl = {}
    acl[ACL.ACL_GROUP_ANONYMOUSE] = [ACL.ACL_READ]
    acl[ACL.ACL_GROUP_CANONICAL] = [ACL.ACL_READ_ACP,ACL.ACL_WRITE_ACP]
    
    s.update_acl('sss.txt', acl)
    
def create_bucket():
    s = SCSBucket('222dasdasdasd')
    s.put_bucket()
    
def remove_bucket():
    s = SCSBucket('222dasdasdasd')
    s.delete_bucket()

''' 分片上传 '''
def customCallback(upload_id, part_num, total, received):
    '''
    分片上传进度回调函数
    '''
    print '==customCallback=====upload_id=====',upload_id,'=======part_num=====',part_num,'-------total----------',total,'====received======',received
    
def customNumCallback(upload_id, partAmount, part):
    '''
    分片上传完毕回调函数
    '''
    print '==customNumCallback=====upload_id=====',upload_id,'-------partAmount----------',partAmount,'-------part----------',part.part_num
    
def part_failed_cb(upload_id, part):
    '''
    分片上传失败回调函数
    '''
    print '==failed upload part #%d in upload_id %s'%(part.part_num, upload_id)
    
def multipartUpload():
    s = SCSBucket('vvzz')
#     initMultipartUploadResult = s.initiateMultipartUpload('test-python.zip');
#     print initMultipartUploadResult
    s.multipart_upload('ttt.zip', '/Users/hanchao/Desktop/ttt.zip',cb=customCallback,num_cb=customNumCallback, part_failed_cb=part_failed_cb)
    
def listAllPart():
    s = SCSBucket('create-a-bucket11')
    print s.list_parts('53606bec73684fa0be9c52de21f35d31', 'Numbers51.dmg')
    
    
if __name__ == '__main__':
    try:
#         create_bucket()
#         list_bucket()
#         remove_bucket()
#         list_bucket_files()
#         get_bucket_meta()
#         put_content()
#         put_file()
#         put_file_relax()
#         get_file()
#         copy_file()
#         get_file_meta()
#         delete_file()
#         info_file()
#         update_file_meta()
#         file_acl_info()
#         update_file_acl()
#         print make_url()
#         print make_url_authed()

        multipartUpload()
#         listAllPart()

    except KeyNotFound ,e:
        #请求的key不存在
        print '[request url is] :\n%s'%e.url
        print '[response headers is] :\n%s'%e.hdrs
        print '[error code is] :\n%s'%e.extra['code']
        
        print '[response body is] :\n%s'%e.data
    except BadRequest ,e:
        #请求错误
        print '[request url is] :\n%s'%e.url
        print '[response headers is] :\n%s'%e.hdrs
        print '[error code is] :\n%s'%e.extra['code']
        print '[response body is] :\n%s'%e.data
    except SCSError, e:
        print '[request url is] :\n%s'%e.url
        print '[response headers is] :\n%s'%e.hdrs
        print '[error code is] :\n%s'%e.extra['code']
        print '[response body is] :\n%s'%e.data


