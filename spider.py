#!/usr/bin/python3
# -*-utf-8 -*-

import urllib.parse
import asyncio
import aiohttp
try:
    from asyncio import JoinableQueue as Queue
except ImportError:
    from asyncio import Queue

from bs4 import BeautifulSoup

import re
import os

class Spider:
    def __init__(self, max_tries=30, max_tasks=50, picture_num=2
                 , rootDir=os.getcwd()):
        self.max_tries = max_tries
        self.max_tasks = max_tasks
        self.picture_num = picture_num
        self.loop = asyncio.get_event_loop()
        self.q = Queue(loop=self.loop)
        self.session = aiohttp.ClientSession(loop=self.loop)
        url = "http://cl.bearhk.info/thread0806.php?fid=15&search=&page=1"
        self.q.put_nowait((url, self.parse_index, None))
        self.rootDir = rootDir


    def close(self):
        self.session.close()

    #delete '\' and '/' in dir name string
    def _strip_dir_name(self, dir):
        str = ''.join(''.join(dir.split('\\')).split('/'))
        return '_'.join(str.split())

    @asyncio.coroutine
    def parse_index(self, response, *arg):
        """ parse index page, return main page urls set"""
        links = set()
        if response.status == 200:
            content_type = response.headers.get('content-type')
            if content_type in ('text/html', 'application/xml'):
                text = yield from response.text(encoding='GBK')

                """BeautifulSoup parse index page, get urls and titles"""
                soup = BeautifulSoup(text, 'lxml')
                for a in soup.find_all(href=re.compile("htm_data"))[4:]:
                    if a.find_parent().name=="h3":
                        normalized = urllib.parse.urljoin(response.url, a['href'])
                        defragmented, frag = urllib.parse.urldefrag(normalized)
                        print(defragmented)
                        print(a.string)
                        self.q.put_nowait((defragmented, self.parse_main, a.string))

    @asyncio.coroutine
    def parse_main(self, response, *arg):
        """parse main page, get picture url and download torrent page url"""
        if response.status == 200:
            content_type = response.headers.get('content-type')
            if content_type in ('text/html', 'application/xml'):
                text = yield from response.text(encoding='GBK')
                #print(text)
                soup = BeautifulSoup(text, 'lxml')
                hashList = soup.find_all(text=re.compile("hash"))
                if len( hashList )!=0:
                    name = self._strip_dir_name(arg[0][0])
                    dir = os.path.join(self.rootDir, name)
                    if not os.path.exists(dir):
                        os.makedirs(dir)
                        print("%20s ========>创建目录！<======="%(name))

                    #parse torrent url
                    torrentPath = os.path.join(dir, "1.torrent")
                    self.q.put_nowait( (hashList[0], self.download_torrent, torrentPath) )

                    #parse picture url
                    jpgList = soup.find_all(src=re.compile("\.jpg"))
                    for i in range(self.picture_num):
                        picPath = os.path.join(dir, "%d.jpg"%i)
                        if not os.path.exists(picPath):
                            self.q.put_nowait((jpgList[i]['src'], self.download_file, picPath))
                            #print(hashList[0])

    @asyncio.coroutine
    def download_file(self, response, *arg):
        if response.status == 200:
            filePath = arg[0][0]
            f=open( filePath, "wb")
            binary = yield from response.read()
            f.write(binary)
            f.close
            print("%30s ========>下载完成！<======="%(filePath))


    @asyncio.coroutine
    def download_torrent(self, response, *args):
        if response.status == 200:
            content_type = response.headers.get('content-type')
            if content_type in ('text/html', 'application/xml'):
                text = yield from response.text(encoding='GBK')
                #print(text)
                downloadUrl = urllib.parse.urljoin(response.url, 'download.php');
                soup = BeautifulSoup(text, 'lxml')
                inputList = soup.find_all('input')
                params = {}
                for i in inputList:
                    params[i['name']]=i['value']

                response = yield from self.session.get(downloadUrl, params=params)
                yield from self.download_file(response, *args)


    @asyncio.coroutine
    def fetch(self, url, handle_func, *arg):
        """Fetch one URL"""
        tries = 0
        exception = None
        while tries < self.max_tries:
            try:
                #print("try %d times"%(tries))
                response = yield from self.session.get(url)
                break;
            except aiohttp.ClientError as client_error:
                exception = client_error
            tries += 1
        else:
            return

        yield from handle_func(response, arg)
        yield from response.release()

    @asyncio.coroutine
    def work(self):
        """Process queue items forever."""
        try:
            while True:
                url,func,name = yield from self.q.get()
                yield from self.fetch(url, func, name)
                self.q.task_done()
        except asyncio.CancelledError:
            pass

    @asyncio.coroutine
    def spider(self):
        """run  the spider until all finished"""
        workers = [asyncio.Task(self.work(),loop=self.loop)
                   for _ in range (self.max_tasks)]
        yield from self.q.join()

        for w in workers:
             w.cancel()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    spider = Spider(rootDir='./source')
    loop.run_until_complete(spider.spider())
    spider.close()
    loop.stop()
    loop.run_forever()
    loop.close()

