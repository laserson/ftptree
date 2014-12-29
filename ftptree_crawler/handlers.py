import json

from twisted.protocols.ftp import FTPFileListProtocol

from scrapy.http import Response
from scrapy.core.downloader.handlers.ftp import FTPDownloadHandler

class FtpListingHandler(FTPDownloadHandler):
    def gotClient(self, client, request, filepath):
        self.client = client
        protocol = FTPFileListProtocol()
        return client.list(filepath, protocol).addCallbacks(
            callback=self._build_response, callbackArgs=(request, protocol),
            errback=self._failed, errbackArgs=(request,))

    def _build_response(self, result, request, protocol):
        self.result = result
        body = json.dumps(protocol.files)
        return Response(url=request.url, status=200, body=body)
