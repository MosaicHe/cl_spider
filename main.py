#!/usr/bin/python3
# -*-coding:utf-8-*-

import urllib.parse
import asyncio
import aiohttp

from Spider import Request
from Spider import Spider
import PageParse
import argparse

ARGS = argparse.ArgumentParser(description="caoliu spider")
ARGS.add_argument("--pages", action='store', type=int,
                  default=1, help='Limit page to spider')
ARGS.add_argument("--max_tries", action='store', type=int,
                  default=30, help='Limit retries on network errors')
ARGS.add_argument("--root_dir", action='store',
                  default='./download', help='directory store picture and torrent')
ARGS.add_argument("--max_tasks", action='store', type=int,
                  default=20, help='Limit concurrent connections')

ROOT_DIR = "/media/mosaic/软件/git-myspider/cl_spider/source/"

args = ARGS.parse_args()

loop = asyncio.get_event_loop()
spider = Spider(max_tries=args.max_tries, max_tasks=args.max_tasks)
PageParse.start(spider, 1, args.pages+1,  root_dir=args.root_dir)
loop.run_until_complete(spider.spider())
spider.close()
loop.stop()
loop.run_forever()
loop.close()

