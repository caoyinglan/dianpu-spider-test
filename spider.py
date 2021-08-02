import json

import requests
from bs4 import BeautifulSoup
import re
import sys
import time
import pandas as pd
import io
from functools import wraps
from selenium import webdriver

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def retry(times, sleep=0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            run_times = 0
            while 1:
                try:
                    return func(*args, **kwargs)
                except Exception as ex:
                    time.sleep(sleep)
                    if run_times < times:
                        run_times += 1
                    else:
                        raise ex
        return wrapper
    return decorator

class baixing(object):
    def __init__(self, shopid):
        self._url = "http://spider.battle.baixing.cn/detail/" + shopid
        self._id = shopid
        self._headers = {'User-agent':
                             'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.182 Safari/537.36',
                         'User-name':
                             'CCCCCYL20210723'
                         }
        self._info = []
        self._href = []
        self._phone = []

    def get_contents(self):
        requests.packages.urllib3.disable_warnings()
        s = requests.session()
        s.keep_alive = False

        proxies = {'http': 'http://LONGZHUASHOU6GBJR1KR0:8CDnVted@http-proxy-t3.dobel.cn:9180',
                 'https': 'http://LONGZHUASHOU6GBJR1KR0:8CDnVted@http-proxy-t3.dobel.cn:9180'}
        response = requests.get(self._url, proxies=proxies, headers=self._headers, verify=False)
        response.encoding = "utf-8"
        print(response.status_code)
        response = response.text
        allThings = BeautifulSoup(response, "html.parser")
        content_title = allThings.find_all('div', class_='company_name')
        pattern1 = re.compile('<a[^>]+href=["\'](.*?)["\']')
        href = pattern1.findall(str(content_title))
        print(href)
        self._href.append(href)
        info = content_title[0].get_text(" ", strip=True)
        print(info)
        self._info.append(info)

        response_phone = requests.get(url="http://spider.battle.baixing.cn/shops/"+ self._id + "/phone", proxies=proxies, headers=self._headers, verify=False)
        content_phone = json.loads(response_phone.text).get('data')
        self._phone.append(content_phone)


    def extract(self):
        self.get_contents()
        ticks = time.strftime("%Y-%m-%d", time.localtime())

        test = pd.DataFrame.from_dict({'info': self._info, 'phone': self._phone}, orient='index')
        path = '.baixing_test_' + str(ticks) + '.csv'
        test.to_csv(path, encoding='utf-8-sig', index=False)


try:
    @retry(3)
    def main():
        shopid = "80601236"
        data = baixing(shopid)
        data.extract()
except Exception as ex:
    print(ex)

def timer(n):
        '''''
        每n秒执行一次
        '''
        count = 0
        while True:
            print(time.strftime('%Y-%m-%d %X', time.localtime()))
            main()
            count += 1
            print(count)
            time.sleep(n)

timer(1)


# if __name__ == '__main__':
#    main()