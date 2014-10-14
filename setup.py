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

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="BSD",
    url=URL,
    download_url = 'https://github.com/SinaCloudStorage/SinaStorage-SDK-Python',
    keywords = ['sina', 'scs', 'sinacloudstorage'],
    packages=['sinastorage'],#find_packages(exclude=["sample.*", "sample"]),
    install_requires=['filechunkio >= 1.5']
#     package_data=find_package_data(
#             PACKAGE,
#             only_in_packages=False
#       ),
#     classifiers=[
#         "Development Status :: 3 - Alpha",
#         "Environment :: Web Environment",
#         "Intended Audience :: Developers",
#         "License :: OSI Approved :: BSD License",
#         "Operating System :: OS Independent",
#         "Programming Language :: Python",
#         "Framework :: Django",
#     ],
#     zip_safe=False,
)