import urllib2
import urllib
import cookielib
import StringIO,gzip
from urlparse import *
import socket
import time
import requests
from sgmllib import SGMLParser
from urlparse import *
import os
import base64

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

def requestMultTimes(url, data='', headers=headers, timeout=1.5, retryTimes=20):
    i=0
    while(i<retryTimes):
        try:
            #print("try %d time"%i)
            if(data!=''):
                r = requests.post(url, data=data, headers=headers, timeout=timeout)
            else:
                r = requests.get( url, timeout=1.5, headers=headers)
            return r.content
        except requests.exceptions.RequestException as e:
            i += 1
    return None


def saveContentAsFile(url, filePath):
    content = requestMultTimes(url)
    if(content):
        f=open( filePath, "wb")
        f.write(requestMultTimes(url))
        f.close()


class ParserTorrentPage(SGMLParser):
        def reset(self):
            self.flag = False
            self.formdata = {}
            self.action=""
            SGMLParser.reset(self)

        def start_form(self, attrs):
            self.flag= True
            for k,v in attrs:
                if(k=="action"):
                    self.action=v

        def end_form(self):
            self.flag = False

        def start_input(self,attrs):
            if(self.flag):
                name=""
                val=""
                for k, v in attrs:
                    if(k=="name" ):
                        name=v
                    elif(k=="value"):
                         val=v
                    if(name!="" and val !=""):
                        self.formdata[name]=val

def saveTorrentFile(url, filePath="./1.torrent"):
	print url
	content = requestMultTimes(url, retryTimes=30)
	print content
	if(content==None):
		return False
	f = ParserTorrentPage()
	f.feed(content)

	boundary = "----WebKitFormBoundarydMcOM7W0mij63Igr"
	parts=[]
	for k,v in f.formdata.items():
		parts.append('--' + boundary)
		parts.append('Content-Disposition: form-data; name="'+k+'"')
		parts.append('')
		parts.append(v)

	parts.append('--' + boundary + '--')
	parts.append('\r\n')
	postdata = '\r\n'.join(parts)

	r = urlparse(url)
	downloadUrl="http://"+r.netloc+"/"+f.action
	content = requestMultTimes(downloadUrl, data=postdata, headers={"Content-Type":"multipart/form-data; boundary="+boundary})
	if(content==""):
		return False
	f=open(filePath, "wb")
	f.write(content)
	f.close()


if __name__=="__main__":
    url="http://t10.imgchili.net/66345/66345844_xv9.cc_nhdta684c.jpg"
    saveContentAsFile(url, "./test.jpg")
    url = "http://www.rmdown.com/link.php?hash=1528d4b8a37c79d2221c437332aff728daa2a4d989b"
    saveTorrentFile(url, "./test.torrent")
