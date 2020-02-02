#!/usr/bin/env python3
# _*_ coding: utf-8  _*_

'For my job! Oh my god!!! Next test: try to increase [start_task] num to test efficiency'

__author__ = 'Jeremy Tsui'

from gevent import monkey
monkey.patch_all()
from queue import Queue
import requests, json, csv, gevent, re, math, os

#get ready for the first requests
first_url2 = 'https://prod.pandateacher.com/ninth-studio-future-railway/base-backend/conductor/chats/panels/10/modules?current_path=%2F%252Fpanel%252Fconductor'
proxy = {'http': '117.94.182.64'}

#update browser's headers, Next plan: [try to write in a txt file]
todayheaders='''Host: prod.pandateacher.com
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:72.0) Gecko/20100101 Firefox/72.0
Accept: application/json, text/plain, */*
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate, br
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdmF0YXIiOiJodHRwczovL2dpdC5mb3JjaGFuZ2UuY24vdXBsb2Fkcy8tL3N5c3RlbS91c2VyL2F2YXRhci80OTAvYXZhdGFyLnBuZyIsImV4cCI6MTU4MDYxOTkwMiwiaWF0IjoxNTgwNjEyNzAyLCJpc3MiOiJsd3JEekJhN1FEOGJ4OU8wSDF5N2lUT1R4ZGdQRE16YSIsIm5hbWUiOiLltJTkv4rmnbAiLCJzdWIiOjQ5MCwidW5hbWUiOiJjdWlqdW5qaWUifQ.yc8V1-R7XJ-OqD79lJRqHM3GoYCv--VGLmwgRMBf47s
Connection: keep-alive
Referer: https://prod.pandateacher.com/ninth-studio-future-railway/frontend/
Cookie: sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22obmqi1Px1ozjOic9rMfYzI2fD87s%22%2C%22%24device_id%22%3A%2216dc975ec5afa-033c310891cf5a8-4a5b66-1764000-16dc975ec5b4aa%22%2C%22props%22%3A%7B%22%24latest_referrer%22%3A%22%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%2C%22first_id%22%3A%2216dc975ec5afa-033c310891cf5a8-4a5b66-1764000-16dc975ec5b4aa%22%7D; SERVERID=f7690181957e443b2faca215e25bdaf8|1580617507|1580612701; prod-auth-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdmF0YXIiOiJodHRwczovL2dpdC5mb3JjaGFuZ2UuY24vdXBsb2Fkcy8tL3N5c3RlbS91c2VyL2F2YXRhci80OTAvYXZhdGFyLnBuZyIsImV4cCI6MTU4MDYxOTkwMiwiaWF0IjoxNTgwNjEyNzAyLCJpc3MiOiJsd3JEekJhN1FEOGJ4OU8wSDF5N2lUT1R4ZGdQRE16YSIsIm5hbWUiOiLltJTkv4rmnbAiLCJzdWIiOjQ5MCwidW5hbWUiOiJjdWlqdW5qaWUifQ.yc8V1-R7XJ-OqD79lJRqHM3GoYCv--VGLmwgRMBf47s; locale=zh-CN
TE: Trailers'''

headers = dict([line.split(": ", 1) for line in todayheaders.split("\n")])

#special students' keyword in nicknames 
keyword = ['忙忙', '考试', '妈妈', '放弃', '特殊','请假', '周一', '周二', '周三', '周四', '周五', '周六', '周日', '周末','不回复', '明天'] 


def createpath(newpath):
    try:
        os.makedirs(newpath)
    except FileExistsError:
        print(newpath+'目录存在，可以直接写入文件\n')
    finally:
        return newpath



abs_path = createpath('/Users/apple/Desktop/op_savecsv/')
work = Queue()

#some students need personal conversation 
# +++++Change now+++++ need to append some student
supply_stu = []
private_stu = []
normal_stu = []

#increase COUNT_INDEX for showing schedule in console log.  
COUNT_INDEX = 0
standard_target = 0
num = 0
end_num = 0
now_class = 0




#determine class level, return the answer to standard_target
def get_class():
    while True:
        now_class = input('which class? please input number\n 1、山脚   2、山腰   3、山顶  \n')
        if now_class in ['1','2','3']:
            return int(now_class)

#send first requests,then get all students' wxid, for creating each student's url. these urls will put into queue.
#get urls' num and return
#Next Version ==>  put putnowait action outside this function, for trying to analysis students situation offline
def get_wx():
    res = requests.get(first_url2, headers = headers, proxies = proxy)
    data_js = json.loads(res.text)

    #collect data I need(only wxid)
    try:
        get_allstu_group = data_js['data']['lists'][1]['lists']
    except:
        print('Headers had updated, please copy a new one and run again!!')
        exit()

    #create a url that can get each student's data. Then put it into a task
    for studata in get_allstu_group:
        wxid = studata['wxid']
        #url = 'https://prod.pandateacher.com/ninth-studio-future-railway/base-backend/conductor/buddy/wxid_d4vx8gec8whv22/dc06090326?current_path=%2Fpanel%2Fconductor&is_group=false's
        status_url = 'https://prod.pandateacher.com/ninth-studio-future-railway/base-backend/conductor/buddy/wxid_d4vx8gec8whv22/{}?current_path=%2Fpanel%2Fconductor&is_group=false'.format(wxid)
        work.put_nowait(status_url)

    #wanna print schedule, so I need this num to check presentage
    return len(get_allstu_group)

#each task , increases COUNT_INDEX to print percentage of getting data's schedule
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

        
        if progress == '':
            level,distance = '无数据','无数据'
            private_stu.append([nickname, weixin, progress, level, distance])
        #determine whether any keyword is included in nickname
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
    for i in range(35):
        task = gevent.spawn(crawler)
        task_list.append(task)
    gevent.joinall(task_list)

def write_in():
    with open(abs_path + 'students_in_rail.csv', 'w') as crawlfile:
        writer = csv.writer(crawlfile)
        writer.writerow(['nickname', 'wxid', 'details', 'level', 'progress', 'learning status'])
        writer.writerows(normal_stu)
    print('write in all students in this train complete!!\n')

def output_csv():
    if private_stu:
        with open(abs_path + 'per_con.csv', 'w', newline='') as perfile:
            writer = csv.writer(perfile)
            writer.writerow(['nickname', 'wxid', 'details', 'level', 'progress', 'learning status'])
            writer.writerows(private_stu)
        print('Write in special students successful!!!\n\n')
    else:
        print('Empty special students list !!!')

    try:
        with open(abs_path + 'all_names.csv') as allwx_file:
            reader = csv.reader(allwx_file)
            all_names_dict = dict((line[0],line[1]) for line in reader)

        with open(abs_path + 'students_in_rail.csv') as actwx_file:
            reader = csv.reader(actwx_file)
            act_wxnames = [line[1] for line in reader]
        
        missfile_path = createpath(abs_path + 'miss/')
        with open(missfile_path+'miss_stu.csv', 'w') as miss_file:
            writer = csv.writer(miss_file)
            for wxname,nickname in all_names_dict.items():
                if wxname not in act_wxnames:
                    writer.writerow([wxname,nickname])
        print('All csvs had generated successfully~~~')
        
    except FileNotFoundError:
        print('You miss some documents......please check\n\n')

    except UnicodeDecodeError:
        print('CSV document can\'t not be encoded by <Unicode> , \n need to save as other encode format')

    print('Separate 3 status students in csv~\n')

# One class has to set 12 groups students
level_5 = []
level_6_low = []
level_6_high = []
level_7_low = []
level_7_high = []
level_8_low = []
level_8_high = []
level_9_low = []
level_9_high = []
level_10_low = []
level_10_high = []
level_over = []
#create a main list to save all groups, name a list, and it will get a 'n' to mark it's index.
all_list = [level_5,level_6_low ,level_6_high,level_7_low,level_7_high,level_8_low,level_8_high,level_9_low,level_9_high,level_10_low,level_10_high,level_over]

work2 = Queue()
#put these groups into queue
for all in all_list:
    work2.put_nowait(all)

#read csv's data by line, distinguish, then add to target list
def add2list():
    with open(abs_path+'students_in_rail.csv') as raildata:
        data = raildata.readlines()
    level_num = (int(now_class)-1)*5

    for eachline in data:
        line = eachline.split(',')
        try:
            if int(line[3]) == level_num:
                level_5.append(line)

            elif int(line[3]) == level_num+1:
                if int(line[4]) < 70:
                    level_6_low.append(line)
                else:
                    level_6_high.append(line)

            elif int(line[3]) == level_num+2:
                if int(line[4]) < 70:
                    level_7_low.append(line)
                else:
                    level_7_high.append(line)

            elif int(line[3]) == level_num+3:
                if int(line[4])<70:
                    level_8_low.append(line)
                else:
                    level_8_high.append(line)

            elif int(line[3]) == level_num+4:
                if int(line[4])<70:
                    level_9_low.append(line)
                else:
                    level_9_high.append(line)

            elif int(line[3]) == level_num+5:
                if int(line[4]) < end_num:
                    level_10_low.append(line)
                else:
                    level_10_high.append(line)

            elif int(line[3]) > level_num+5:
                level_over.append(line)
        except:
            continue


sep_f_path = createpath(abs_path+'separate_csvfile/')
def write_each(filename, index):

    #to distingish between 3 classes. 'index' has to be divided by '2', get step's number 
    if now_class == '2':
        level = math.ceil(index/2) + 5    
    elif now_class == '3':
        level = math.ceil(index/2) + 10
    else:
        level = math.ceil(index/2)  

    #put different datas into target csv
    if index == 0:
        with open(sep_f_path+'bottom.csv','w') as filewrite:
            writer = csv.writer(filewrite)
            writer.writerows(filename)

    elif 11 > index > 0:    
        #divide the high process and the low
        if index % 2 == 0:
            with open(sep_f_path+'{}.csv'.format(str(level)+'_h'),'w') as filewrite:
                writer = csv.writer(filewrite)
                writer.writerows(filename)
        else:
            with open(sep_f_path+'{}.csv'.format(str(level)+'_l'),'w') as filewrite:
                writer = csv.writer(filewrite)
                writer.writerows(filename)

    else:
        with open(sep_f_path+'over.csv','w') as filewrite:
            writer = csv.writer(filewrite)
            writer.writerows(filename)


#'name_index' to count how long the queue line is, than we can be used to name a csv file
name_index = 0 
def get_task_ele():
    global name_index
    while not work2.empty():
        mylist = work2.get_nowait()
        write_each( mylist, name_index )
        name_index+=1

def create_json_task():         
    job_list = []
    for i in range(5):
        task = gevent.spawn(get_task_ele)
        job_list.append(task)

    gevent.joinall(job_list)
    print('All csv done!! Please check files in \'separate_csv\'\n')

def write_injson():
    #create a filename's list to collect all csvname, so don't put any meaningless file in this direction path
    filename_list = []
    #then filtrate  these csv file, get their name to use open(function). 
    for dir in os.listdir(sep_f_path):
        if '.csv' in dir:
            filename_list.append(dir)
        
    json_path = createpath(abs_path+'savejson/')
    for csvname in filename_list:
        #collect every filename and open it
        with open(sep_f_path + csvname) as read_f:
            reader = csv.reader(read_f)
            #to combine all {wxid} s with a whole string, for writing in a json file
            data = ''
            #wxid uses in collecting all students' wxid
            wxidlist = []
            for line in reader:
                wxidlist.append(line[1])
            #get each student's wxid and combine it in a string 
            for wxid in wxidlist:
                data+='{\"wxid\":'+' \"'+wxid+'\"'+'},'
            #this string has to be including in a [ ]
            data='['+data[:-1]+']'

        #write in, cut tail(4 bytes)
    
        with open(json_path + '{}.json'.format(csvname[:-4]), 'w') as f_wxid:
            f_wxid.write(data)
    print('All json files created successfully!!!')
            
def start_job():
    global standard_target,num,end_num,now_class
    now_class = get_class() 
    standard_target = now_class * 5
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
    add2list()
    create_json_task()
    write_injson()



if __name__ == "__main__":
    start_job()