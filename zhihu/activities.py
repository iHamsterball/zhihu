# -*- coding: utf-8 -*-
# Build-in / Std
import os, sys, time, platform, random, string, pickle
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

class Activities:
    _xsrf = None
    userid = None
    url = None
    soup = None
    log = None
    saved_data = None
    count = None
    call_count = None
    list = None
    array = None
    relative_frequency = None

    def __init__(self, userid):
        self.userid = userid
        self.url = "https://www.zhihu.com/people/" + userid + "/activities"
        self.__get_xsrf__()
        self.saved_data = 0
        self.count = 0
        self.call_count = 0
        self.list = []
        self.array = [0] * 24
        self.relative_frequency = [0.0] * 24

    #def __check_end__(self):
        # 如果递归get_activity返回则为结束

    def __delay__(self):
        time.sleep(random.uniform(2, 10))

    def __get_xsrf__(self):
        # 部分 userid 无法被用于获取 xsrf，目测是编码问题，可能存在被错误编码的 utf-8 字符
        # 故直接采用自己的 id，反正 xsrf 只要任意知乎网页都可以获取到
        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
            'Host': "www.zhihu.com",
            'Origin': "https://www.zhihu.com",
            'Pragma': "no-cache",
            'Referer': "https://www.zhihu.com/people/hamster-53"
        }
        r = requests.get("https://www.zhihu.com/people/hamster-53", headers=headers, verify=False)
        self.soup = BeautifulSoup(r.content, "lxml")
        print r.encoding
        print r.status_code
        #print self.soup
        self._xsrf = self.soup.find("input", attrs={'name': '_xsrf'})["value"]
        print self._xsrf
        
    def __update_log__(self):
        tmplist = self.soup.find_all("div", class_="zm-profile-section-item zm-item clearfix")
        for item in tmplist:
            #print item
            #print not (item.get('data-time') == '' or item.get('data-time') == None)
            if item.has_attr('data-time'):
                print item.get('data-time')
                if len(item.get('data-time')) >= 10 and string.atoi(item.get('data-time')) >= 1295971200:
                    self.list.append(string.atoi(item.get('data-time')))
        self.log = str(self.list[-1])
        print "log value: " + self.log
        #print time.localtime(string.atof(self.log))
    
    def __get_activity__(self):
        # 极端情况下会超出递归上限，所以并不能用递归写法
        # ヾ(•ω•`)o
        self.call_count += 1
        print self.call_count
        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
            'Host': "www.zhihu.com",
            'Origin': "https://www.zhihu.com",
            'Pragma': "no-cache",
            'Referer': "https://www.zhihu.com/people/" + self.userid,
            'X-Requested-With': "XMLHttpRequest",
            'X-Xsrftoken': self._xsrf
        }
        if self.log == None:
            params = {}
        else:
            params = {
                'start': self.log
            }
        
        #print 'Sending requests...'
        r = requests.post(self.url, headers=headers, params=params, verify=False)

        print r.status_code
        if r.status_code != 200:
            print "Retring.."
            return self.get_activity()

        print r.json()['msg'][0]
        if r.json()["msg"][0] == 0:
            print "All data gathered, saving result"
            self.save_result()
            return True

        response = r.json()["msg"][1]
        if platform.system() == 'Windows':
            response = response.decode('utf-8').encode('gbk', 'ignore')
        self.soup = BeautifulSoup(response, "lxml")
        #self.soup.prettify()
        self.__update_log__()
        return False

    def gather_from_website(self):
        flag = False
        while (not flag):
            flag = self.__get_activity__()
            self.__delay__()
            #print type(self.saved_data)
            #print type(self.log)
            if self.saved_data > string.atoi(self.log):
                flag = True
        self.list = list(set(self.list))
        self.list.sort(reverse=True)
        self.save_result()


    def generate_statistics(self, start=0, end=sys.maxint, timezone='Asia/Harbin'):
        os.environ['TZ'] = timezone
        if not platform.system() == 'Windows':
            time.tzset()
            print os.environ.get('TZ', '(not set)')
        for i in self.list:
            if i >= start and i <= end:
                self.count += 1
                self.array[time.localtime(i)[3]] += 1

    def calculate(self):
        if self.count == 0:
            return False
        tmp = 0
        for i in self.array:
            self.relative_frequency[tmp] = float(i) / self.count
            tmp += 1
        return True

    def save_result(self):
        print os.getcwd()
        if not os.path.exists("data/" + self.userid):
            os.mkdir("data/" + self.userid)
        list_file = file("data/" + self.userid + "/list.ser", "wt")
        pickle.dump(self.list, list_file)

    def check_gathered(self):
        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
            'Host': "www.zhihu.com",
            'Origin': "https://www.zhihu.com",
            'Pragma': "no-cache",
            'Referer': "https://www.zhihu.com/people/" + self.userid,
            'X-Requested-With': "XMLHttpRequest",
            'X-Xsrftoken': self._xsrf
        }
        r = requests.post(self.url, headers=headers, verify=False)
        if r.status_code != 200:
            print "Retring.."
            self.check_gathered()
            return
        response = r.json()["msg"][1]
        if platform.system() == 'Windows':
            response = response.decode('utf-8').encode('gbk', 'ignore')
        self.soup = BeautifulSoup(r.json()["msg"][1], "lxml")
        self.soup.prettify()
        node = self.soup.find("div", class_="zm-profile-section-item zm-item clearfix")
        if not os.path.exists("data/" + self.userid):
            return False
        list_file = file("data/" + self.userid + "/list.ser", "rt")
        list = pickle.load(list_file)
        if len(list) != 0:
            print type(node.get("data-time"))
            print type(list[0])
            self.list = list
            self.saved_data = list[0]
            print string.atoi(node.get("data-time")) == list[0]
            if string.atoi(node.get("data-time")) == list[0]:
                return True
        return False

    def load_from_file(self):
        list_file = file("data/" + self.userid + "/list.ser", "rt")
        self.list = pickle.load(list_file)

    @staticmethod
    def check_userid(userid):
        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
            'Host': "www.zhihu.com",
            'Origin': "https://www.zhihu.com",
            'Pragma': "no-cache",
            'Referer': "https://www.zhihu.com/people/hamster-53"
        }
        r = requests.get('https://www.zhihu.com/people/' + userid, headers=headers)
        print r
        print r.status_code
        if r.status_code != 200:
            return False
        return True

def main():
    tmp = Activities('calton007')
    tmp.get_activity()
    #tmp.generate_statistics()
    tmp.generate_statistics(1434443557, 1439483656)
    tmp.calculate()
    print tmp.array
    print tmp.count
    print tmp.relative_frequency

if __name__ == '__main__':
    main()
