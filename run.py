import IndexPage
import MainPage
import os
import sys
import threading
import thread
import time
from gevent import monkey; monkey.patch_socket()
import gevent

startIndexPage=1
endIndexPage=1
counterLimit=0


threadMax = 5
threads = []

class MainPageUrl(object):
	def __init__(self, start, end):
		self.endPage=end
		self.currentPage=start
		self.urlList = []
		self.urlListLen=0
		self.currentIndex=0
		
	def getMainpageUrl(self):
		#urlList is not ready or already  be read
		if( self.urlListLen==0 or self.currentIndex>=self.urlListLen):
			#reach the last page
			if(self.currentPage > self.endPage):
				return None
			else:
				url="http://cl.bearhk.info/thread0806.php?fid=15&search=&page=%d"%self.currentPage
				print url
				#get url list from index page
				self.urlList=IndexPage.getIndexPageUrls(url)
				self.urlListLen = len(self.urlList)
				self.currentIndex=0
				print "*****************************************\n"
				print "*****************page %d, url counter %d*****************\n"%(self.currentPage,self.urlListLen);
				print "*****************************************\n"
				self.currentPage += 1
				
		#mainpageUrl="http://cl.bearhk.info/%s"%self.urlList[self.currentIndex]
		#self.currentIndex+=1
		return self.urlList


def f(url):
    #print('GET: %s' % url)
    MainPage.exec_download("http://cl.bearhk.info/%s"%url)

#main
os.chdir("source")
finished = False
m = MainPageUrl(startIndexPage, endIndexPage)	
threads =[gevent.spawn(f, url) for url in m.getMainpageUrl()]
gevent.joinall(threads)
			

	
		
