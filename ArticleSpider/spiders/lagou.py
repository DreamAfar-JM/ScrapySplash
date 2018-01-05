# -*- coding: utf-8 -*-
import re
import scrapy
import datetime

from scrapy.linkextractors import LinkExtractor
# from scrapy.spiders.splash_crawl import CrawlSpider, Rule
from scrapy.spiders import CrawlSpider, Rule
from ArticleSpider.items import LaGouItem,ArticleItemLoader
from ArticleSpider.utils.common import get_md5
from scrapy_redis.spiders import RedisSpider
from ArticleSpider.settings import SQL_DATETIME_FORMAT,SQL_DATE_FORMAT
class LagouSpider(CrawlSpider,RedisSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    #start_urls = ['https://www.lagou.com/']
    start_urls = ['https://www.lagou.com']
    # 设置自己的settings
    custom_settings = {
        "COOKIES_ENABLED": False,
        #"DOWNLOAD_DELAY":5
    }
    redis_key = "lagou:start_urls"
    rules = (
        #如果url匹配到这些结果，follow是深度查询
        Rule(LinkExtractor(allow=r'gongsi/j\d+.html'), follow=True),
        Rule(LinkExtractor(allow=r'zhaopin/.*'), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html.*'), callback='parse_job', follow=True),
    )
    # def GetPage(self,response):
    #     JobNum = response.meta.get("link_text","")
    #     MatchObj = re.match(".*?(\d+).*",JobNum)
    #     if MatchObj:
    #         JobNum = int(MatchObj.group(1))
    #         if JobNum > 10:
    #             URL = response.url
    #             UrlMatchObj = re.match(".*j(\d+).*",URL)
    #             PageNum = JobNum // 10 + 2
    #             for i in range(2,PageNum):
    #                 FromData = {
    #                     'companyId': int(UrlMatchObj.group(1)),
    #                     'positionFirstType': '全部',
    #                     'pageNo': i,
    #                     'pageSize': 10
    #                 }
    #                 PostUrl = "https://www.lagou.com/gongsi/searchPosition.json"
    #                 return [scrapy.FormRequest(
    #                     url=PostUrl,
    #                     formdata=FromData,
    #                     callback=self.GetPageUrl,
    #                 )]
    # def GetPageUrl(self,response):
    #     print(response)
    #     all = response.css("a::attr(href)")
    #     print(all)
    def parse_job(self, response):
        LaGouArticleItem = ArticleItemLoader(item=LaGouItem(), response=response)
        LaGouArticleItem.add_css("job_name", '.job-name::attr(title)')
        LaGouArticleItem.add_css("salary", ".salary::text")
        LaGouArticleItem.add_xpath("job_exp", "//dd[@class='job_request']/p/span[3]/text()")
        LaGouArticleItem.add_xpath("edu", "//dd[@class='job_request']/p/span[4]/text()")
        LaGouArticleItem.add_xpath("job_type", "//dd[@class='job_request']/p/span[5]/text()")
        LaGouArticleItem.add_xpath("work_city","//dd[@class='job_request']/p/span[2]/text()")
        LaGouArticleItem.add_css("company_name","#job_company .b2::attr(alt)")
        LaGouArticleItem.add_css("company_url",".job_company dt a::attr(href)")
        LaGouArticleItem.add_css("work_addr",".work_addr")
        #LaGouArticleItem.add_xpath("feedback","//div[@class='publisher_data']/div[2]/span[@class='tip']/i/text()")
        LaGouArticleItem.add_css("create_date",".publish_time::text")
        LaGouArticleItem.add_value("job_url", response.url)
        #LaGouArticleItem.add_value("job_url_id",get_md5(response.url))
        LaGouArticleItem.add_css("job_advantage", ".job-advantage p::text")
        LaGouArticleItem.add_css("job_desc",".job_bt div")
        LaGouArticleItem.add_css("tag",".position-label li")
        ArticleItemLoder = LaGouArticleItem.load_item()

        return ArticleItemLoder




