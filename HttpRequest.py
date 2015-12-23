import urllib2
import urllib
import cookielib
import StringIO,gzip
from urlparse import *
import socket
import time
import requests

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
            print("try %d time"%i)
            if(data!=''):
                r = requests.post(url, data=data, headers=headers, timeout=timeout)
            else:
                r = requests.get( url, timeout=1.5, headers=headers)
            break
        except requests.exceptions.RequestException as e:
            i += 1
    return r.content

if __name__=="__main__":
    url="http://t10.imgchili.net/66345/66345844_xv9.cc_nhdta684c.jpg"
    f=open( "test.jpg", "wb")
    f.write(requestMultTimes(url))
    f.close()
