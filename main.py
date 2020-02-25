import sys
from urllib.error import HTTPError

import requests

import re
import os
import zlib
import pymysql
import json
import redis
from fake_useragent import UserAgent as UA
from urllib import request, parse
from videotools import DownVideo
from settings import *


class TTSSpider:
    def __init__(self,):
        self.all_url = 'http://tts.tmooc.cn/studentCenter/toMyttsPage'
        self.course_link_re = r'<ul class="course-link">(.*?)?</ul>'

    # def __get_cookie(self):
    #     url = UC_PATH_ + "/login"
    #     loginName = input("邮箱或手机")
    #     password = input("密码")
    #     accountType = log_type(loginName)
    #     password = encrypt(password)
    #     postdata = {
    #         "accountType": accountType,
    #         "password": password,
    #         "loginName": loginName
    #     }
    #     response = requests.post(url=url, data=postdata, headers=UA)
    #     cookie.txt = response.cookies
    #     return cookie.txt

    def __get_data(self, url, cookie):
        user_request_header = {"cookie": cookie}
        url = url
        query_data = bytes(parse.urlencode(user_query_dict), encoding="utf8")

        req = request.Request(url=url, data=query_data, headers=user_request_header, method="GET")
        response = request.urlopen(req)

        data = response.read()
        # data = zlib.decompress(data,16 + zlib.MAX_WBITS) # 内网加密
        data = data.decode()
        return data

    def __download_video(self, data, url, className, x):
        result = re.findall(r'id="active_(.+?\.m3u8)', data)
        title = re.findall(r'id="video_stage_lty">(.+?)</div>', data)
        result = set(result)
        for r in result:
            if not os.path.exists('video/' + className[0] + "/" + title[0]):
                os.makedirs('video/' + className[0] + "/" + title[0])
            # exit()
            a = DownVideo(url, r, 'video/' + className[0] + "/" + title[0] + '/' + r, className[0])
            a.run()
            print(r, 'download success')
        return title[0]

    def __get_urls(self, data):
        course_list = re.findall(self.course_link_re, data, re.S)
        # print(course_list)
        for i in course_list:
            try:
                video = re.findall('href="(.*)">视频', i)[0]
            except IndexError as I:
                video = ""
            try:
                course = re.findall('href="(.*)">PPT', i)[0]
            except IndexError as I:
                course = ""
            try:
                case = re.findall('href="(.*)">案例', i)[0]
            except IndexError as I:
                case = ""
            try:
                exercise = re.findall('href="(.*)">作业', i)[0]
            except IndexError as I:
                exercise = ""

            exercise = re.findall('href="(.*)">作业', i)
            yield {"video": video, "course": course, "case": case, "exercise": exercise}

    def run(self, cookie, className):
        first_data = self.__get_data(self.all_url, cookie)
        url_dict = self.__get_urls(first_data)
        while True:
            try:
                url = next(url_dict)
            except StopIteration as SI:
                sys.exit("尝试更换cookie!")
            while True:
                try:
                    res =re.findall("(menuId=.*?)&ver",url["video"])[0]+"\n"
                    f = open("downloadCache","a+")
                    f.seek(0,0)
                    D_list=f.readlines()
                    D_list=set(D_list)
                    if res in D_list:
                        print("already download!")
                        break

                    video_data = self.__get_data(url["video"], cookie)
                    a=self.__download_video(video_data, url["video"], className, int(className[1]))
                    print(a+"download success!")
                    f.seek(0,2)
                    f.write(res+"\n")
                    f.close()
                    break
                except Exception as e:
                    print(e)
                    break


def show():
    print("1.aid-python")
    print("2.big-大数据")
    print("3.cgb-Java互联网框架软件工程师")
    print("4.csd-C++国际软件工程师")
    print("5.esd-国际嵌入式软件工程师")
    print("6.jsd-Java企业级应用软件工程师")
    print("7.nsd-linux云计算")
    print("8.ntd-网络运维与网络安全")
    print("9.tsd-国际软件测试工程师")
    print("10.vrd-建模")
    print("11.web-网页设计")
    print("别忘记cookie.txt更换cookie")


def choose(classID):
    if classID == "1":
        classID = "AIDTN201908-6"
    elif classID == "2":
        classID = "BIGTN201907-6"
    elif classID == "3":
        classID = "CGB_A_V02-6"
    elif classID == "4":
        classID = "CSDTN201903-6"
    elif classID == "5":
        classID = "ESDTN201903-6"
    elif classID == "6":
        classID = "JSDTN201908-6"
    elif classID == "7":
        classID = "NSDTN201904-6"
    elif classID == "8":
        classID = "NTDTN201903-6"
    elif classID == "9":
        classID = "TSDTN201905-6"
    elif classID == "10":
        classID = "VRDTN201908-6"
    elif classID == "11":
        classID = "WEBTN201805-7"
    return classID.split("-")


if __name__ == "__main__":
    try:
        show()
        classId = input("课程编号:")
        className = choose(classId)
        with open("cookie.txt", "r") as f:
            str_co = f.read()
            cookie = str_co.strip()
        b = TTSSpider()
        b.run(cookie, className)
    except KeyboardInterrupt as KI:
        print("程序退出")
