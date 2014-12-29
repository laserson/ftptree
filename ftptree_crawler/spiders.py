import os
import json
from urlparse import urlparse

from scrapy import Spider
from scrapy.http.request import Request

from ftptree_crawler.items import FtpTreeLeaf

class AnonFtpRequest(Request):
    anon_meta = {'ftp_user': 'anonymous',
                 'ftp_password': 'laserson@cloudera.com'}

    def __init__(self, *args, **kwargs):
        super(AnonFtpRequest, self).__init__(*args, **kwargs)
        self.meta.update(self.anon_meta)


class FtpTreeSpider(Spider):
    name = 'ftptree'

    def __init__(self, config_file, *args, **kwargs):
        super(FtpTreeSpider, self).__init__(*args, **kwargs)
        with open(config_file, 'r') as ip:
            config = json.loads(ip.read())
        url = 'ftp://%s/%s' % (config['host'], config['root_path'])
        self.start_url = url
        self.site_id = config['id']

    def start_requests(self):
        yield AnonFtpRequest(self.start_url)

    def parse(self, response):
        url = urlparse(response.url)
        basepath = url.path
        files = json.loads(response.body)
        for f in files:
            if f['filetype'] == 'd':
                path = os.path.join(response.url, f['filename'])
                request = AnonFtpRequest(path)
                yield request
            if f['filetype'] == '-':
                path = os.path.join(basepath, f['filename'])
                result = FtpTreeLeaf(
                    filename=f['filename'], path=path, size=f['size'])
                yield result
