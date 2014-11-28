#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple spider named bearSpider
Requiring only Python and no other preconditions.
bearSpider is started by running this script with argument as follows:
-h --help           Open help
-n --thread_number  Thread number, the default is single
-o --output         Output path, the default is pics directory under current dir
-l --img_number     Download images number, the default is 10
"""

import sys, os
import getopt
import urllib2
import re
import thread, threading
import time

class bearSpider():
    def __init__(self):
        self.img_info_list = []
        self.img_id = 1
        self.download_img_number = 0
        self.enable = False
        self.lock = thread.allocate_lock()

    def LoadPage(self, img_number):
        url = "http://www.topit.me/"
        # 初始化页面和图片的id
        page_id = 1
        img_id = 1
        while len(self.img_info_list) < img_number:
            page_content = urllib2.urlopen(url+"?p="+str(page_id)).read().decode('utf-8')
            # topit上img标签有两种格式，一种地址在src中，一种地址在data-original中。
            page_items = re.findall('<img(.*?)id="item_d_(\d+?)".*?alt="(.*?)".*?src="(.*?)".*?>', page_content, re.S)
            for item in page_items:
                img_name = str(item[1])+"."+item[3].split('.')[-1]
                if item[3].split('/')[-1] == "blank.gif":
                    img_url = re.search('data-original="(.*?)"', item[0]).group(1)
                else:
                    img_url = item[3]
                img_info = [img_name, img_url]
                if len(self.img_info_list) < img_number:
                    self.img_info_list.append(img_info)
                    # print u"第%d页第%d条" % (page_id, img_id)+"img name:"+img_name
                    # print img_url
                else:
                    break
                img_id += 1
            page_id += 1

    def DownloadImg(self, img_number, output, tread_name):
        while self.img_id <= img_number and self.enable:
            self.lock.acquire()            # 上锁
            img_id = self.img_id
            self.img_id += 1
            self.lock.release()            # 解锁
            img_info = self.img_info_list[img_id-1]
            img_name = img_info[0]
            img_url = img_info[1]
            # 目录不存在时需先创建
            if os.path.exists(output) == False:
                os.makedirs(output)
            # 写入二进制文件
            try:
                img = urllib2.urlopen(img_url).read()
                f = open(output+"/"+img_name, 'wb')
                f.write(img)
                f.close()
                print tread_name+": download image_"+str(img_id)+" successfully!"
                self.download_img_number += 1
            except:
                print tread_name+": download image_"+str(img_id)+" failed!"
        self.enable = False

    def Start(self, thread_number, output, img_number):
        self.enable = True
        # 加载页面内容，将解析到的图片地址存入数组
        self.LoadPage(img_number)
        # 根据数组中的图片地址下载图片
        print u'Start downloading, output to:'+output
        for i in range(0, thread_number):
            if self.enable:
                thread.start_new_thread(self.DownloadImg, (img_number, output, "bearSpider-"+str(i+1)))
                time.sleep(1)
            else:
                break
		# 主线程等待时间
        time.sleep(60)
        print "All Over!You have download", self.download_img_number, "images under", output, "directory."

    def help(self):
        print __doc__
		
    def usage(self):
        print "Invalid input!\nHelp are as fallows:"
        print __doc__


if __name__ == '__main__':
    bearSpider = bearSpider()
    argv = sys.argv[1:]

    # 初始化命令行参数
    thread_number = 10
    output = './pics/'
    img_number = 100
    # 获取输入的命令行参数,若输入不符合规则则打印usage信息
    if argv and not re.match('-.*?', argv[0]):
        bearSpider.usage()
        sys.exit(2)	
    try:
        opts, args = getopt.getopt(argv, "hn:o:l:", ["help", "thread_number=", "output=", "img_number="])
    except getopt.GetoptError:
        bearSpider.usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            bearSpider.help()
            sys.exit()
        elif opt in ("-n", "--thread_number"):
            thread_number = int(arg)
        elif opt in ("-o", "--output"):
            output = arg.replace("'", "").replace("\"", "")
        elif opt in ("-l", "--img_number"):
            img_number = int(arg)

    bearSpider.Start(thread_number, output, img_number)