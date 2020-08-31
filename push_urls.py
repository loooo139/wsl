'''
@Author: li xuefeng
@Date: 2020-07-28 22:28:02
LastEditTime: 2020-08-31 22:03:11
LastEditors: lixf
@Description: 
FilePath: \wsl\push_urls.py
@越码越快乐
'''
import threading, queue
from selenium import webdriver
from datetime import date
from datetime import timedelta
import time, sys

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
with open('./new_reporter.txt') as f:
    for k, line in enumerate(f):
        if k == 0:
            continue
        line = line.strip()
        tmp = line.split('\t')
        other, author = tmp[:-1], tmp[-1]
        if '"' in author:
            author = author.replace('"', "").split(",")
            author = map(lambda x: x.strip(), author)
            for i in author:
                tmp_list = [j for j in other]
                tmp_list.append(i)
                url_list.append('\t'.join(tmp_list))
        else:
            url_list.append(line)
        # url = []
        # url.append(line[0])
        # date_string = line[1]
        # year = date_string[-4:]
        # mon = month_dict[date_string[2:5]]
        # day = date_string[:2]
        # try:
        #     begin = date(int(year), int(mon), int(day))
        #     start_date = begin.strftime("%Y/%m/%d")
        #     end_date = (begin + timedelta(days=3)).strftime("%Y/%m/%d")
        #     url.append(start_date)
        #     url.append(end_date)
        #     url_list.append(url)
        #     if len(url[0]) == 0:
        #         print('\t'.join(line))
        #     tmp = [line[2], start_date, end_date]
        #     url_list.append(tmp)
        #     if len(tmp[0]) == 0:
        #         print('\t'.join(line))
        #         print(k)
        # except:
        #     print("wrong date" + date_string)
        #     print(sys.exc_info())
        #     continue
result = []
import redis
r = redis.StrictRedis(host='tencent.latiaohaochi.cn',
                      port=6379,
                      password='6063268abc',
                      db=0)
time_null = 0
for i, url in enumerate(url_list):
    # if len(url[0]) == 0:
    #     print('null key_word ')
    #     time_null += 1
    #     print(time_null)
    #     continue
    r.sadd('author_urls', url)
    print(i, r.scard('author_urls'))
