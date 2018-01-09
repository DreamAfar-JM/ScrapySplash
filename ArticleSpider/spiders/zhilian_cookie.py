# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import scrapy
from scrapy.conf import settings
import os,sys
ProjectDir = os.path.abspath(os.path.dirname(__file__))
ProjectDir = os.path.abspath(os.path.dirname(ProjectDir))
ProjectDir = os.path.abspath(os.path.dirname(ProjectDir))
sys.path.insert(0, ProjectDir)

class DemoSpider(scrapy.Spider):
    name = "demo"
#allowed_domains = ["csdn.com"]
    start_urls = ["https://rdsearch.zhaopin.com/Home/ResultForCustom?SF_1_1_1=%E6%8A%80%E6%9C%AF%E6%80%BB%E7%9B%91&orderBy=DATE_MODIFIED,1&SF_1_1_27=0&exclude=1"]
    cookie = settings['COOKIE']  # 带着Cookie向网页发请求\
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0',
               'Connection': 'keep - alive',
               'Host':'rdsearch.zhaopin.com',
               'Referer': 'https://rdsearch.zhaopin.com/home/SearchByCustom',
                'Upgrade-Insecure-Requests':'1',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, sdch',
               'Accept-Language': 'zh-CN,zh;q=0.8',
    }
    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0],headers=self.headers,cookies=self.cookie)# 这里带着cookie发出请求

    def parse(self, response):
        #print (response.css("div.rd-resumelist-span span::text").extract_first())
        print (response.body)