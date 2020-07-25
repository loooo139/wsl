#!/usr/bin/python
# -*- coding:utf-8 -*-
'''

@Author: li xuefeng
@Date: 2020-07-25 01:06:38
@LastEditTime: 2020-07-25 12:05:19
@LastEditors: lixf
@Description: 
@FilePath: \wsl_py\crawler.py
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
driver = webdriver.Chrome(options=options)  # 打开 Chrome 浏览器
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
with open('./url.csv') as f:
    for k, line in enumerate(f):
        if k == 0:
            continue
        line = line.strip().split(',')
        url = []
        url.append(line[0])
        date_string = line[-1]
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
        except:
            print("wrong date" + date_string)
            continue
result = []
import redis
r=redis.StrictRedis(host='tencent.latiaohaochi.cn',port=6379,password='6063268abc',db=0)
for url in url_list:
    r.rpush('urls','\t'.join(url_list))
print(r.llen('urls'))

res = open('./dis_res.csv', 'a', encoding='utf8')
# driver.implicitly_wait(0.5)
while r.llen('urls')!=0:
    time.sleep(5)
    print('remain task', r.llen('urls'))
    line =r.lindex('urls',0).split('\t')
    r.lpop('urls')
    name, start_date, end_date = line[0], line[1], line[2]
    try:

        driver.get(
            "https://www.wsj.com/search/term.html?KEYWORDS={name}&min-date={start_date}&max-date={end_date}&isAdvanced=true&daysback=90d&andor=AND&sort=date-desc&source=wsjarticle"
            .format(name=name, start_date=start_date, end_date=end_date))
        try:
            len_res = int(
                driver.find_elements_by_xpath('//li[@class="results-count"]')
                [0].text.split()[-1])
        except:
            r.rpush('urls','\t'.join(line))
            continue
        for i in range(int(len_res / 20) + 1):
            print("full len  page is {0},cur is {1}".format(
                int(len_res / 20) + 1, i + 1))
            if i != 0:
                continue
                # 有问题，待修复
                time.sleep(2)
                driver.find_elements_by_xpath(
                    '//li[@class="next-page"]')[0].click()
                time.sleep(3)
                cur_res = int(
                    driver.find_elements_by_xpath(
                        '//li[@class="results-count"]').text.split()[-1])
                print('click next page finish,cur_lenth is %d', cur_res)
                if cur_res != len_res:
                    r.rpush('urls','\t'.join(line))
                    continue
            news = driver.find_elements_by_xpath(
                '//div[@class="headline-container"]')
            print("find " + str(len(news)) + "news")
            if len(news) == 0:
                r.rpush('urls','\t'.join(line))
                continue
            for k, i in enumerate(news):
                print(k + 1)
                # print(i.text)
                new_res = i.text.split('\n')
                t = i.find_elements_by_xpath('//li[@class="byline"]')
                try:

                    try:
                        author = i.find_elements_by_xpath(
                            '//li[@class="byline"]')[k].text[3:]
                    except:
                        author = 'null'
                    tag = i.find_elements_by_xpath(
                        '//div[@class="category"]')[k].text
                    title = i.find_elements_by_xpath(
                        '//h3[@class="headline"]')[k].text
                    date = i.find_elements_by_xpath('//time')[k].text
                    absrtact = i.find_elements_by_xpath(
                        '//div[@class="summary-container"]')[k].text
                    single_res = '\t'.join([
                        name, start_date, end_date, tag, title, author, date,
                        absrtact
                    ])
                    if r.sadd('news',single_res)!=0:
                        res.write(single_res + '\n')
                        print(single_res)
                    else:
                        print('duplicate news')
                except:
                    single_res = '\t'.join(
                        [name, start_date, end_date, i.text])
                    res.write(single_res + '\n')
                print('write one news ' + str(k))
        print('finish one  pages jobs,left is ', r.llen('urls'))

        # res.write(i.text)
    except:
        r.rpush('urls','\t'.join(line))
#  得到网页 html, 还能截图
driver.quit()
