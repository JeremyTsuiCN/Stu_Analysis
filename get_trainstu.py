#!/usr/bin/env python3
# _*_ coding: utf-8  _*_

'For my job! Oh my god!!! '

__author__ = 'Jeremy Tsui'

from gevent import monkey
monkey.patch_all()
from queue import Queue
import requests, json, csv, gevent, re


proxy = {'http': '117.94.182.64'}

#update browser's headers, Next plan: [try to write in a txt file]
todayheaders='''Host: prod.pandateacher.com
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:73.0) Gecko/20100101 Firefox/73.0
Accept: application/json, text/plain, */*
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate, br
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdmF0YXIiOiJodHRwczovL2dpdC5mb3JjaGFuZ2UuY24vdXBsb2Fkcy8tL3N5c3RlbS91c2VyL2F2YXRhci80OTAvYXZhdGFyLnBuZyIsImV4cCI6MTU4MzA0MTg0NiwiaWF0IjoxNTgzMDM0NjQ2LCJpc3MiOiJsd3JEekJhN1FEOGJ4OU8wSDF5N2lUT1R4ZGdQRE16YSIsIm5hbWUiOiLltJTkv4rmnbAiLCJzdWIiOjQ5MCwidW5hbWUiOiJjdWlqdW5qaWUifQ.y7DxEXSW32sJodCM11Z_2MaOqLHxMeLwVWL53Jw0mVU
Connection: keep-alive
Referer: https://prod.pandateacher.com/ninth-studio-future-railway/frontend/
Cookie: sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22obmqi1Px1ozjOic9rMfYzI2fD87s%22%2C%22%24device_id%22%3A%2216dc975ec5afa-033c310891cf5a8-4a5b66-1764000-16dc975ec5b4aa%22%2C%22props%22%3A%7B%22%24latest_referrer%22%3A%22%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%2C%22first_id%22%3A%2216dc975ec5afa-033c310891cf5a8-4a5b66-1764000-16dc975ec5b4aa%22%7D; SERVERID=2e838da71e6d77631c71e2ccab8f6db9|1583036275|1583027442; locale=zh-CN; prod-auth-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdmF0YXIiOiJodHRwczovL2dpdC5mb3JjaGFuZ2UuY24vdXBsb2Fkcy8tL3N5c3RlbS91c2VyL2F2YXRhci80OTAvYXZhdGFyLnBuZyIsImV4cCI6MTU4MzA0MTg0NiwiaWF0IjoxNTgzMDM0NjQ2LCJpc3MiOiJsd3JEekJhN1FEOGJ4OU8wSDF5N2lUT1R4ZGdQRE16YSIsIm5hbWUiOiLltJTkv4rmnbAiLCJzdWIiOjQ5MCwidW5hbWUiOiJjdWlqdW5qaWUifQ.y7DxEXSW32sJodCM11Z_2MaOqLHxMeLwVWL53Jw0mVU
TE: Trailers'''

headers = dict([line.split(": ", 1) for line in todayheaders.split("\n")])
work = Queue()


train_url = 'https://prod.pandateacher.com/ninth-studio-future-railway/base-backend/conductor/chats/panels/13/modules?current_path=%2Fpanel%2Fconductor'


wxidlist = []
def get_wx():
    res = requests.get(train_url, headers = headers, proxies = proxy)
    data_js = json.loads(res.text)

    #collect data I need(only wxid)
    try:
        get_allstu_group = data_js['data']['lists'][0]['lists']
        for stu_list in get_allstu_group:
            wxidlist.append(stu_list['wxid'])
    except:
        print('Headers had updated, please copy a new one and run again!!')
        exit()


    #should update this url periodically to avoid potential errors.
    #_______ tutor's wxid _____
    for wxid in wxidlist:
        status_url = 'https://prod.pandateacher.com/ninth-studio-future-railway/base-backend/conductor/buddy/{}/{}?current_path=%2Fpanel%2Fconductor&is_group=false'.format('wxid_th5yqnhdcvzc22',wxid)
        work.put_nowait(status_url)

get_wx()
target_wxid = []
num =  0 
def crawler():
    global num
    while not work.empty():
        url = work.get_nowait()
        num += 1 
        res2 = requests.get(url, headers = headers, proxies = proxy)
        res_json = res2.json()

        try:
            progress = res_json['data']['course_info'][1]['progress']
            level = re.findall(r'第(.*?)关', progress)[0]

            if int(level) < 15:
                target_wxid.append(res_json['data']['wxid'])
        except:
            pass

task_list = []
for i in range(35):
    task = gevent.spawn(crawler)
    task_list.append(task)
gevent.joinall(task_list)

print(('一共{}/{}位学生').format(len(target_wxid), num))
data = ''
#get each student's wxid and combine it in a string 
for wxid in target_wxid:
    data+='{\"wxid\":'+' \"'+wxid+'\"'+'},'

#this string has to be including in a [ ]
data='['+data[:-1]+']'

with open('/Users/apple/Desktop/new.json', 'w') as f_wxid:
    f_wxid.write(data)