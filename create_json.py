import os,csv

filename_list = []
for dir in os.listdir('/Users/apple/Desktop/output'):
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

for csvfile in filename_list:
    with open('/Users/apple/Desktop/output/{}'.format(csvfile)) as read_f:
        reader = csv.reader(read_f)
        data = ''
        wxidlist = []
        for line in reader:
            wxidlist.append(line[1])
        
        for wxid in wxidlist:
            data+='{\"wxid\":'+' \"'+wxid+'\"'+'},'
        data='['+data[:-1]+']'

        with open('/Users/apple/Desktop/output/savejson/{}.json'.format(csvfile[:-4]), 'w') as f_wxid:
            f_wxid.write(data)