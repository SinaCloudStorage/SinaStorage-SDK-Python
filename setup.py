#-*- coding:UTF-8 -*-
#!/usr/bin/env python

from setuptools import setup, find_packages

PACKAGE = "sinastorage"
NAME = "scs-sdk"
DESCRIPTION = u"Python SDK For 新浪云存储"
AUTHOR = "sina cloud storage"
AUTHOR_EMAIL = "hanchao3@staff.sina.com.cn"
URL = "http://open.sinastorage.com/"
VERSION = __import__(PACKAGE).__version__

def readme():
    try:
        with open("README.md") as f:
            return f.read()
    except:
        return ''

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=readme(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="MIT",
    platforms = "Posix; MacOS X; Windows",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Internet',
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4"
    ],
    url=URL,
    download_url = 'https://github.com/SinaCloudStorage/SinaStorage-SDK-Python',
    keywords = ['sina', 'scs', 'sinacloudstorage'],
    packages=find_packages(exclude=["sample*", "sample"]),
#     install_requires=['filechunkio'],
    
)