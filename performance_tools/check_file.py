# !usr/bin/python
#-*-coding:utf8-*-

import os
import time
def count_file(folder_name):

    count = 0
    for fn in os.listdir(folder_name):  # fn 表示的是文件名
        count = count + 1
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),count)

while True:
    folder_name = '/home/ubuntu/data/face++/split_face_expand1.2_1.5'
    count_file(folder_name)
    time.sleep(4)