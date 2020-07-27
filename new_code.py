'''
@Author: li xuefeng
@Date: 2020-07-25 01:06:38
@LastEditTime: 2020-07-27 12:35:34
@LastEditors: lixf
@Description: 
@FilePath: \wsl_py\crawler.py
@越码越快乐
'''
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading, queue
from selenium import webdriver
from datetime import date
from datetime import timedelta
import time
import pymysql
from lxml import etree
import sys
options = webdriver.ChromeOptions()
# 设置中文
options.add_argument('lang=zh_CN.UTF-8')
options.add_argument('--ignore-certificate-errors')
# options.add_argument('--headless')
# 更换头部

# mobile_emulation = {"deviceName": "Nexus 5"}

# options.add_experimental_option("mobileEmulation", mobile_emulation)

options.add_argument(
    'user-agent="Mozilla/5.0 (iPDd; U; CPU iPhone OS 2_1 like Mac OS X; ja-jp) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5F137 Safari/525.20"'
)
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
res = open('./res_v1.csv', 'a', encoding='utf8')
full_res = 0
driver.implicitly_wait(10)
# driver.set_page_load_timeout(10)
mysql = pymysql.connect(host='tencent.latiaohaochi.cn',
                        user='root',
                        password='6063268abc',
                        db='crawler')
cursor = mysql.cursor()
sql = 'insert into wsl_news(key_word,start_date,end_date,news_tag,news_title,news_author,news_time,news_summary,news_url) values("{}","{}","{}","{}","{}","{}","{}","{}","{}")'
while not url_que.empty():

    print('remain task', url_que.qsize())
    line = url_que.get()
    name, start_date, end_date = line[0], line[1], line[2]
    try:
        driver.get(
            "https://www.wsj.com/search/term.html?KEYWORDS={name}&min-date={start_date}&max-date={end_date}&isAdvanced=true&daysback=90d&andor=AND&sort=date-desc&source=wsjarticle"
            .format(name=name, start_date=start_date, end_date=end_date))
        # WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located(
        #         (By.XPATH, "//div[@class='headline-container']")))
        # time.sleep(3)
        try:
            news = driver.find_elements_by_css_selector('.headline-container')
            len_res = int(
                driver.find_elements_by_css_selector(
                    'li[class="results-count"]')[0].text.split()[-1])
        except Exception as e:
            url_que.put(line)
            print('something wrong ', e, e.args)
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
                    url_que.put(line)
                    continue
            print("find " + str(len(news)) + " news")
            if len(news) == 0:
                url_que.put(line)
                continue
            # news_source = driver.page_source
            # print(news_source)
            # html = etree.HTML(news_source)
            # news = html.xpath('//div[@class="headline-container"]')
            for k, i in enumerate(news):
                print(k + 1)
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
                    date = i.find_elements_by_css_selector('time')[0].text
                    absrtact = i.find_elements_by_css_selector(
                        'div[class="summary-container"]')[0].text
                    news_url = i.find_elements_by_css_selector(
                        'h3 > a')[0].get_attribute('href')
                    single_res = '\t'.join([
                        name, start_date, end_date, tag, title, author, date,
                        absrtact, news_url
                    ])
                    res.write(single_res + '\n')
                    print(single_res)
                    try:
                        news_sql = sql.format(name, start_date, end_date, tag,
                                              title, author, date, absrtact,
                                              news_url)
                        cursor.execute(news_sql)
                        mysql.commit()
                        print('insert to db success')
                    except:
                        print(sys.exc_info())
                        print(news_sql)
                        print('insert to db failed')
                except Exception as e:
                    print('exception ', e)
                    single_res = '\t'.join(
                        [name, start_date, end_date, i.text])
                    res.write(single_res + '\n')
                print('write one news ' + str(++full_res))
        print('finish one  pages jobs,left is ', url_que.qsize())

        # res.write(i.text)
    except Exception as e:
        print('something wrong ', e, e.args)
        url_que.put(line)
#  得到网页 html, 还能截图
driver.quit()
