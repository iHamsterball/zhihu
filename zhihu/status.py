# -*- coding: utf-8 -*-
# Build-in / Std
import os, sys, time, platform, random, string, pickle
import re, json, cookielib, ctypes, _ctypes

# requirements
import requests, termcolor, html2text
try:
    from bs4 import BeautifulSoup
except:
    import BeautifulSoup
# module
from auth import islogin
from auth import Logging

"""
    Note:
        1. 身份验证由 `auth.py` 完成。
        2. 身份信息保存在当前目录的 `cookies` 文件中。
        3. `requests` 对象可以直接使用，身份信息已经自动加载。

    By Luozijun (https://github.com/LuoZijun), 09/09 2015

"""

requests = requests.Session()
requests.cookies = cookielib.LWPCookieJar('cookies')

try:
    requests.cookies.load(ignore_discard=True)
except:
    Logging.error(u"你还没有登录知乎哦 ...")
    Logging.info(u"执行 `python auth.py` 即可以完成登录。")
    raise Exception("无权限(403)")

if islogin() != True:
    Logging.error(u"你的身份信息已经失效，请重新生成身份信息( `python auth.py` )。")
    raise Exception("无权限(403)")

reload(sys)
sys.setdefaultencoding('utf8')

class Status:
    so = None
    delay = None

    def __init__(self):
        self.so = ctypes.CDLL("./zhihu/clib/ping.so")

    def __reload__(self):
	_ctypes.dlclose(self.so._handle)
	_ctypes.dlclose(self.so._handle)
	self.so = ctypes.CDLL("./zhihu/clib/ping.so")
	print "reload"

    def ping(self):
	self.__reload__()
        ret = self.so.ping("www.zhihu.com")
	if ret != -1:
	    self.delay = ret / 1000.0
	else:
	    return self.ping()
        return self.delay
