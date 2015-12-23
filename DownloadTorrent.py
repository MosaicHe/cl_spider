import urllib2
import StringIO,gzip
from sgmllib import SGMLParser
from urlparse import *
import HttpRequest
import os
import base64
import time

class GetIdList(SGMLParser):
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

class Download_Torrent(object):

    def __init__(self, dir):
		self.dir = dir

    def download_torrent(self, url):
		content = HttpRequest.requestMultTimes(url)
		if(content==""):
			return False
		f = GetIdList()
		f.feed(content)

		boundary = "----WebKitFormBoundarydMcOM7W0mij63Igr"
		parts=[]
		for k,v in f.formdata.items():
			parts.append('--' + boundary)
			parts.append('Content-Disposition: form-data; name="'+k+'"')
			parts.append('')
			#if(k=="reff"):
			#	parts.append(base64.b64encode(str(time.time())))
			#else:
			#	parts.append(v)
			parts.append(v)
		parts.append('--' + boundary + '--')
		parts.append('\r\n')
		postdata = '\r\n'.join(parts)

		r = urlparse(url)
		downloadUrl="http://"+r.netloc+"/"+f.action
		content = HttpRequest.requestMultTimes(downloadUrl, data=postdata, headers={ "Content-Type":"multipart/form-data; boundary="+boundary})
		if(content==""):
			return False
		filename=f.formdata['ref']+".torrent"
		f=open(os.path.join(self.dir,  filename), "wb")
		f.write(content)
		f.close()
		return True

def download(url, dir):
    __dt__=Download_Torrent(dir)
    return __dt__.download_torrent(url)


if __name__=="__main__":
    url="http://www.rmdown.com/link.php?hash=153af089fb7f0a5c9d1496ea87b6a87c803ac31399d"
    download(url, ".")





