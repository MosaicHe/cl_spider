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

CL_URL = "http://cl.bearhk.info/thread0806.php?fid=15&search=&page=%s"


CONTENT_TYPE_TEXT = {
    'text/html',
    'application/xml',
    'text/xml',
    'text/*'
}

class Request(object):
    def __init__(self, spider, url, request_type='get', params=None, data=None,
                 content_type='text'):
        self.spider = spider
        self.url = url
        self.request_type = request_type
        self.params = params
        self.data = data
        self.content_type = content_type

        # append request to spider task queue
        self.spider.append_request(self)

    def handle_func(self, content):
        pass

class Spider:
    def __init__(self,page_num=1, max_tries=30, max_tasks=10, picture_num=2
                 , rootDir=os.getcwd()):
        self.max_tries = max_tries
        self.max_tasks = max_tasks
        self.picture_num = picture_num
        self.loop = asyncio.get_event_loop()
        self.q = Queue(loop=self.loop)
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.rootDir = rootDir
        self.page_num = page_num

    def close(self):
        self.session.close()


    def append_request(self, request):
        self.q.put_nowait(request)


    @asyncio.coroutine
    def _get_request(self):
        r = yield from self.q.get()
        return r


    @asyncio.coroutine
    def fetch(self, request_type, url, params, data):
        """Fetch one URL"""
        tries = 0
        exception = None
        while tries < self.max_tries:
            try:
                print("try %s---->%d times"%(url, tries))
                with aiohttp.Timeout(40):
                    response = yield from self.session.get(url, params=params)
                    if response.status == 200:
                        url = response.url
                        content_type = response.headers.get('content-type')
                        if content_type in CONTENT_TYPE_TEXT:
                            content = yield from response.text(encoding='GBK')
                        else:
                            content = yield from response.read()
                        yield from response.release()
                        return content
                break;
            except asyncio.TimeoutError:
                print("timeout")
                pass
            except aiohttp.ClientError as client_error:
                exception = client_error
            tries += 1
        else:
            print("try %s---->more than %d times, quit"%(url, tries))
            return None


    @asyncio.coroutine
    def _work(self):
        """Process queue items forever."""
        try:
            while True:
                r = yield from self._get_request()
                content = yield from self.fetch(r.request_type, r.url, r.params, r.data)
                if(content):
                    r.handle_func(content)
                self.q.task_done()
        except asyncio.CancelledError:
            pass

    @asyncio.coroutine
    def work(self):
        yield from self._work()

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
    spider = Spider(page_num=5, max_tries=2, max_tasks=2, rootDir='./source')
    request = IndexPageRequest(CL_URL%1)
    spider.append_request(request)
    loop.run_until_complete(spider.spider())
    spider.close()
    loop.stop()
    loop.run_forever()
    loop.close()

