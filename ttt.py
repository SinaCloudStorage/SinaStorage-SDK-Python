import sinastorage
from sinastorage.bucket import SCSBucket
from sinastorage.utils import FileWithCallback

import socket  
timeout = 20    
socket.setdefaulttimeout(timeout)

sinastorage.setDefaultAppInfo('1001nht3m7', '9fc22bb7ef60f6e9290b1e424daf744f40e7574f')

def uploadCallBack(total, uploaded, *args):
    print 'total:%s   received:%s'%(total,uploaded)

if __name__ == '__main__':
    scs = SCSBucket()
    buckets = scs.list_buckets()
    for bucket in buckets:
        try:
            if bucket[0].startswith('py-test'):
                s = SCSBucket(bucket[0])
                file_gen = s.listdir()
                for item in file_gen:
                    if not item[1]:
                        s.delete(item[0])
                s.delete_bucket()
        except Exception as err:
            print err
            pass