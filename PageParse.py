#!/usr/bin/python3
# -*-utf-8-*-

import urllib.parse
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
import os

from Spider import Request
from Spider import Spider

PICTURE_NUM = 2
CL_URL = "http://cl.bearhk.info/thread0806.php?fid=15&search=&page=%s"

#delete '\' and '/' in dir name string
def strip_dir_name(dir):
    str = '-'.join('-'.join(dir.split('\\')).split('/'))
    return '-'.join(str.split())


class IndexPageRequest(Request):
    def handle_func(self, content):
        """ parse index page, return main page urls set"""
        #links = set()
        """BeautifulSoup parse index page, get urls and titles"""
        soup = BeautifulSoup(content, 'lxml')
        for a in soup.find_all(href=re.compile("htm_data")):
            if a.find_parent().name=="h3":
                normalized = urllib.parse.urljoin(self.url, a['href'])
                defragmented, frag = urllib.parse.urldefrag(normalized)
                print(defragmented)
                print(a.string)

                request = MainPageRequest(self.spider, defragmented, a.string)
        return 0


class MainPageRequest(Request):
    def __init__(self, spider, url, title):
        self.title =title
        Request.__init__(self, spider, url)

    def handle_func(self, content):
        #print(content)
        soup = BeautifulSoup(content, 'lxml')
        hash_list = soup.find_all(text=re.compile("hash"))
        if len( hash_list )!=0:
            name = strip_dir_name(self.title)
            dir = os.path.join("./", name)
            if not os.path.exists(dir):
                os.makedirs(dir)
                print("%s ==============>创建目录！"%(name))

            #parse torrent url
            torrentPath = os.path.join(dir, "1.torrent")
            if not os.path.exists(torrentPath):
                print(torrentPath)
                TorrentDownload(self.spider, hash_list[0], torrentPath)

            #parse picture url
            jpg_list = soup.find_all(src=re.compile("\.jpg"))

            round_times = PICTURE_NUM
            if len(jpg_list) < PICTURE_NUM:
                round_times = len(jpg_list)

            for i in range(round_times):
                pic_path = os.path.join(dir, "%d.jpg"%i)
                print(pic_path)
                if not os.path.exists(pic_path) and jpg_list[i].has_key('src'):
                    FileDownload(self.spider, jpg_list[i]['src'], pic_path)

class TorrentDownload(Request):
    def __init__(self, spider, url, path, params=None):
        self.path = path
        Request.__init__(self, spider=spider, url=url)

    def handle_func(self,content):
        downloadUrl = urllib.parse.urljoin(self.url, 'download.php');
        soup = BeautifulSoup(content, 'lxml')
        inputList = soup.find_all('input')
        params = {}
        for i in inputList:
            params[i['name']]=i['value']

        FileDownload(spider=self.spider, url=downloadUrl, path=self.path, params=params)


class FileDownload(Request):
    def __init__(self, spider, url, path, params=None):
        self.path = path
        Request.__init__(self, spider=spider, url=url, params=params, content_type="binary")

    def handle_func(self, content):
        with open(self.path, "wb") as f:
            f.write(content)
            print("%s============>下载完成!"%(self.path))


def start(spider, start_page=1, end_page=2, root_dir="./"):
    print("enter %s"%root_dir)
    os.chdir(root_dir)
    for i in range(start_page, end_page)[::-1]:
        request = IndexPageRequest(spider, CL_URL%i)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    spider = Spider(page_num=5, max_tries=30, max_tasks=20, rootDir='./source')
    request = IndexPageRequest(spider, CL_URL%1)
    loop.run_until_complete(spider.spider())
    spider.close()
    loop.stop()
    loop.run_forever()
    loop.close()

