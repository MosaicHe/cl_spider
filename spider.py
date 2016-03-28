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

class Spider:
    def __init__(self, max_tries=30, max_tasks=5, picture_num=4):
        self.max_tries = max_tries
        self.max_tasks = max_tasks
        self.picture_num = picture_num
        self.loop = asyncio.get_event_loop()
        self.q = Queue(loop=self.loop)
        self.session = aiohttp.ClientSession(loop=self.loop)
        url = "http://cl.bearhk.info/thread0806.php?fid=15&search=&page=1"
        self.q.put_nowait((url, self.parse_index, None))


    def close(self):
        self.session.close()

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
                for a in soup.find_all(href=re.compile("htm_data"))[3:10]:
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
                    jpgList = soup.find_all(src=re.compile("\.jpg"))
                    self.q.put_nowait((jpgList[0]['src'], self.download_picture, "1.jpg"))
                    #print(hashList[0])

    @asyncio.coroutine
    def download_picture(self, response, *arg):
        if response.status == 200:
            f=open( "1.jpg", "wb")
            binary = yield from response.read()
            f.write(binary)
            f.close

    @asyncio.coroutine
    def fetch(self, url, handle_func, *arg):
        """Fetch one URL"""
        tries = 0
        exception = None
        while tries < self.max_tries:
            try:
                print("try %d times"%(tries))
                response = yield from self.session.get(url)
                break;
            except aiohttp.ClientError as client_error:
                exception = client_error
            tries += 1

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
    spider = Spider()
    loop.run_until_complete(spider.spider())
    spider.close()
    loop.stop()
    loop.run_forever()
    loop.close()

