#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import urllib
import json
import socket
import urllib.request
import urllib.parse
import urllib.error
# 设置超时
import time
import pymysql.cursors
import thumbnail

TIMEOUT = 5
SAVE_PATH = "wallpaper/"
socket.setdefaulttimeout(TIMEOUT)
CONNECT = pymysql.Connect(
    host='172.104.181.57',
    port=4306,
    user='root',
    passwd='3x7jE9m4',
    db='wallpaper',
    charset='utf8'

    # host='localhost',
    # port=3306,
    # user='root',
    # passwd='123456',
    # db='wallpaper',
    # charset='utf8'
)
CURSOR = CONNECT.cursor()
# 图片分类
TAG = ""
TAG_NUMER = ""


class Crawler:
    # 睡眠时长
    __time_sleep = 0.1
    __amount = 0
    __start_amount = 0
    __counter = 0
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}

    def insert_into_db(self, pic_path, pic_name, pic_status):
        pic_path = pic_path.replace("\\", "\\\\")
        sql = "INSERT INTO picture (pic_path, pic_name, pic_status, pic_tag) VALUES ('%s', '%s', '%s' ,'%s' )"
        data = (pic_path, pic_name, pic_status, TAG)
        CURSOR.execute(sql % data)
        CONNECT.commit()
        print('成功插入', CURSOR.rowcount, '条数据')

    # 获取图片url内容等
    # t 下载图片时间间隔
    def __init__(self, t=0.1):
        self.time_sleep = t

    # 获取后缀名
    def get_suffix(self, name):
        m = re.search(r'\.[^\.]*$', name)
        if m.group(0) and len(m.group(0)) <= 5:
            return m.group(0)
        else:
            return '.jpeg'

    # 获取referrer，用于生成referrer
    def get_referrer(self, url):
        par = urllib.parse.urlparse(url)
        if par.scheme:
            return par.scheme + '://' + par.netloc
        else:
            return par.netloc

        # 保存图片

    def save_image(self, rsp_data):
        save_path = SAVE_PATH + TAG + "/"
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        # 判断名字是否重复，获取图片长度
        self.__counter = len(os.listdir(save_path)) + 1
        for image_info in rsp_data['imgs']:

            try:
                time.sleep(self.time_sleep)
                suffix = str(self.get_suffix(image_info['objURL']))
                # 指定UA和referrer，减少403
                refer = self.get_referrer(image_info['objURL'])
                opener = urllib.request.build_opener()
                opener.addheaders = [
                    ('User-agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0'),
                    ('Referer', refer)
                ]
                urllib.request.install_opener(opener)
                # 保存图片
                if suffix == ".jpeg":
                    file_name = str(self.__counter) + ".jpg"
                else:
                    if not suffix == ".jpg":
                        continue
                    else:
                        file_name = str(self.__counter) + suffix
                # print(suffix)
                urllib.request.urlretrieve(image_info['objURL'], save_path + file_name)
                absolute_path = os.path.abspath(save_path + file_name)
                print(absolute_path)
                self.insert_into_db(absolute_path, file_name, '0')
            except urllib.error.HTTPError as urllib_err:
                print(urllib_err)
                continue
            except Exception as err:
                time.sleep(1)
                print(err)
                print("产生未知错误，放弃保存")
                continue
            else:
                print("壁纸+1,已有" + str(self.__counter) + "张壁纸")
                self.__counter += 1
        return

    # 开始获取
    def get_images(self, word='美女'):
        search = urllib.parse.quote(word)
        # pn int 图片数
        pn = self.__start_amount
        while pn < self.__amount:

            url = 'http://image.baidu.com/search/avatarjson?tn=resultjsonavatarnew&ie=utf-8&word=' + search + '&cg=girl&pn=' + str(
                pn) + '&rn=60&itg=0&z=0&fr=&width=1080&height=1920&lm=-1&ic=0&s=0&st=-1&gsm=1e0000001e'
            # 设置header防ban
            try:
                time.sleep(self.time_sleep)
                req = urllib.request.Request(url=url, headers=self.headers)
                page = urllib.request.urlopen(req)
                rsp = page.read().decode('unicode_escape')
            except UnicodeDecodeError as e:
                print(e)
                print('-----UnicodeDecodeErrorurl:', url)
            except urllib.error.URLError as e:
                print(e)
                print("-----urlErrorurl:", url)
            except socket.timeout as e:
                print(e)
                print("-----socket timout:", url)
            else:
                # 解析json
                rsp_data = json.loads(rsp)
                self.save_image(rsp_data)
                # 读取下一页
                print("下载下一页")
                pn += 60
            finally:
                page.close()
        print("下载任务结束")
        return

    def start(self, word, spider_page_num=1, start_page=1):
        """
        爬虫入口
        :param word: 抓取的关键词
        :param spider_page_num: 需要抓取数据页数 总抓取图片数量为 页数x60
        :param start_page:起始页数
        :return:
        """
        self.__start_amount = (start_page - 1) * 60
        self.__amount = spider_page_num * 60 + self.__start_amount
        self.get_images(word)


if __name__ == '__main__':
    print('*************开始爬取壁纸*************')
    crawler = Crawler(0.05)  # 抓取延迟为 0.05
    # 查询获取分类
    sql = "SELECT tag_id, tag_name, tag_number, tag_pinyin FROM tag"
    CURSOR.execute(sql)
    result = CURSOR.fetchall()
    for row in result:
        tid = row[0]
        tname = row[1]
        tnumber = row[2]
        TAG = row[3]
        crawler.start("手机壁纸 " + TAG, 5, 1)
    CURSOR.close()
    CONNECT.close()
    thumbnail.thumbnail_pic('wallpaper/')
    # crawler.start('手机壁纸', 10, 1)  # 抓取关键词为 “二次元 美女”，总数为 10 页（即总共 10*60=600 张），起始抓取的页码为 1
    # crawler.start('帅哥', 5)  # 抓取关键词为 “帅哥”，总数为 5 页（即总共 5*60=300 张）
