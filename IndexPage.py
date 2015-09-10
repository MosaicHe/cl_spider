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
            hrel=[v for k,v in attrs if ( (k=="href") & (v.find("htm_data") >= 0))]
            if hrel:
                self.url_list.extend(hrel)

def gzdecode(data):
    compressedstream = StringIO.StringIO(data)
    try:
        gziper = gzip.GzipFile(fileobj=compressedstream)
    except IOError:
        return None
    else:
        data2 = gziper.read()
        return data2


class IndexPage(object):
    def __init__(self, url):
        self.index_url=url
        self.htmlContent=""
        self.urls=[]
        self.headers={
			"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Encoding":"*",
			"Accept-Language":"en-US,en;q=0.8",
			"Cache-Control":"max-age=0",
			"Connection":"keep-alive",
                        "Host":"cl.bearhk.info",
			"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/39.0.2171.65 Chrome/39.0.2171.65 Safari/537.36",
        }

    def initial(self):
		req=urllib2.Request(self.index_url, headers=self.headers)
		i = 0
		while(1):
			try:
				i += 1
				print("try %d" % i)
				time.sleep(0.5)
				response=urllib2.urlopen(req, timeout=10)
				time.sleep(1)
                        except urllib2.HTTPError,e:
                                print e.code
                                print e.read()
				continue
			except urllib2.URLError,e:
                                print "url error"
				continue
                        except socket.error as e:
                                print "socket error"
				continue
			except socket.timeout as e:
				print "socket timeout"
				continue
			else:
				try:
					content = response.read()
				except socket.error:
					print "socket read error"
					continue
                                #print content
				#self.htmlContent=gzdecode(content)
                                #if(self.htmlContent==None):
                                self.htmlContent=content
				parserhtml=ParserHtml()
				parserhtml.feed(self.htmlContent)
				self.urls=parserhtml.url_list
				#print(self.urls)
                                return

def getIndexPageUrls(url):
     m = IndexPage(url)
     m.initial()
     #print(m.urls)
     return m.urls

if __name__=="__main__":
	page=6
	while(page<20):
		url="http://cl.bearhk.info/thread0806.php?fid=15&search=&page=%d"%page
#    url="http://www.baidu.com"
		m = IndexPage(url)
		m.initial()
		print(m.urls)
		page+=1



