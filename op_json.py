from gevent import monkey
monkey.patch_all()
from queue import Queue
import json,csv,gevent,math


with open(r'/Users/apple/Desktop/day2/now03.csv') as fulldata:
    data = fulldata.readlines()


now_class = input('请输入目前阶段: 1、山脚   2、山腰   3、山顶  \n')
def write_each(filename,index):
    #so quick that we can't see this content....
    print('第{}个文件写入中'.format(index+1),end="")
    print("\b"*20,end="",flush=True)

    #set a step to distingish between different levels 
    if now_class == '2':
        level = math.ceil(index/2) + 5    
    elif now_class == '3':
        level = math.ceil(index/2) + 10
    else:
        level = index  
            
    #put different data into target csv
    if index == 0:
        with open(r'/Users/apple/Desktop/output/bottom.csv','w') as filewrite:
            writer = csv.writer(filewrite)
            writer.writerows(filename)

    elif 11 > index > 0:    

        if index % 2 == 0:
            with open(r'/Users/apple/Desktop/output/{}.csv'.format(str(level)+'_h'),'w') as filewrite:
                writer = csv.writer(filewrite)
                writer.writerows(filename)
        else:
            with open(r'/Users/apple/Desktop/output/{}.csv'.format(str(level)+'_l'),'w') as filewrite:
                writer = csv.writer(filewrite)
                writer.writerows(filename)

    else:
        with open(r'/Users/apple/Desktop/output/over.csv','w') as filewrite:
                writer = csv.writer(filewrite)
                writer.writerows(filename)


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



#read csv's data by line, distinguish, then add to target list
def add2list(select_num):
    level_num = (int(select_num)-1)*5
    for eachline in data:
        line = eachline.split(',')
        try:
            if int(line[3]) == level_num:
                level_5.append(line)

            elif int(line[3]) == level_num+1:
                if int(line[4]) < 60:
                    level_6_low.append(line)
                else:
                    level_6_high.append(line)

            elif int(line[3]) == level_num+2:
                if int(line[4]) < 60:
                    level_7_low.append(line)
                else:
                    level_7_high.append(line)

            elif int(line[3]) == level_num+3:
                if int(line[4])<60:
                    level_8_low.append(line)
                else:
                    level_8_high.append(line)

            elif int(line[3]) == level_num+4:
                if int(line[4])<60:
                    level_9_low.append(line)
                else:
                    level_9_high.append(line)

            elif int(line[3]) == level_num+5:
                if int(line[4]) < 60:
                    level_10_low.append(line)
                else:
                    level_10_high.append(line)

            elif int(line[3]) > level_num+6:
                level_over.append(line)
        except:
            continue

add2list(now_class)


#create a main list to save every level's list
all_list = [level_5,level_6_low ,level_6_high,level_7_low,level_7_high,level_8_low,level_8_high,level_9_low,level_9_high,level_10_low,level_10_high,level_over]

work = Queue()

#put these little list into queue
for all in all_list:
    work.put_nowait(all)

#create a 'n' to count how long the queue line is, than we can use 'n' to name a csv file
n = 0 
def get_task_ele():
    global n
    while not work.empty():
        mylist = work.get_nowait()
        write_each( mylist, n )
        n+=1
        
    

job_list = []

for i in range(5):
    task = gevent.spawn(get_task_ele)
    job_list.append(task)


gevent.joinall(job_list)
print('文件生成成功，请打开文件夹检查')