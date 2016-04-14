@asyncio.coroutine
def parse_index(self, response, *arg):
    """ parse index page, return main page urls set"""
    links = set()
    if response.status == 200:
        content_type = response.headers.get('content-type')
        if content_type in ('text/html', 'application/xml'):
            text = yield from response.text(encoding='GBK')

                """BeautifulSoup parse index page, get urls and titles"""
                soup = BeautifulSoup(text, 'lxml')
                for a in soup.find_all(href=re.compile("htm_data")):
                    if a.find_parent().name=="h3":
                        normalized = urllib.parse.urljoin(response.url, a['href'])
                        defragmented, frag = urllib.parse.urldefrag(normalized)
                        print(defragmented)
                        print(a.string)
                        self.q.put_nowait((defragmented, None, self.parse_main, a.string))

                return 0

    @asyncio.coroutine
    def parse_main(self, response, *arg):
        """parse main page, get picture url and download torrent page url"""
        if response.status == 200:
            content_type = response.headers.get('content-type')
            if content_type in ('text/html', 'application/xml'):
                text = yield from response.text(encoding='GBK')
                #print(text)
                soup = BeautifulSoup(text, 'lxml')
                hashList = soup.find_all(text=re.compile("hash"))
                if len( hashList )!=0:
                    name = self._strip_dir_name(arg[0][0])
                    dir = os.path.join(self.rootDir, name)
                    if not os.path.exists(dir):
                        os.makedirs(dir)
                        print("%s ==============>创建目录！"%(name))

                    #parse torrent url
                    torrentPath = os.path.join(dir, "1.torrent")
                    if not os.path.exists(torrentPath):
                        self.q.put_nowait( (hashList[0], None, self.download_torrent, torrentPath) )

                    #parse picture url
                    jpgList = soup.find_all(src=re.compile("\.jpg"))
                    for i in range(self.picture_num):
                        picPath = os.path.join(dir, "%d.jpg"%i)
                        if not os.path.exists(picPath):
                            self.q.put_nowait((jpgList[i]['src'], None, self.download_file, picPath))

    @asyncio.coroutine
    def download_file(self, response, *arg):
        if response.status == 200:
            print(repsonse.headers.get('content-type'))
            filePath = arg[0][0]
            binary = yield from response.read()
            with open( filePath, "wb") as f:
                f.write(binary)
                print("%s ===============>下载完成！"%(filePath))

    @asyncio.coroutine
    def download_torrent(self, response, *args):
        if response.status == 200:
            content_type = response.headers.get('content-type')
            if content_type in ('text/html', 'application/xml'):
                text = yield from response.text(encoding='GBK')
                #print(text)
                downloadUrl = urllib.parse.urljoin(response.url, 'download.php');
                soup = BeautifulSoup(text, 'lxml')
                inputList = soup.find_all('input')
                params = {}
                for i in inputList:
                    params[i['name']]=i['value']
                    self.q.put_nowait((downloadUrl, params, self.download_file, args[0][0]))


