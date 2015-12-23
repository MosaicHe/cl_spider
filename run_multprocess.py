import IndexPage
import MainPage
import os
import sys
import threading
import thread
import time

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
				
		mainpageUrl="http://cl.bearhk.info/%s"%self.urlList[self.currentIndex]
		self.currentIndex+=1
		return mainpageUrl

		
class DowloadThread(threading.Thread):
	def __init__(self, url):
		threading.Thread.__init__(self)
		self.url = url
	
	def run(self):
		MainPage.exec_download(self.url)
		thread.exit_thread()
		
#main
os.chdir("source")
finished = False
m = MainPageUrl(startIndexPage, endIndexPage)	
counter=0
while(True):
	if(finished and threading.activeCount()==1 ):
		print "*******************************************\n"
		print "*********** download finished *************\n"
		print "*******************************************\n"
		exit()
	elif(threading.activeCount() < threadMax):
		url = m.getMainpageUrl()
		if(url!=None):
			t = DowloadThread(url)
			t.start()
			
			if(counterLimit>0 and counter>counterLimit):
				exit()
			else:
				counter+=1
		else:
			finished = True
			runningList = threading.enumerate()
			for t in runningList:
				if(t != threading.currentThread()):
					t.join()
	time.sleep(0.3)

	
		
