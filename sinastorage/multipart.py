#-*- coding:UTF-8 -*-
'''
Created on 2014年4月29日

@author: hanchao
'''
def part_lister(mpupload, part_number_marker=None):
    """
    A generator function for listing parts of a multipart upload.
    """
    more_results = True
    part = None
    while more_results:
        parts = mpupload.get_all_parts(None, part_number_marker)
        for part in parts:
            yield part
        part_number_marker = mpupload.next_part_number_marker
        more_results = mpupload.is_truncated

class Part(object):
    ''' 分片对象 '''
    def __init__(self, part_num, etag=None):
        self.part_num = part_num
        self.etag = etag

class MultipartUpload(object):
    '''
    分片上传
    '''
    def __init__(self, bucket=None):
        self.scsBucket = bucket
        self.bucket_name = None
        self.key_name = None
        self.upload_id = None
        self.parts = []
        
        self.parts_amount = 0
        self.bytes_per_part = None
        
        self.current_part_num_offset = 0
        
    def get_next_part(self):
        ''' 获取下一片分片 '''
        part = None
        while self.current_part_num_offset < self.parts_amount:
            part = Part(self.current_part_num_offset)
#             self.parts.append(part)
            yield part
            self.current_part_num_offset += 1
                


        
        