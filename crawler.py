#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*- coding: utf-8 -*-
'''

@Author: li xuefeng
@Date: 2020-07-25 01:06:38

LastEditTime: 2020-09-07 21:17:08
LastEditors: lixf
@Description: 
FilePath: \wsl\crawler.py
@越码越快乐
'''
from datetime import datetime
import threading, queue
from selenium import webdriver
from datetime import date
from datetime import timedelta
import time
import redis
import pymysql
import sys, os, platform
from datetime import datetime, tzinfo, timedelta


class UTC(tzinfo):
    """UTC"""
    def __init__(self, offset=0):
        self._offset = offset

    def utcoffset(self, dt):
        return timedelta(hours=self._offset)

    def tzname(self, dt):
        return "UTC +%s" % self._offset

    def dst(self, dt):
        return timedelta(hours=self._offset)


def ping(url='tencent.latiaohaochi.cn'):
    print('ping ' + url)
    print('current os is ' + platform.platform())
    if 'Linux' in platform.platform():
        result = os.system(u'ping ' + url + ' -c 3')
    else:
        result = os.system(u"ping " + url + ' -n 3')
    #result = os.system(u"ping www.baidu.com -n 3")
    if result == 0:
        print("the network is good")
    else:
        print("can not connect the wsj,will use the proxy")
    return result


options = webdriver.ChromeOptions()
# 设置中文
# mobileEmulation = {'deviceName': 'Galaxy S5'}
options.add_argument('--ignore-certificate-errors')
# from selenium.webdriver.chrome.options import Options
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# options.add_experimental_option('mobileEmulation', mobileEmulation)
options.add_argument('--headless')
# 更换头部
options.add_argument(
    'user-agent="Mozilla/5.0 (iPod; U; CPU iPhone OS 2_1 like Mac OS X; ja-jp) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5F137 Safari/525.20"'
)
if ping() == 0:
    redis_url = 'tencent.latiaohaochi.cn'
    mysql_url = 'tencent.latiaohaochi.cn'
else:
    redis_url = 'latiaohaochi.cn'
    mysql_url = 'latiaohaochi.cn'
# if ping('www.google.com') != 0:
#     print('using proxy browse the wjs')
#     # options.add_argument("--proxy-server=socks5://n1.latiaohaochi.top:10808")
driver = webdriver.Chrome(options=options)  # 打开 Chrome 浏览器
r = redis.StrictRedis(host=redis_url,
                      port=6379,
                      password='6063268abc',
                      retry_on_timeout=5,
                      db=0)
res = open('./dis_res.csv', 'a', encoding='utf8', buffering=1)

#len_res=0
full_res = 0
driver.implicitly_wait(10)
# driver.set_page_load_timeout(10)
mysql = pymysql.connect(host=mysql_url,
                        user='root',
                        password='6063268abc',
                        connect_timeout=200,
                        db='crawler')
cursor = mysql.cursor()
sql = 'insert into wsl_news_v4(key_word,start_date,end_date,news_tag,news_title,news_author,news_time,news_summary,news_url,news_index) values("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'
fail_data = open('./other.csv', 'a', encoding='utf8')
while True:
    try:
        while r.scard('author_urls') != 0:
            #    time.sleep(5)
            print(datetime.now(UTC(8)))
            print('remain task')
            print(r.scard('author_urls'))
            line = r.spop('author_urls').decode('utf8').split('\t')
            #    r.lpop('urls')
            # name, start_date, end_date = line[0], line[1], line[2]
            origin_index, name, start_date, author_ori = line[0], line[
                1], line[2], line[-1]
            end_date = start_date.split()[0]
            start_date = str(int(end_date.split('/')[0]) - 1)
            start_date += end_date[4:]
            try:
                single_url = "https://www.wsj.com/search/term.html?KEYWORDS={name}&min-date={start_date}&max-date={end_date}&byline={author}&isAdvanced=true&daysback=1y&andor=AND&sort=date-desc&source=wsjarticle".format(
                    name=name.replace('&', '%26'),
                    start_date=start_date,
                    end_date=end_date,
                    author=author_ori)
                print('current url is ', single_url, '\n', 'loading')
                driver.get(single_url)
                print(datetime.now(UTC(8)))
                # WebDriverWait(driver, 10).until(
                #     EC.presence_of_element_located(
                #         (By.XPATH, "//div[@class='headline-container']")))
                # time.sleep(3)
                try:
                    news = driver.find_elements_by_css_selector(
                        '.headline-container')
                    if len(news) == 0:
                        print('no news parse')
                        r.sadd('author_urls', '\t'.join(line))
                        continue
                    len_res = int(
                        driver.find_elements_by_css_selector(
                            'li[class="results-count"]')[0].text.split()[-1])
                except IndexError as e:
                    # r.sadd('urls', '\t'.join(line))
                    print('find no news on this page,put it back to db')
                    print('current url is ', single_url)
                    r.sadd('author_urls', '\t'.join(line))
                    continue
                for i in range(int(len_res / 20) + 1):
                    print("full len  page is {0},cur is {1}".format(
                        int(len_res / 20) + 1, i + 1))
                    if i != 0:
                        # continue
                        # 有问题，待修复
                        # time.sleep(2)
                        driver.find_elements_by_xpath(
                            '//li[@class="next-page"]')[0].click()
                        # time.sleep(3)
                        cur_res = int(
                            driver.find_elements_by_css_selector(
                                'li[class="results-count"]')[0].text.split()
                            [-1])
                        print('click next page finish,cur_lenth is %d',
                              cur_res)
                        if cur_res != len_res:
                            r.radd('author_urls', '\t'.join(line))
                            continue
                        news = driver.find_elements_by_css_selector(
                            '.headline-container')
                    print("find " + str(len(news)) + " news")
                    if len(news) == 0:
                        r.sadd('author_urls', '\t'.join(line))
                        print('it seems there is no news ,try it later')
                        print('current url is ', single_url)
                        continue
                    for k, i in enumerate(news):
                        print(k + 1)
                        print(datetime.now(UTC(8)))
                        # print(i.text)
                        new_res = i.text.split('\n')
                        try:

                            try:
                                author = i.find_elements_by_css_selector(
                                    'li[class="byline"]')[0].text[3:]
                            except:
                                author = 'null'
                            tag = i.find_elements_by_css_selector(
                                'div[class="category"]')[0].text
                            title = i.find_elements_by_css_selector(
                                'h3[class="headline"]')[0].text
                            date = i.find_elements_by_css_selector(
                                'time')[0].text
                            absrtact = i.find_elements_by_css_selector(
                                'div[class="summary-container"]')[0].text
                            news_url = i.find_elements_by_css_selector(
                                'h3 > a')[0].get_attribute('href')
                            news_index = origin_index + '-' + author_ori
                            single_res = '\t'.join(
                                (name, start_date, end_date, tag, title,
                                 author, date, absrtact, news_url, news_index))
                            res.write(single_res + '\n')
                            print(single_res)
                            if r.sadd('news_v4', single_res) == 0:
                                print('duplicate news')
                                continue
                            try:
                                news_sql = sql.format(name, start_date,
                                                      end_date, tag, title,
                                                      author, date, absrtact,
                                                      news_url, news_index)
                                cursor.execute(news_sql)
                                mysql.commit()
                                print('insert to db success')
                                full_res += 1
                                print('write one news ' + str(full_res))
                            except:
                                print(sys.exc_info())
                                print(news_sql)
                                print('insert to db failed')
                                mysql = pymysql.connect(
                                    host='tencent.latiaohaochi.cn',
                                    user='root',
                                    password='6063268abc',
                                    connect_timeout=20,
                                    db='crawler')
                                cursor = mysql.cursor()
                                mysql.rollback()
                        except Exception as e:
                            print('exception', e, sys.exc_info())
                            single_res = '\t'.join(
                                [name, start_date, end_date, i.text])
                            fail_data.write(single_res + '\n')

                print('finish one  pages jobs,left is ', r.scard('urls'))

                # res.write(i.text)
            except Exception as e:
                print(datetime.now(UTC(8)))
                print('something wrong ', e, e.args, sys.exc_info())
                print('could not load the page,tiemout,try late')
                r = redis.StrictRedis(host=redis_url,
                                      port=6379,
                                      password='6063268abc',
                                      retry_on_timeout=5,
                                      db=0)
                r.sadd('author_urls', '\t'.join(line))
        #  得到网页 html, 还能截图
        print('jobs finish ,queue is empty')
        break
    except Exception as e:
        print('maybe redis is down ', sys.exc_info())
        print(e, e.args)
        r = redis.StrictRedis(host=redis_url,
                              port=6379,
                              password='6063268abc',
                              retry_on_timeout=5,
                              db=0)
        mysql = pymysql.connect(host=mysql_url,
                                user='root',
                                password='6063268abc',
                                connect_timeout=20,
                                db='crawler')
        cursor = mysql.cursor()
driver.quit()
