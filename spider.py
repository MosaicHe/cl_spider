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

class Spider:
    def __init__(self, max_tries=30, max_tasks=2):
        self.max_tries = max_tries
        self.max_tasks = max_tasks
        self.loop = asyncio.get_event_loop()
        self.q = Queue(loop=self.loop)
        self.session = aiohttp.ClientSession(loop=self.loop)
        url = "http://cl.bearhk.info/thread0806.php?fid=15&search=&page=1"
        self.q.put_nowait((url, self.fetch, None))


    def close(self):
        self.session.close()

    @asyncio.coroutine
    def parse_index(self, response):
        """ parse index page, return main page urls set"""
        links = set()
        if response.status == 200:
            content_type = response.headers.get('content-type')
            print(content_type)
            if content_type in ('text/html', 'application/xml'):
                text = yield from response.text(encoding='GBK')

                """BeautifulSoup parse index page, get urls and titles"""
                soup = BeautifulSoup(text, 'lxml')
                for h3 in soup.find_all('h3'):
                    if not h3.a['href'].find("htm_data"):
                        normalized = urllib.parse.urljoin(response.url, h3.a['href'])
                        defragmented, frag = urllib.parse.urldefrag(normalized)
                        print(defragmented)
                        print(h3.a.string)

    @asyncio.coroutine
    def fetch(self, url):
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

        #text = yield from response.read()
        #print(text.decode('GBK'))

        yield from self.parse_index(response)

        yield from response.release()

    @asyncio.coroutine
    def work(self):
        """Process queue items forever."""
        try:
            while True:
                url,func,name = yield from self.q.get()
                if name!=None:
                    yield from func(url, name)
                else:
                    yield from func(url)
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

