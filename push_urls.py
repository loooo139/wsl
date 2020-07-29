'''
@Author: li xuefeng
@Date: 2020-07-28 22:28:02
@LastEditTime: 2020-07-29 13:26:55
@LastEditors: lixf
@Description: 
@FilePath: \wsl\push_urls.py
@越码越快乐
'''
import threading, queue
from selenium import webdriver
from datetime import date
from datetime import timedelta
import time
options = webdriver.ChromeOptions()
# 设置中文
#options.add_argument('--ignore-certificate-errors')
from selenium.webdriver.chrome.options import Options
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--headless')
# 更换头部
options.add_argument(
    'user-agent="Mozilla/5.0 (iPod; U; CPU iPhone OS 2_1 like Mac OS X; ja-jp) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5F137 Safari/525.20"'
)
#options.add_argument("--proxy-server=socks5://127.0.0.1:10808")
month_dict = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12
}
# 将刚刚复制的帖在这
url_list = []
url_que = queue.Queue()
with open('./urls.csv') as f:
    for k, line in enumerate(f):
        if k == 0:
            continue
        line = line.strip().split(',')
        url = []
        url.append(line[0])
        date_string = line[1]
        year = date_string[-4:]
        mon = month_dict[date_string[2:5]]
        day = date_string[:2]
        try:
            begin = date(int(year), int(mon), int(day))
            start_date = begin.strftime("%Y/%m/%d")
            end_date = (begin + timedelta(days=3)).strftime("%Y/%m/%d")
            url.append(start_date)
            url.append(end_date)
            url_list.append(url)
            url_que.put(url)
            url_que.put([
                line[2],
                start_date,
                end_date,
            ])
        except:
            print("wrong date" + date_string)
            continue
result = []
import redis
r = redis.StrictRedis(host='tencent.latiaohaochi.cn',
                      port=6379,
                      password='6063268abc',
                      db=0)
for i, url in enumerate(url_list):
    r.sadd('urls', '\t'.join(url))
    print(i,r.scard('urls'))
