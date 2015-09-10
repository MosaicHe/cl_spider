#!/usr/bin/python
#!-*-coding:utf8-*-

import urllib2
import StringIO,gzip
from sgmllib import SGMLParser
import os
import re
import time
import socket

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
            hrel=[v for k,v in attrs if k=="href"]
            if hrel:
                self.url_list.extend(hrel)

def gzdecode(data):
    compressedstream = StringIO.StringIO(data)
    gziper = gzip.GzipFile(fileobj=compressedstream)
    data2 = gziper.read()
    return data2


class IndexPage(object):
    def __init__(self, url):
        self.index_url=url
        self.htmlContent=""
        self.urls=[]
        self.headers={
			"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Encoding":"gzip, deflate, lzma, sdch",
			"Accept-Language":"zh-CN,zh;q=0.8",
			"Cache-Control":"max-age=0",
			"Connection":"keep-alive",
			"Cookie":"__cfduid=d309b0ef2c49ef4d2c91b19533be48f081433253304; 227c9_lastfid=0; 227c9_lastvisit=0%091435847608%09%2Fread.php%3Ftid%3D5877; CNZZDATA950900=cnzz_eid%3D1900637555-1433252450-%26ntime%3D1435844487",
			"Host":"cl.bearhk.info",
			"Referer":"http://cl.bearhk.info/index.php",
			"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.125 Safari/537.36 OPR/30.0.1835.88",
        }

    def initial(self):
		f = open("../index6.html")
		self.htmlContent=f.read()
		#print(self.htmlContent)
		parserhtml=ParserHtml()
		parserhtml.feed(self.htmlContent)
		self.urls=parserhtml.url_list
		print(self.urls)

def getIndexPageUrls(url):
     m = IndexPage(url)
     m.initial()
     #print(m.urls)
     return m.urls

if __name__=="__main__":
    url="http://t66y.com/thread0806.php?fid=15"
    m = IndexPage(url)
    m.initial()
    print(m.urls)



