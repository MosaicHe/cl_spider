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

def gzdecode(data):
    compressedstream = StringIO.StringIO(data)
    gziper = gzip.GzipFile(fileobj=compressedstream)
    data2 = gziper.read()
    return data2


class MainPage(object):
    def __init__(self, url):
        self.url=url
        self.fileDir=""
        self.pic_url=[]
        self.torrent_url=""
        self.htmlContent=""
        self.parserhtml=ParserHtml()
        self.validpage=True
        self.httpRequest=HttpRequest.HttpRequest()

    def initial(self):
		self.htmlContent = self.httpRequest.getHttpContent(self.url)
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
        '''
        pic_num=0
        for url in self.pic_url:
            if pic_num>4:
                    break
            pic_num+=1
            print("downloading picture %d"%pic_num)
            headers={
                      "Cookie":"__cfduid=d85f67776754f2f8889f05449af0967d91433699473; CNZZDATA950900=cnzz_eid%3D1154953464-1433695251-%26ntime%3D1433780060",
                      "If-None-Match":'W/"1e833fa-229b-518048e8e1455"',
                      "If-Modified-Since":"Mon, 09 Jun 2015 16:58:54 GMT",
                    }
            content = self.httpRequest.getHttpContentRaw(url,"", headers)
            if(content==""):
                print("failed")
                break
            name="%d.jpg"%pic_num
            f=open( name, "wb")
            f.write(content)
            f.close()
            print("success")
        '''

        headers={
            "Connection":"keep-alive",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
            "Accept-Encoding":"gzip, deflate, sdch",
            "Accept-Language":"zh-CN,zh;q=0.8",
            "Cookie":"__cfduid=d85f67776754f2f8889f05449af0967d91433699473; CNZZDATA950900=cnzz_eid%3D1154953464-1433695251-%26ntime%3D1433780060",
            "If-None-Match":'W/"1e833fa-229b-518048e8e1455"',
            "If-Modified-Since":"Mon, 09 Jun 2015 16:58:54 GMT",
        }
        pic_num=0
        #print(self.pic_url)
        #self.pic_url=["http://t10.imgchili.net/66313/66313166_bobb00262jp_5.jpg"]
        for url in self.pic_url:
            r = urlparse(url)
            req=urllib2.Request(url, headers=headers)
            req.add_header("Host", r.netloc)
            if pic_num>4:
                    break
            pic_num+=1
            try:
                response=urllib2.urlopen(req, timeout=8)
                content = response.read()
            except urllib2.URLError,e:
                print("Download picture %d"%pic_num+" failed")
            except socket.timeout as e:
                print "socket timeout"
            except:
                print "unknown error"
            else:
                name="%d.jpg"%pic_num
                f=open( os.path.join(self.fileDir, name), "wb")
                f.write(content)
                f.close()
                print("Download picture %d"%pic_num+" success")

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

