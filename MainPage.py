#!/usr/bin/python
#!-*-coding:utf8-*-

import urllib2
import StringIO,gzip
from sgmllib import SGMLParser
import os
import re
import DownloadTorrent
import HttpRequest
from urlparse import *
import socket
from gevent import monkey; monkey.patch_socket()
import gevent

class ParserHtml(SGMLParser):
    def reset(self):
        self.flag = False
        self.title=""
        self.title_flag=False
        self.url = ""
        self.picture=[]
        SGMLParser.reset(self)

    def start_title(self,attrs):
        self.title_flag=True

    def end_title(self):
        self.title_flag=False

    def start_a(self, attrs):
        self.flag= True

    def end_a(self):
        self.flag = False

    def start_img(self, attrs):
        pic=[v for k,v in attrs if k=="src" and v.find(".jpg")!=-1]
        if(pic):
            self.picture.extend(pic)

    def handle_data(self, data):
        if self.flag:
            if(data.find("hash=")!=-1):
                self.url=data

        if self.title_flag:
            #print(data.decode("GBK"))
            self.title=data.decode("GBK")

class MainPage(object):
	def __init__(self, mainPageContent):
		self.title=""
		self.pic_url=[]
		self.torrent_url=""
		parserhtml=ParserHtml()
		parserhtml.feed(mainPageContent)
		self.torrent_url=parserhtml.url
		self.pic_url=parserhtml.picture
		self.title=parserhtml.title.split('  ')[0].replace('/','-').replace(' ', '-')
		if(self.title==""):
			self.title=self.torrent_url.split('=')[-1]
		#self.fileDir=re.match("[A-Z0-9]*", self.parserhtml.title)
		#print(self.title)

	def getTitle(self):
		return self.title

	def getPictureUrlList(self, num=3):
		return self.pic_url[:num]

	def getTorrentUrl(self):
		return self.torrent_url


if __name__=="__main__":
	url="http://cl.bearhk.info/htm_data/15/1506/1514602.html"
	content = HttpRequest.requestMultTimes(url)
	print content
	if(content!=None):
		m = MainPage(content)
		print m.getTitle()
		print m.getPictureUrlList(4)
		print m.getTorrentUrl()
    
