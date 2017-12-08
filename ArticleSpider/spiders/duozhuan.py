# -*- coding: utf-8 -*-
import scrapy
import re
from urllib import parse
class DuozhuanSpider(scrapy.Spider):
    name = "duozhuan"
    index = "https://www.duozhuan.cn"
    allowed_domains = ["https://www.duozhuan.cn"]
    start_urls = ['https://www.duozhuan.cn/Aboutus/hot_feed/']
    agent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    headers = {
        #"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "HOST": "www.duozhuan.cn",
        "Referer": "https://www.duozhuan.cn",
            }
    header = {
        #"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "HOST": "www.duozhuan.cn",
        "Referer": "https://www.duozhuan.cn/Aboutus/hot_feed/",
        "Upgrade-Insecure-Requests":1
    }
    def parse(self, response):
        #获取当前页所有标题URL
        PostURL =  response.css("header .clearfix li a::attr(href)").extract()
        #HotUrl = []
        for Post in PostURL:
            MatchObj = re.match("^/hot_feed-[0-9]",Post)
            if MatchObj:
                HotUrl = parse.urljoin(self.index,Post)
                yield scrapy.Request(HotUrl,headers=self.header,callback=self.parse_get_url,dont_filter=True)

    def parse_get_url(self,response):
        NowPageAllUrl = response.css(".discuss-table a::attr(href)").extract()
        NextPage = response.css(".ps-right::attr(href)").extract()[0]
        for NowPage in NowPageAllUrl:
            if "show_feed" in NowPage:
                yield scrapy.Request(NowPage,headers=self.headers,callback=self.parse_get_content,dont_filter=True)
        if "javascript" not in NextPage:
            NextPageUrl = parse.urljoin(self.index,NextPage)
            yield scrapy.Request(NextPageUrl, headers=self.header, callback=self.parse_get_url, dont_filter=True)
    def parse_get_content(self,response):
        pass


    def start_requests(self):
        return [scrapy.Request("https://www.duozhuan.cn/Aboutus/hot_feed/", headers=self.headers, callback=self.parse)]