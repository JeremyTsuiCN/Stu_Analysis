from gevent import monkey
monkey.patch_all()
from queue import Queue
import json,csv,gevent,math,os

abs_path = '/Users/apple/Desktop/op_savecsv/'
with open(abs_path+'complete_data.csv') as fulldata:
    data = fulldata.readlines()



while True:
    now_class = input('which class? please input number\n 1、山脚   2、山腰   3、山顶  \n')
    if now_class in ['1','2','3']:
        break


def write_each(filename,index):
    #so quick that we can't see this content....
    print('第{}个文件写入中'.format(index+1),end="")
    print("\b"*20,end="",flush=True)

    #to distingish between 3 classes. 'index' has to be divided by '2', get high step's number and low's at line 37 condition
    if now_class == '2':
        level = math.ceil(index/2) + 5    
    elif now_class == '3':
        level = math.ceil(index/2) + 10
    else:
        level = math.ceil(index/2)  
            
    #put different datas into target csv
    if index == 0:
        with open(abs_path + 'separate_csv/bottom.csv','w') as filewrite:
            writer = csv.writer(filewrite)
            writer.writerows(filename)

    elif 11 > index > 0:    
        #divide the high process and the low
        if index % 2 == 0:
            with open(abs_path + 'separate_csv/{}.csv'.format(str(level)+'_h'),'w') as filewrite:
                writer = csv.writer(filewrite)
                writer.writerows(filename)
        else:
            with open(abs_path + 'separate_csv/{}.csv'.format(str(level)+'_l'),'w') as filewrite:
                writer = csv.writer(filewrite)
                writer.writerows(filename)

    else:
        with open(abs_path + 'separate_csv/over.csv','w') as filewrite:
                writer = csv.writer(filewrite)
                writer.writerows(filename)

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


#create a main list to save all groups
all_list = [level_5,level_6_low ,level_6_high,level_7_low,level_7_high,level_8_low,level_8_high,level_9_low,level_9_high,level_10_low,level_10_high,level_over]

work = Queue()

#put these groups into queue
for all in all_list:
    work.put_nowait(all)

#create a 'n' to count how long the queue line is, than we can use 'n' to name a csv file
n = 0 
def get_task_ele():
    global n
    while not work.empty():
        mylist = work.get_nowait()
        # call at line 18
        write_each( mylist, n )
        n+=1
        
    

job_list = []

for i in range(5):
    task = gevent.spawn(get_task_ele)
    job_list.append(task)


gevent.joinall(job_list)
print('done!! Please check files in \'separate_csv\'')

#+++++++++++++++++new file here++++++++++++++

#create a filename's list to collect all csvname, so don't put any meaningless file in this direction path
filename_list = []

#then filtrate  these csv file, get their name to use open(function). 

csv_files_path = abs_path + '/separate_csv/'
for dir in os.listdir(csv_files_path):
    if '.csv' in dir:
        filename_list.append(dir)
    

for csvname in filename_list:
    #collect every filename and open it
    with open(csv_files_path + csvname) as read_f:
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
        with open(abs_path + '/savejson/{}.json'.format(csvname[:-4]), 'w') as f_wxid:
            f_wxid.write(data)