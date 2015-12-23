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
    def __init__(self, url):
        self.url=url
        self.fileDir=""
        self.pic_url=[]
        self.torrent_url=""
        self.htmlContent=""
        self.parserhtml=ParserHtml()
        self.validpage=True

    def initial(self):
		self.htmlContent = HttpRequest.requestMultTimes(self.url)
		#print(self.htmlContent)
		if(not self.htmlContent):
			self.validpage=False
			return
		self.parserhtml.feed(self.htmlContent)
		self.torrent_url=self.parserhtml.url
		if self.torrent_url=="":
			self.validpage=False
			return
		self.pic_url=self.parserhtml.picture
		self.fileDir=self.parserhtml.title.split('  ')[0].replace('/','-').replace(' ', '-')
		if(self.fileDir==""):
			self.fileDir=self.torrent_url.split('=')[-1]
		#self.fileDir=re.match("[A-Z0-9]*", self.parserhtml.title)
		print(self.fileDir)
		#print(self.pic_url)
		dirlist=os.listdir('.')
		if( not self.fileDir.encode("GBK") in dirlist ):
			try:
				os.mkdir(self.fileDir)
			except:
				self.fileDir=self.torrent_url.split("hash=")[-1]
				if( not self.fileDir.encode("GBK") in dirlist ):
					os.mkdir(self.fileDir)

    def download_picture(self):
        i=0
        for url in self.pic_url[:4]:
                name="%d.jpg"%i
                f=open( os.path.join(self.fileDir, name), "wb")
                f.write(HttpRequest.requestMultTimes(url))
                f.close()
                i += 1
                print("Download picture %d"%i+" success")

    def download_torrent(self):
        if(DownloadTorrent.download(self.torrent_url, self.fileDir)):
            print("downloading torrent success")
        else:
            print("downloading torrent failed")


def exec_download(url):
	m = MainPage(url)
	m.initial()
	if not m.validpage:
		return
	m.download_picture()
	m.download_torrent()

if __name__=="__main__":
    url="http://cl.bearhk.info/htm_data/15/1506/1514602.html"
    m = MainPage(url)
    m.initial()
    m.download_picture()
    #m.download_torrent()

