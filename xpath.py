import  queue
# from selenium import webdriver
from datetime import date
from datetime import timedelta
import time, requests
from lxml import etree
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
res = open('./baba.csv', 'a', encoding='utf8')
# driver.implicitly_wait(0.5)
headers = {
    'user-agent':
    'Mozilla/5.0 (iPod; U; CPU iPhone OS 2_1 like Mac OS X; ja-jp) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5F137 Safari/525.20'
}
while not url_que.empty():
    time.sleep(5)
    print('remain task%d', url_que.qsize())
    line = url_que.get()
    name, start_date, end_date = line[0], line[1], line[2]
    url = "https://www.wsj.com/search/term.html?KEYWORDS={name}&min-date={start_date}&max-date={end_date}&isAdvanced=true&daysback=90d&andor=AND&sort=date-desc&source=wsjarticle".format(
        name=name, start_date=start_date, end_date=end_date)

    r = requests.get(url=url,headers=headers,proxies=dict(http='socks5://127.0.0.1:10808',https='socks5://127.0.0.1:10808'))
    if r.status_code!=200:
        url_que.put(line)
        continue
    print(r.text)
    root=etree.HTML(r.text)
    nodes=root.xpath('//li[@class="results-count"]')
    try:

        page_len=root.xpath('//li[@class="results-count"]')[1].text.split()[-1]
        full_news=root.xpath('//li[@class="results-count"]')[0].text.split()[-1]
        print('full pags is '+page_len)
        for i in range(int(page_len)):
            # if i!=0:
            #     url = url +'&page={}'.format(i+1)

            #     r = requests.get(url=url,headers=headers,proxies=dict(http='socks5://127.0.0.1:10808',https='socks5://127.0.0.1:10808')
            #     root=etree.HTML(r.text)
                
            print('cur page is '+str(i+1))
            page_news=root.xpath('//div[@class="headline-container"]')
            for j,z in enumerate(page_news):
                print('get the '+str(j+1+20*i)+' news')
                single_news=i.text

    except:
        url_que.put(line)
        print('the page '+url+'is failed,try later,put it back to queue')