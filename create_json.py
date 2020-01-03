import os,csv

#create a filename's list to collect all csvfile, so don't put any meaningless file in this direction path
filename_list = []

#then filtrate  these csv file, get their name to use open(function). 

csv_files_path = '/Users/apple/Desktop/output/'
for dir in os.listdir(csv_files_path):
    if '.csv' in dir:
        filename_list.append(dir)


# data=''
# wxidlist = []
# for csvfile in filename_list:
#     with open('/Users/apple/Desktop/{}'.format(csvfile)) as read_f:
#         reader = csv.reader(read_f)
#         for line in reader:
#             wxidlist.append(line[1])
# for wxid in wxidlist:
#     data+='{\"wxid\":'+' \"'+wxid+'\"'+'},'
# data='['+data[:-1]+']'
# with open('/Users/apple/Desktop/output/line12.json', 'w') as f_wxid:
#     f_wxid.write(data)
#this code's function is for creating a single json file, so we need a new code to create all kind of file, for one time



#here to get each csv's name, then open it and read each file's data 
for csvfile in filename_list:
    #get every filename and open it
    with open(csv_files_path + csvfile) as read_f:
        reader = csv.reader(read_f)
        #sign a string object to combine all wxid with a whole string, for writing in a json file
        data = ''
        #wxid uses in collecting all students' wxid
        wxidlist = []
        for line in reader:
            wxidlist.append(line[1])
        #so we can get each student's wxid an combine it in a string 
        for wxid in wxidlist:
            data+='{\"wxid\":'+' \"'+wxid+'\"'+'},'
        #this string has to be including in a [ ]
        data='['+data[:-1]+']'

        #write in 
        with open(csv_files_path+'/savejson/{}.json'.format(csvfile[:-4]), 'w') as f_wxid:
            f_wxid.write(data)