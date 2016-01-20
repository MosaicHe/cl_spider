#!/usr/bin/python
#!-*-coding:utf8-*-

import urllib2
import StringIO,gzip
from sgmllib import SGMLParser
import os
import re
import time
import socket
import requests
import HttpRequest

class ParserHtml(SGMLParser):
    def reset(self):
        self.h3_flag=False
        self.url_list=[]
        SGMLParser.reset(self)

    def start_h3(self,attrs):
        self.h3_flag=True

    def end_h3(self):
        self.h3_flag=False

    def start_a(self, attrs):
        if self.h3_flag:
            hrel=[v for k,v in attrs if ( (k=="href") & (v.find("htm_data") >= 0))]
            if hrel:
                self.url_list.extend(hrel)

class IndexPage(object):
    def __init__(self, content):
        self.index=0
        self.urls=[]
        parserhtml=ParserHtml()
        parserhtml.feed(content)
        self.urls=[ "http://cl.bearhk.info/%s"%u for u in parserhtml.url_list ]

    def __next__(self):
        if self.index > len(self.urls)-1:
            raise StopIteration();
        url=self.urls[self.index]
        self.index=self.index+1
        return url

    def __getitem__(self, index):
        return self.urls[index]



if __name__=="__main__":
	content = HttpRequest.requestMultTimes('http://cl.bearhk.info/thread0806.php?fid=15&search=&page=1', retryTimes=50)
	if(content):
		indexPage = IndexPage(content)
		for url in indexPage:
			print(url)

