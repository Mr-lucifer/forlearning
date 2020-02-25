import os
from urllib import request, parse
from urllib.error import HTTPError
import re
from Crypto.Cipher import AES
from settings import *


class DownVideo:
    def __init__(self, url, fileName: str, targetFileName: str, className: str):
        self.fileName = fileName[:-5]
        self.request_header = {
            'Origin': 'http://tts.tmooc.cn',
            'Referer': url,
            'User-Agent': useragent,
        }
        self.total_size = 0
        # self.url = 'http://videotts.it211.com.cn/'
        self.url = "http://c.it211.com.cn/"
        self.num = 0
        self.targetFileName = targetFileName
        self.className = className

    def run(self):
        # print(menuId, fileName, targetFileName)

        cipher = self.__get_static_key(self.fileName, self.request_header, self.url)

        self.__down_video(cipher)
        #

    def __down_video(self, cipher):
        if os.path.exists(self.targetFileName[:-5] + '.ts'):
            f = open(self.targetFileName[:-5] + '.ts', 'ab')
        else:
            f = open(self.targetFileName[:-5] + '.ts', 'wb')

        repeat = 0
        while True:
            try:
                url = 'http://c.it211.com.cn/' + self.fileName + '/' + self.fileName + '-' + str(self.num) + '.ts'
                # print(url)
                req = request.Request(url=url, data={}, headers=self.request_header, method="GET")
                response = request.urlopen(req)
                part_size = int(response.info()["Content-Length"])
                self.total_size += part_size
                size = os.path.getsize(self.targetFileName[:-5] + '.ts')

                if size>=self.total_size:
                    self.num += 1
                    continue
                lens=self.total_size-size
                data = response.read()
                res = part_size-lens
                f.write(cipher.decrypt(data[res:]))
                self.num += 1
            except HTTPError as e:
                if e.code == 501:
                    continue
                if e.code == 404:
                    if repeat < 3:
                        repeat += 1
                        continue
                    print(e)
                    repeat = 0
                    print(self.fileName, 'done')
                    break
        f.close()

    def __get_static_key(self, fileName, request_header, url):
        while True:
            try:
                # 获取static.key
                url_key = url + fileName + '/static.key'
                req_key = request.Request(url=url_key, data={}, headers=request_header, method="GET")
                response_key = request.urlopen(req_key)
                key = response_key.read()
                cipher = AES.new(key=key, mode=AES.MODE_CBC, IV=key)
                break
            except HTTPError as HT:
                if HT.code == 404:
                    print("视频不存在")
                    return

            except Exception as e:
                print('static key error')
                # print(e)
                continue
        return cipher

# if __name__ == '__main__':
# downVideoByMidFname('672192', 'aid19040429am.m3u8', 'video/aid19040429am/aid19040429am.m3u8')
