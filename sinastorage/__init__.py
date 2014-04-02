from __future__ import absolute_import

__version__ = "1.1.0"

from .bucket import SCSFile, SCSBucket, SCSError, KeyNotFound
SCSFile, SCSBucket, SCSError, KeyNotFound
__all__ = "SCSFile", "SCSBucket", "SCSError"


class appinfo(object):
    def __init__(self,access_key,secret_key):
        self.access_key=access_key
        self.secret_key=secret_key

def getDefaultAppInfo():
    pass

def setDefaultAppInfo(access_key,secret_key):
    default = appinfo(access_key,secret_key)
    global getDefaultAppInfo 
    getDefaultAppInfo = lambda: default