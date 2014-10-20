#-*- coding:UTF-8 -*-
#!/usr/bin/env python

from setuptools import setup, find_packages

PACKAGE = "sinastorage"
NAME = "scs-sdk"
DESCRIPTION = u"Python SDK For 新浪云存储"
AUTHOR = "sina cloud storage"
AUTHOR_EMAIL = "hanchao3@staff.sina.com.cn"
URL = "http://open.sinastorage.com/"
VERSION = '1.1.0'       #__import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="BSD",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    url=URL,
    download_url = 'https://github.com/SinaCloudStorage/SinaStorage-SDK-Python',
    keywords = ['sina', 'scs', 'sinacloudstorage'],
    packages=find_packages(exclude=["sample*", "sample"]),
    install_requires=['filechunkio'],
    
)