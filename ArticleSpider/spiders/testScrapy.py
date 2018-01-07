# -*- coding: utf-8 -*-
import re
import scrapy
import datetime

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ArticleSpider.items import ZhiLianItem,ArticleItemLoader
from ArticleSpider.utils.common import get_md5
from scrapy_redis.spiders import RedisSpider
from ArticleSpider.settings import SQL_DATETIME_FORMAT,SQL_DATE_FORMAT
from scrapy_splash import SplashRequest

lua_script = """
function main(splash)
    splash:go(splash.args.url)
    splash:wait(2)
    return splash:html()
end
"""


class cnblogSpider(CrawlSpider):
    name = 'test'
    allowed_domains = ['cnblogs.com']
    start_url = 'https://www.cnblogs.com/shanyou/p/8227397.html'

    def parse(self, response):
        print("get_url:%s" %response.url)
        yield SplashRequest(response.url, endpoint='execute', args={'images': 0, 'lua_source': lua_script},
                                cache_args=['lua_source'], callback=self.parse_num_url)


    def parse_num_url(self, response):
        pattern = '.*/p/.*\d+\.html'
        le = LinkExtractor(allow=pattern)
        links = le.extract_links(response)
        for link in links:
            print(link.url)

        return

