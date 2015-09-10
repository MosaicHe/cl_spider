import urllib2
import StringIO,gzip
from sgmllib import SGMLParser
from urlparse import *
import HttpRequest
import os

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
		self.httpRequest=HttpRequest.HttpRequest()
		self.dir = dir

    def download_torrent(self, url):
		content = self.httpRequest.getHttpContent(url)
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
			parts.append(v)
		parts.append('--' + boundary + '--')
		parts.append('\r\n')
		postdata = '\r\n'.join(parts)

		r = urlparse(url)
		downloadUrl="http://"+r.netloc+"/"+f.action
		content = self.httpRequest.getHttpContent(downloadUrl, postdata, { "Content-Type":"multipart/form-data; boundary="+boundary})
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
    url="http://www.rmdown.com/link.php?hash=1529b80aa7e31ac705a22ae24604fae88610abc7816"
    download(url)





