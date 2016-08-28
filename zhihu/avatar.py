# -*- coding: utf-8 -*-
# Build-in / Std
import os, sys, time, platform, random, string, StringIO, pickle
import re, json, cookielib

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

class Avatar:
    userid = None
    url = None
    src = None
    file = None
    ret = None

    def __init__(self, userid):
        self.userid = userid
        self.url = "https://www.zhihu.com/people/" + userid

    def fetch_img_url(self):
        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
            'Host': "www.zhihu.com",
            'Origin': "https://www.zhihu.com",
            'Pragma': "no-cache",
            'Referer': "https://www.zhihu.com/people/hamster-53"
        }
        r = requests.get(self.url, headers=headers, verify=False)
        soup = BeautifulSoup(r.content, "lxml")
        img = soup.find("img", class_="Avatar Avatar--l")
        self.src = img.get('src').replace("_l", "")
        self.file = 'static/avatar/' + self.userid + '/' + os.path.basename(self.src)
        self.ret = '/static/avatar/' + self.userid + '/' + os.path.basename(self.src)
        print self.src

    def save_img(self):
        print os.getcwd()
        if not os.path.exists("static/avatar/" + self.userid):
            os.mkdir("static/avatar/" + self.userid)
        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36"
        }
        r = requests.get(self.src, headers=headers, verify=False)
        print r.status_code
        if r.status_code == 200:
            with open(self.file, 'wb') as f:
                for chunk in r:
                    f.write(chunk)

def main():
    tmp = Avatar('calton007')
    tmp.fetch_img_url()
    tmp.save_img()

if __name__ == '__main__':
    main()