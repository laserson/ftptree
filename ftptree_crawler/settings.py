# -*- coding: utf-8 -*-

# Scrapy settings for ftptree project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'ftptree'
SPIDER_MODULES = ['ftptree_crawler.spiders']
NEWSPIDER_MODULE = 'ftptree_crawler.spiders'
USER_AGENT = 'ftptree (+http://www.cloudera.com)'
DOWNLOAD_HANDLERS = {'ftp': 'ftptree_crawler.handlers.FtpListingHandler'}
DOWNLOAD_DELAY = 2
LOG_LEVEL = 'INFO'
URLLENGTH_LIMIT = 80000
