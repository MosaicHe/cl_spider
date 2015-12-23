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
endIndexPage=4
counterLimit=100


threadMax = 5
threads = []



def getMainpageUrl(pageIndex, itemLimit):
	url="http://cl.bearhk.info/thread0806.php?fid=15&search=&page=%d"%pageIndex
	print url
	#get url list from index page
	indexPage=IndexPage.IndexPage(url)
        return indexPage


def f(url):
    #print('GET: %s' % url)
    MainPage.exec_download("http://cl.bearhk.info/%s"%url)

#main
os.chdir("source")

for i in range(startIndexPage,endIndexPage+1):
	threads =[gevent.spawn(f, url) for url in getMainpageUrl(i, counterLimit)]
	gevent.joinall(threads)



