import json
import os
import pickle
import random
import time
from io import BytesIO
from threading import Thread
from urllib.parse import urlparse, parse_qs

import requests
from PIL import Image

# 用户的User-Agent列表
USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Mobile Safari/537.36",
]

class showpng(Thread):
    def __init__(self, data):
        Thread.__init__(self)
        self.data = data
    def run(self):
        img = Image.open(BytesIO(self.data))
        img.show()

class WeChatLogin():
    ua = random.choice(USER_AGENT_LIST)
    headers = {'User-Agent': ua, 'Referer': "https://mp.weixin.qq.com/","Host": "mp.weixin.qq.com"}

    def islogin(self,session):
        try:
            session.cookies.load(ignore_discard=True)
        except Exception:
            pass
        loginurl = session.get("https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=ask&token=&lang=zh_CN&f=json&ajax=1").json()
        if loginurl['base_resp']['ret'] == 0:
            print('Cookies值有效，无需扫码登录！')
            return session, True
        else:
            print('Cookies值已经失效，请重新扫码登录！')
            return session, False

    def gzhlogin(self):
        # 写入
        session = requests.session()
        if not os.path.exists('../gzhcookies.cookie'):
            with open('../gzhcookies.cookie', 'wb') as f:
                pickle.dump(session.cookies, f)
        # 读取
        session.cookies = pickle.load(open('../gzhcookies.cookie', 'rb'))
        session, status = self.islogin(session)

        if not status:
            session = requests.session()
            session.get('https://mp.weixin.qq.com/', headers=self.headers)
            session.post('https://mp.weixin.qq.com/cgi-bin/bizlogin?action=startlogin',
                         data='userlang=zh_CN&redirect_url=&login_type=3&sessionid={}&token=&lang=zh_CN&f=json&ajax=1'.format(int(time.time() * 1000)), headers=self.headers)
            loginurl = session.get('https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=getqrcode&random={}'.format(int(time.time() * 1000)))
            dateurl = 'https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=ask&token=&lang=zh_CN&f=json&ajax=1'
            t = showpng(loginurl.content)
            t.start()
            while 1:
                date = session.get(dateurl).json()
                if date['status'] == 0:
                    print('二维码未失效，请扫码！')
                elif date['status'] == 6:
                    print('已扫码，请确认！')
                if date['status'] == 1:
                    print('已确认，登录成功！')
                    url = session.post('https://mp.weixin.qq.com/cgi-bin/bizlogin?action=login',
                                       data='userlang=zh_CN&redirect_url=&cookie_forbidden=0&cookie_cleaned=1&plugin_used=0&login_type=3&token=&lang=zh_CN&f=json&ajax=1',
                                       headers=self.headers).json()
                    # url['redirect_url']:/cgi-bin/home?t=home/index&lang=zh_CN&token=1540184765
                    token = parse_qs(urlparse(url['redirect_url']).query).get('token', [None])[0]
                    session.get('https://mp.weixin.qq.com{}'.format(url['redirect_url']), headers=self.headers)
                    break
                time.sleep(2)
            cookie = '; '.join([f"{name}={value}" for name, value in session.cookies.items()])
            with open('../gzhcookies.cookie', 'wb') as f:
                pickle.dump(session.cookies, f)
            if not os.path.exists('../cookie.json'):
                with open('../cookie.json', 'w') as f:
                    line = {'token': token, 'cookie': cookie}
                    json.dump(line, f, ensure_ascii=False)
        else:
            with open('../cookie.json', 'r') as f:
                line = json.load(f)
        return line


def get_cookie_token():
    WeChatLogin().gzhlogin()
    with open('../cookie.json', 'r', encoding='utf-8') as f:
        cookies = json.load(f)
        cookie, token = cookies['cookie'], cookies['token']
    return cookie, token

if __name__ == "__main__":
    get_cookie_token()