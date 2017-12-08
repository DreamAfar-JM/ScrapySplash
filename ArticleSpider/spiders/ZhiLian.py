# -*- coding: utf-8 -*-
import re
import scrapy
import datetime

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ArticleSpider.items import ZhiLianItem,ArticleItemLoader
from ArticleSpider.utils.common import get_md5
from ArticleSpider.scrapy_redis.spiders import RedisSpider
from ArticleSpider.settings import SQL_DATETIME_FORMAT,SQL_DATE_FORMAT


class ZhilianSpider(CrawlSpider,RedisSpider):
    name = 'ZhiLian'
    allowed_domains = ['jobs.zhaopin.com']
    start_urls = ['http://jobs.zhaopin.com/']
    redis_key = "zhilian:start_urls"
    #start_urls = ['http://jobs.zhaopin.com/']

    rules = (
        Rule(LinkExtractor(allow=r'(^|^/)(sj\d+($|/p\d+))'), follow=True),
        #匹配厦门
        # Rule(LinkExtractor(allow=r'^xiamen/.*'), follow=True),
        # Rule(LinkExtractor(allow=r'^xiamen/$'), follow=True),
        Rule(LinkExtractor(allow=r'.*\d+.*.htm$'),callback="parse_zl", follow=True),
    )

    def parse_zl(self, response):
        LaGouArticleItem = ArticleItemLoader(item=ZhiLianItem(), response=response)
        LaGouArticleItem.add_css("job_name", '.fixed-inner-box h1::text')
        LaGouArticleItem.add_xpath("salary", "//div[@class='terminalpage-left']/ul/li[1]/strong/text()")
        LaGouArticleItem.add_xpath("job_exp", "//div[@class='terminalpage-left']/ul/li[5]/strong/text()")
        LaGouArticleItem.add_xpath("edu", "//div[@class='terminalpage-left']/ul/li[6]/strong/text()")
        LaGouArticleItem.add_xpath("job_type", "//div[@class='terminalpage-left']/ul/li[4]/strong/text()")
        LaGouArticleItem.add_xpath("work_city","//div[@class='terminalpage-left']/ul/li[2]/strong/a/text()")
        LaGouArticleItem.add_css("company_name",".inner-left a ::text")
        LaGouArticleItem.add_css("company_url",".inner-left a::attr(href)")
        LaGouArticleItem.add_css("work_addr",".terminalpage-main h2::text")
        #LaGouArticleItem.add_xpath("feedback","//div[@class='publisher_data']/div[2]/span[@class='tip']/i/text()")
        LaGouArticleItem.add_xpath("create_date","//div[@class='terminalpage-left']/ul/li[3]/strong")
        LaGouArticleItem.add_value("job_url", response.url)
        #LaGouArticleItem.add_value("job_url_id",get_md5(response.url))
        LaGouArticleItem.add_css("job_advantage", ".welfare-tab-box ::text")
        LaGouArticleItem.add_xpath("job_desc","//div[@class='tab-inner-cont'][1]/p")
        LaGouArticleItem.add_xpath("tag","//div[@class='terminalpage-left']/ul/li[8]/strong/a/text()")
        ArticleItemLoder = LaGouArticleItem.load_item()

        return ArticleItemLoder
