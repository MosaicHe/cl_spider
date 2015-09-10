import urllib2
import urllib
import cookielib
import StringIO,gzip
from urlparse import *
import socket
import time

headers_default={
                "Connection":"keep-alive",
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
                "Accept-Encoding":"gzip, deflate, sdch",
                "Accept-Language":"zh-CN,zh;q=0.8",
            }

def gzdecode(data):
    compressedstream = StringIO.StringIO(data)
    gziper = gzip.GzipFile(fileobj=compressedstream)
    data2 = gziper.read()
    return data2

class _HttpRequest(object):

    def __init__(self):
        self.content=""
        self.headers=headers_default
        self.cookie=cookielib.LWPCookieJar()
        handler=urllib2.HTTPCookieProcessor(self.cookie)
        self.opener=urllib2.build_opener(handler)

    def getHttpContentRaw(self, url,data="", headers={}):
		r = urlparse(url)
		print(url)
		netloc=r.netloc
		request=urllib2.Request(url,data=data, headers=self.headers)
		request.add_header( "Host", netloc)
		for k,v in headers.iteritems():
			request.add_header(k,v)
		#print reqouest.header_items()
		print("start open mainpage")
		counter = 0
		while(counter<20):
			try:
				counter = counter + 1
				print("try %d" % counter)
				#response = urllib2.urlopen(request)
				response = self.opener.open(request, timeout=10)
			except urllib2.URLError,e:
				time.sleep(0.5)
				continue
			except socket.timeout as e:
				print "socket timeout"
				time.sleep(0.5)
				continue
			except:
				time.sleep(0.5)
				continue
			else:
				try:
					content=response.read()
				except socket.error:
					time.sleep(0.5)
					continue
				else:
					return content

    def getHttpContent(self, url, data="", headers={}):
		content=self.getHttpContentRaw(url,data, headers)
		if( not content):
			return None
		else:
			return gzdecode(content)

def HttpRequest():
    __httpRequest = _HttpRequest()
    return __httpRequest


if __name__=="__main__":
    url="http://t10.imgchili.net/66345/66345844_xv9.cc_nhdta684c.jpg"
    httprequest = HttpRequest()
    f=open( "test.jpg", "wb")
    f.write(httprequest.getHttpContentRaw(url))
    f.close()
