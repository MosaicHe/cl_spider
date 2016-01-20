#!/usr/bin/python
#!-*-coding:utf8-*-

import IndexPage
import MainPage
import HttpRequest
import os
import sys
import threading
import thread
import time
from gevent import monkey; monkey.patch_socket()
import gevent

startIndexPage=1
endIndexPage=1
counterLimit=100


threadMax = 5
threads = []

DIR="source"


def executeMainPage(url, path):
	print('GET: %s' % url)
	mContent = HttpRequest.requestMultTimes(url, retryTimes=30);
	print mContent
	if(content!=None):
		mPage = MainPage.MainPage(mContent)
		dirPath = os.path.join(path, mPage.getTitle())
		print dirPath
		if( not  os.path.exists(dirPath) ):
			print mPage.getTitle()
			os.mkdir(dirPath)
		torrentPath = os.path.join(dirPath, "1.torrent")
		print mPage.getTitle()
		t=gevent.spawn( HttpRequest.saveTorrentFile, mPage.getTorrentUrl(), torrentPath)
		
	

#main
targetPath = os.path.join(os.getcwd(), DIR)
for i in range(startIndexPage,endIndexPage+1):
	url="http://cl.bearhk.info/thread0806.php?fid=15&search=&page=%d"%i
	print url
	#get url list from index page
	content = HttpRequest.requestMultTimes(url);
	if(content!=None):
		indexPage=IndexPage.IndexPage(content)
		#threads.extend([gevent.spawn(executeMainPage, url, targetPath) for url in indexPage])
		threads.append(gevent.spawn(executeMainPage, indexPage[3], targetPath))
		gevent.joinall(threads)


time.sleep(100)

		



