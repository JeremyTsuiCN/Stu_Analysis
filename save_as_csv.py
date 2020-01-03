from gevent import monkey
monkey.patch_all()
from queue import Queue
import requests,json,csv,gevent,re

work = Queue()

#get this request url
first_url = 'https://prod.pandateacher.com/ninth-studio-future-railway/base-backend/conductor/chats/panels/10/modules?current_path=%2Fpanel%2Fconductor'

#need a proxy agent
proxy = {
'http': '117.94.182.64'
}


#update browser's headers
todayheaders='''Host: prod.pandateacher.com
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:71.0) Gecko/20100101 Firefox/71.0
Accept: application/json, text/plain, */*
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate, br
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdmF0YXIiOiJodHRwczovL2dpdC5mb3JjaGFuZ2UuY24vdXBsb2Fkcy8tL3N5c3RlbS91c2VyL2F2YXRhci80OTAvYXZhdGFyLnBuZyIsImV4cCI6MTU3ODAzOTE3NiwiaWF0IjoxNTc4MDMxOTc2LCJpc3MiOiJsd3JEekJhN1FEOGJ4OU8wSDF5N2lUT1R4ZGdQRE16YSIsIm5hbWUiOiLltJTkv4rmnbAiLCJzdWIiOjQ5MCwidW5hbWUiOiJjdWlqdW5qaWUifQ.-qOeZKqQg2jQH5NCca9w2UYcxSEaWrFw0RXiM56TGls
Connection: keep-alive
Referer: https://prod.pandateacher.com/ninth-studio-future-railway/frontend/
Cookie: sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22490%22%2C%22%24device_id%22%3A%2216dc975ec5afa-033c310891cf5a8-4a5b66-1764000-16dc975ec5b4aa%22%2C%22props%22%3A%7B%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%2C%22first_id%22%3A%2216dc975ec5afa-033c310891cf5a8-4a5b66-1764000-16dc975ec5b4aa%22%7D; SERVERID=3847ab526202584eee1fed82128f885c|1578036437|1578017516; locale=zh-CN; prod-auth-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdmF0YXIiOiJodHRwczovL2dpdC5mb3JjaGFuZ2UuY24vdXBsb2Fkcy8tL3N5c3RlbS91c2VyL2F2YXRhci80OTAvYXZhdGFyLnBuZyIsImV4cCI6MTU3ODAzOTE3NiwiaWF0IjoxNTc4MDMxOTc2LCJpc3MiOiJsd3JEekJhN1FEOGJ4OU8wSDF5N2lUT1R4ZGdQRE16YSIsIm5hbWUiOiLltJTkv4rmnbAiLCJzdWIiOjQ5MCwidW5hbWUiOiJjdWlqdW5qaWUifQ.-qOeZKqQg2jQH5NCca9w2UYcxSEaWrFw0RXiM56TGls
TE: Trailers'''

#generate a headers
headers = dict([line.split(": ",1) for line in todayheaders.split("\n")])

#send requests then get reponse
res = requests.get(first_url,headers=headers,proxies=proxy)



#change into dictionary
data_js = json.loads(res.text)

#collect data I need(only wxid)

try:
    get_allstu_group = data_js['data']['lists'][1]['lists']
except:
    print('Headers已经更新，请重新复制，再重新运行！')
    exit()
# collect students that have not learned today, or before. Save as a csv file prepare for create a json list
postufile = open(r'/Users/apple/Desktop/day2/now03.csv', 'w', newline='',encoding='utf-8-sig')
writer = csv.writer(postufile)
writer.writerow(['nickname', 'wxid', 'details', 'level', 'progress'])




#create a url that can get each student's data. Then put it into a task
for studata in get_allstu_group:
    wxid = studata['wxid']
    status_url = 'https://prod.pandateacher.com/ninth-studio-future-railway/base-backend/conductor/buddy/wxid_th5yqnhdcvzc22/{}?current_path=%2Fpanel%2Fconductor&is_group=false'.format(wxid)
    work.put_nowait(status_url)


#wanna print schedule, so I need this num to check presentage
num = len(get_allstu_group)
COUNT_INDEX = 0

#some students need personal conversation, so I make a list
private_stu = []


special_word = input('哪些关键字学生需要私聊？？')

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
        if special_word not in nickname:
            writer.writerow([nickname, weixin, progress, level, distance])
            
        else:
            private_stu.append([nickname, weixin, progress, level, distance])

        print("\b"*30,end="",flush=True)
        print('{}条数据，写入进度:{:.1f}%'.format(num,100*(COUNT_INDEX/num) ), end="")
        

task_list = []


for i in range(5):
    task = gevent.spawn(crawler)
    task_list.append(task)

gevent.joinall(task_list)


print('写入群发人员名单成功！！')
postufile.close()

with open(r'/Users/apple/Desktop/output/per_con.csv', 'w', newline='') as perfile:
    writer = csv.writer(perfile)
    writer.writerows(private_stu)

print('写私聊人员名单成功！！准备处理下一步：分隔不同阶段的同学情况')