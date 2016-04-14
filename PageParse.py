#!/usr/bin/python3
# -*-utf-8-*-

import urllib.parse
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
import os

from spider import Request
from spider import Spider

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
        hashList = soup.find_all(text=re.compile("hash"))
        if len( hashList )!=0:
            name = strip_dir_name(self.title)
            dir = os.path.join("./source", name)
            if not os.path.exists(dir):
                os.makedirs(dir)
                print("%s ==============>创建目录！"%(name))

            #parse torrent url
            #torrentPath = os.path.join(dir, "1.torrent")
            #if not os.path.exists(torrentPath):
            #    print torrentPath

            #parse picture url
            jpg_list = soup.find_all(src=re.compile("\.jpg"))
            for i in range(PICTURE_NUM):
                pic_path = os.path.join(dir, "%d.jpg"%i)
                print(pic_path)
                if not os.path.exists(pic_path):
                    FileDownload(self.spider, jpg_list[i]['src'], pic_path)

#class TorrentDownload(Request):
#    def __init__(self, spider, url, path, param):

class FileDownload(Request):
    def __init__(self, spider, url, path):
        self.path = path
        Request.__init__(self, spider, url, content_type="binary")

    def handle_func(self, content):
        with open(self.path, "wb") as f:
            f.write(content)
            print("%s============>下载完成!"%(self.path))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    spider = Spider(page_num=5, max_tries=30, max_tasks=5, rootDir='./source')
    request = IndexPageRequest(spider, CL_URL%2)
    loop.run_until_complete(spider.spider())
    spider.close()
    loop.stop()
    loop.run_forever()
    loop.close()

