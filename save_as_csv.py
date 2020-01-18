#!/usr/bin/env python3
# _*_ coding: utf-8  _*_

'For my job! Oh my god!!!'

__author__ = 'Jeremy Tsui'

from gevent import monkey
monkey.patch_all()
from queue import Queue
import requests,json,csv,gevent,re


#—————————全局变量的定义——————————————————

#rail way workspace
first_url2 = 'https://prod.pandateacher.com/ninth-studio-future-railway/base-backend/conductor/chats/panels/10/modules?current_path=%2F%252Fpanel%252Fconductor'
proxy = {'http': '117.94.182.64'}

#update browser's headers
todayheaders='''Host: prod.pandateacher.com
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:72.0) Gecko/20100101 Firefox/72.0
Accept: application/json, text/plain, */*
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate, br
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdmF0YXIiOiJodHRwczovL2dpdC5mb3JjaGFuZ2UuY24vdXBsb2Fkcy8tL3N5c3RlbS91c2VyL2F2YXRhci80OTAvYXZhdGFyLnBuZyIsImV4cCI6MTU3OTM0Nzc2NiwiaWF0IjoxNTc5MzQwNTY2LCJpc3MiOiJsd3JEekJhN1FEOGJ4OU8wSDF5N2lUT1R4ZGdQRE16YSIsIm5hbWUiOiLltJTkv4rmnbAiLCJzdWIiOjQ5MCwidW5hbWUiOiJjdWlqdW5qaWUifQ.3LgtVCLEineqiNmt7t9mzgM1b0k7QpSYhjuUFwXPYuA
Connection: keep-alive
Referer: https://prod.pandateacher.com/ninth-studio-future-railway/frontend/
Cookie: sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22obmqi1Px1ozjOic9rMfYzI2fD87s%22%2C%22%24device_id%22%3A%2216dc975ec5afa-033c310891cf5a8-4a5b66-1764000-16dc975ec5b4aa%22%2C%22props%22%3A%7B%22%24latest_referrer%22%3A%22%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%2C%22first_id%22%3A%2216dc975ec5afa-033c310891cf5a8-4a5b66-1764000-16dc975ec5b4aa%22%7D; SERVERID=2e838da71e6d77631c71e2ccab8f6db9|1579343899|1579311641; locale=zh-CN; prod-auth-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdmF0YXIiOiJodHRwczovL2dpdC5mb3JjaGFuZ2UuY24vdXBsb2Fkcy8tL3N5c3RlbS91c2VyL2F2YXRhci80OTAvYXZhdGFyLnBuZyIsImV4cCI6MTU3OTM0Nzc2NiwiaWF0IjoxNTc5MzQwNTY2LCJpc3MiOiJsd3JEekJhN1FEOGJ4OU8wSDF5N2lUT1R4ZGdQRE16YSIsIm5hbWUiOiLltJTkv4rmnbAiLCJzdWIiOjQ5MCwidW5hbWUiOiJjdWlqdW5qaWUifQ.3LgtVCLEineqiNmt7t9mzgM1b0k7QpSYhjuUFwXPYuA
TE: Trailers'''

headers = dict([line.split(": ", 1) for line in todayheaders.split("\n")])

# special_word = input('keywords in special students\' name that need private conversation')
keyword = ['忙忙', '考试', '妈妈', '放弃', '特殊','请假', '周一', '周二', '周三', '周四', '周五', '周六', '周日', '周末','不回复', '明天'] 

abs_path = '/Users/apple/Desktop/op_savecsv/'
work = Queue()

#some students need personal conversation
private_stu = []
normal_stu = []

#increase COUNT_INDEX for showing schedule in console log.  
COUNT_INDEX = 0
standard_target = 0
num = 0
end_num = 0

#-------判断哪个阶段，每个阶段的最后在第几行————————————
def get_class():
    while True:
        now_class = input('which class? please input number\n 1、山脚   2、山腰   3、山顶  \n')
        if now_class in ['1','2','3']:
            return int(now_class)


#第一个请求，获取所有同学微信的列表，用于构造请求每个学生信息的URL，以备加入异步任务。返回列表长度，输出进度百分比
def get_wx():
    res = requests.get(first_url2, headers = headers, proxies = proxy)
    data_js = json.loads(res.text)

    #collect data I need(only wxid)
    try:
        get_allstu_group = data_js['data']['lists'][1]['lists']
    except:
        print('Headers had updated, please copy a new one and run again!!')
        exit()
    # collect students that have not learned today, or before. Save as a csv file prepare for create a json list
    #before we write in folder, set a absolute path first
    #这一段要留意SSSSSSSSSS
    #试试改写用with open的语法 因为这里就用了一次，希望可以和数据写入一起操作。不单独写标题了
    #normalstufile = open(abs_path + 'complete_data.csv', 'w', newline = '', encoding = 'utf-8-sig')
    #writer = csv.writer(normalstufile)
    #writer.writerow(['nickname', 'wxid', 'details', 'level', 'progress', 'learning status'])
    #这一段要留意EEEEEEEEEEEE

    #create a url that can get each student's data. Then put it into a task
    for studata in get_allstu_group:
        wxid = studata['wxid']
        #url = 'https://prod.pandateacher.com/ninth-studio-future-railway/base-backend/conductor/buddy/wxid_d4vx8gec8whv22/dc06090326?current_path=%2Fpanel%2Fconductor&is_group=false'
        status_url = 'https://prod.pandateacher.com/ninth-studio-future-railway/base-backend/conductor/buddy/wxid_d4vx8gec8whv22/{}?current_path=%2Fpanel%2Fconductor&is_group=false'.format(wxid)
        work.put_nowait(status_url)

    #wanna print schedule, so I need this num to check presentage
    return len(get_allstu_group)

def crawler():
    global COUNT_INDEX
    while not work.empty():
        COUNT_INDEX += 1
        url = work.get_nowait()
        res2 = requests.get(url, headers = headers, proxies = proxy)
        res_json = res2.json()
        weixin = res_json['data']['wxid']
        nickname = res_json['data']['nickname']
        info = res_json['data']['current_train_info']
        
        try:
            progress = info['progress']
            level = re.findall(r'第(.*?)课', progress)[0]
            distance = re.findall(r'#(.*?)句', progress)[0]
        except:
            progress = ''

        #determine whether any keyword is included in nickname
        if progress == '':
            level,distance = '无数据','无数据'
            private_stu.append([nickname, weixin, progress, level, distance])

        elif int(level) >= standard_target and int(distance)==end_num:
            normal_stu.append([nickname, weixin, progress, level, distance])

        elif list( filter(lambda x: x in nickname,keyword)): 
            private_stu.append([nickname, weixin, progress, level, distance])

        else:
            normal_stu.append([nickname, weixin, progress, level, distance])

        print("\b"*30,end="",flush=True)
        print('sum: {}, process: {:.1f}%'.format(num,100*(COUNT_INDEX/num) ), end="")


def start_task():        
    task_list = []
    for i in range(5):
        task = gevent.spawn(crawler)
        task_list.append(task)
    gevent.joinall(task_list)

def write_in():
    with open(abs_path + 'complete_data.csv', 'w') as crawlfile:
        writer = csv.writer(crawlfile)
        writer.writerow(['nickname', 'wxid', 'details', 'level', 'progress', 'learning status'])
        writer.writerows(normal_stu)


def output_csv():
    if private_stu:
        with open(abs_path + 'per_con.csv', 'w', newline='') as perfile:
            writer = csv.writer(perfile)
            writer.writerow(['nickname', 'wxid', 'details', 'level', 'progress', 'learning status'])
            writer.writerows(private_stu)
        print('Special students done！！')
    else:
        print('Empty special students list !!!')

    try:
        with open(abs_path + 'all_names.csv') as allwx_file:
            reader = csv.reader(allwx_file)
            all_names_dict = dict((line[0],line[1]) for line in reader)

        with open(abs_path + 'complete_data.csv') as actwx_file:
            reader = csv.reader(actwx_file)
            act_wxnames = [line[1] for line in reader]

        with open(abs_path + 'stu_not_in_list/miss_stu.csv', 'w') as miss_file:
            writer = csv.writer(miss_file)
            for wxname,nickname in all_names_dict.items():
                if wxname not in act_wxnames:
                    writer.writerow([wxname,nickname])
        
    except FileNotFoundError:
        print('You miss some documents......please check\n\n')

    except UnicodeDecodeError:
        print('CSV document can\'t not be encoded by <Unicode> , \n need to save as other encode format')

    print('Separate students at different stages')


def start_job():
    global standard_target,num,end_num
    now_class = get_class()
    standard_target = ( now_class + 1 ) * 5
    if standard_target == 5:
        end_num = 158
    elif standard_target == 10:
        end_num = 205
    else:
        end_num = 147

    num = get_wx()
    start_task()
    write_in()
    output_csv()



if __name__ == "__main__":
    start_job()
