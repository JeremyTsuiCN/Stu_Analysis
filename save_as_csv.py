from gevent import monkey
monkey.patch_all()
from queue import Queue
import requests,json,csv,gevent,re

work = Queue()

#rail way workspace
first_url2 = 'https://prod.pandateacher.com/ninth-studio-future-railway/base-backend/conductor/chats/panels/10/modules?current_path=%2F%252Fpanel%252Fconductor'

proxy = {
'http': '117.94.182.64'
}


#update browser's headers
todayheaders='''Host: prod.pandateacher.com
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:72.0) Gecko/20100101 Firefox/72.0
Accept: application/json, text/plain, */*
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate, br
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdmF0YXIiOiJodHRwczovL2dpdC5mb3JjaGFuZ2UuY24vdXBsb2Fkcy8tL3N5c3RlbS91c2VyL2F2YXRhci80OTAvYXZhdGFyLnBuZyIsImV4cCI6MTU3OTE2MzkxOSwiaWF0IjoxNTc5MTU2NzE5LCJpc3MiOiJsd3JEekJhN1FEOGJ4OU8wSDF5N2lUT1R4ZGdQRE16YSIsIm5hbWUiOiLltJTkv4rmnbAiLCJzdWIiOjQ5MCwidW5hbWUiOiJjdWlqdW5qaWUifQ.sylpJsjqCeZPzqd8FbLU6EEOr2Dgnx09viFZO1Roiac
Connection: keep-alive
Referer: https://prod.pandateacher.com/ninth-studio-future-railway/frontend/
Cookie: sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22obmqi1Px1ozjOic9rMfYzI2fD87s%22%2C%22%24device_id%22%3A%2216dc975ec5afa-033c310891cf5a8-4a5b66-1764000-16dc975ec5b4aa%22%2C%22props%22%3A%7B%22%24latest_referrer%22%3A%22%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%2C%22first_id%22%3A%2216dc975ec5afa-033c310891cf5a8-4a5b66-1764000-16dc975ec5b4aa%22%7D; SERVERID=3847ab526202584eee1fed82128f885c|1579157019|1579156718; locale=zh-CN; prod-auth-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdmF0YXIiOiJodHRwczovL2dpdC5mb3JjaGFuZ2UuY24vdXBsb2Fkcy8tL3N5c3RlbS91c2VyL2F2YXRhci80OTAvYXZhdGFyLnBuZyIsImV4cCI6MTU3OTE2MzkxOSwiaWF0IjoxNTc5MTU2NzE5LCJpc3MiOiJsd3JEekJhN1FEOGJ4OU8wSDF5N2lUT1R4ZGdQRE16YSIsIm5hbWUiOiLltJTkv4rmnbAiLCJzdWIiOjQ5MCwidW5hbWUiOiJjdWlqdW5qaWUifQ.sylpJsjqCeZPzqd8FbLU6EEOr2Dgnx09viFZO1Roiac
TE: Trailers'''


headers = dict([line.split(": ", 1) for line in todayheaders.split("\n")])

res = requests.get(first_url2, headers = headers, proxies = proxy)


#change into dictionary
data_js = json.loads(res.text)

#collect data I need(only wxid)
try:
    get_allstu_group = data_js['data']['lists'][1]['lists']
except:
    print('Headers had updated, please copy a new one and run again!!')
    exit()
# collect students that have not learned today, or before. Save as a csv file prepare for create a json list
#before we write in folder, set a absolute path first

abs_path = '/Users/apple/Desktop/op_savecsv/'

postufile = open(abs_path + 'complete_data.csv', 'w', newline = '', encoding = 'utf-8-sig')
writer = csv.writer(postufile)
writer.writerow(['nickname', 'wxid', 'details', 'level', 'progress', 'learning status'])




#create a url that can get each student's data. Then put it into a task
for studata in get_allstu_group:
    wxid = studata['wxid']
    #url = 'https://prod.pandateacher.com/ninth-studio-future-railway/base-backend/conductor/buddy/wxid_d4vx8gec8whv22/dc06090326?current_path=%2Fpanel%2Fconductor&is_group=false'
    status_url = 'https://prod.pandateacher.com/ninth-studio-future-railway/base-backend/conductor/buddy/wxid_d4vx8gec8whv22/{}?current_path=%2Fpanel%2Fconductor&is_group=false'.format(wxid)
    work.put_nowait(status_url)

#wanna print schedule, so I need this num to check presentage
num = len(get_allstu_group)
COUNT_INDEX = 0

#some students need personal conversation
private_stu = []

# special_word = input('keywords in special students\' name that need private conversation')
keyword = ['忙忙', '考试', '妈妈', '放弃', '特殊','请假', '周一', '周二', '周三', '周四', '周五', '周六', '周日', '周末','不回复', '明天'] 


#increase COUNT_INDEX for showing schedule in console log.  
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
        if list( filter(lambda x: x in nickname,keyword) ):
            private_stu.append([nickname, weixin, progress, level, distance])
            
        else:
            writer.writerow([nickname, weixin, progress, level, distance])
            

        print("\b"*30,end="",flush=True)
        print('sum: {}, process: {:.1f}%'.format(num,100*(COUNT_INDEX/num) ), end="")
        

task_list = []


for i in range(5):
    task = gevent.spawn(crawler)
    task_list.append(task)

gevent.joinall(task_list)


print('\n general students csv done！！')
postufile.close()


if private_stu:
    with open(abs_path + 'per_con.csv', 'w', newline='') as perfile:
        writer = csv.writer(perfile)
        writer.writerows(private_stu)

    print('Special students done！！')
else:
    print('empty special student list')


#check miss students
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

