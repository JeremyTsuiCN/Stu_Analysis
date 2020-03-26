#!/usr/bin/env python3
# _*_ coding: utf-8  _*_

'Oh my god!!! To Bro Night'

__author__ = 'Jeremy Tsui'

import os, shutil

# 本设计功能介绍：
# 淘宝美工需要把 修过的图（jpg格式）不保留地覆盖 原图（CR2格式），前后两种图片同名

# 要点：CR2原图来自于多个文件夹（不同系列），修过的图倒是无序的，直接覆盖原图即可

# 原理：遍历修过的图并统计所有文件名，并同时遍历多个文件夹且遍历多个文件然后统计所有文件名
# 当新图的文件名与原图文件名相同，则找出原图并删除，再将新图传进相应的原图文件夹中

# 硬性要求，目录结构，所有的图用文件夹放在一个汇总的目录里头，一定要符合:   
# mainpath > newpicdir > n * eachdir > all files  
# mainpath > oldpicdir > n * eachdir > all files


#统计有多少个次级文件夹
def openDirs(my_path):
    os.chdir(my_path)
    main_files = [i for i in os.listdir(my_path)]
    return filter(os.path.isdir, [os.path.join(os.getcwd(),filename) for filename in main_files])

#返回次级文件夹中的所有文件
# collectFiles = lambda x: os.listdir(x)

#遍历次级文件夹，再遍历文件所属的目标文件夹，统计所有文件名
def takeOffList(dir_lists):
    mylist = [] 
    for listdir in dir_lists:
        for dir in os.listdir(listdir):
            mylist.append(dir)
    return mylist

#移除旧文件&移动新文件
def rmOldFile(newfile, newpath, oldfile, dirnamelist):
    for dirname in dirnamelist:
        try:
            del_file = os.path.join(dirname, oldfile)
            os.remove(del_file)
            print(oldfile + '被替换')
            move_file = os.path.join(newpath, newfile)
            shutil.move(move_file, dirname)
            return
        except:
            pass
    

if __name__ == "__main__":
    #新旧两个文件目录还是要画出来区分的，不然单纯遍历上一级目录的话，顺序自己心里没底
    old_path = '/Users/apple/Desktop/myip'
    new_path = '/Users/apple/Desktop/op_savecsv'

    #次级文件夹，装在列表里
    old_subdirs = [i for i in openDirs(old_path)]
    new_subdirs = [i for i in openDirs(new_path)]

    #所有次级文件夹里的所有文件，新文件只有一个次级文件夹,用0访问
    oldname_list = takeOffList(old_subdirs)
    newname_list = takeOffList(new_subdirs)
    new_subdir = new_subdirs[0]

    for newname in newname_list:
        # 当条件吻合
        purename = newname[:-3] + 'CR2'
        if purename in oldname_list:
            # 文件移动move：参数需要文件名和其路径。 参数位置 0，1
            # 文件删除：需要其文件名。参数位置2
            # 而路径，因为之前只为对比文件名而只统计了原图的文件名，并没有保留文件名所对应的路径。
            # 所以把有可能的路径，即需要遍历次级路径作为参数3传入
            rmOldFile(newname, new_subdir, purename, old_subdirs)




