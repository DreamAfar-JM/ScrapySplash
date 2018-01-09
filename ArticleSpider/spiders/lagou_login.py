# -*- coding: utf-8 -*-

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ArticleSpider.items import LaGouItem,ArticleItemLoader
from ArticleSpider.utils.common import get_md5
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from selenium import webdriver
import os,sys
ProjectDir = os.path.abspath(os.path.dirname(__file__))
ProjectDir = os.path.abspath(os.path.dirname(ProjectDir))
ProjectDir = os.path.abspath(os.path.dirname(ProjectDir))
sys.path.insert(0, ProjectDir)

class LagouSpider(CrawlSpider):
    name = 'lagou_login'
    allowed_domains = ['www.lagou.com']
    # start_urls = ['https://www.lagou.com/']
    start_urls = ['https://www.lagou.com']
    header = {
        "HOST": "passport.lagou.com",
        "Referer": "https://www.lagou.com",
        # 'User-Agent': agent
    }
    # 设置自己的settings
    custom_settings = {
        "COOKIES_ENABLED": True,
    }
    rules = (
        #如果url匹配到这些结果，follow是深度查询
        Rule(LinkExtractor(allow=r'gongsi/j\d+.html'), follow=True),
        Rule(LinkExtractor(allow=r'zhaopin/.*'), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html.*'), callback='parse_job', follow=True),
    )

    def __init__(self):
        self.browser = webdriver.Chrome(executable_path="D:/python/chromedriver.exe")
        super(LagouSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        # 当爬虫退出的时候关闭chrome
        print("spider closed")
        self.browser.quit()

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
        LaGouArticleItem.add_value("job_url_id",get_md5(response.url))
        LaGouArticleItem.add_css("job_advantage", ".job-advantage p::text")
        LaGouArticleItem.add_css("job_desc",".job_bt div")
        LaGouArticleItem.add_css("tag",".position-label li")
        ArticleItemLoder = LaGouArticleItem.load_item()
        return ArticleItemLoder
    #
    # def start_requests(self):
    #     # return [scrapy.Request("https://www.zhihu.com/#signin",headers=self.header,callback=self.login)]
    #     Url = "https://passport.lagou.com/login/login.html"
    #     return [scrapy.Request(Url, headers=self.header, callback=self.login,meta={'cookiejar':1})]
    #
    # # def get_captcha(self):
    # #     import time
    # #     t = str(int(time.time()*1000))
    # #     captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)
    #
    # # 以下为登录操作
    # def login(self, response):
    #     Url = "https://passport.lagou.com/login/login.html"
    #     post_data = {
    #         "phone_num": "18518734899@163.com",
    #         "password": "727585266!@#",
    #     }
    #     print("登录成功")
    #     return [scrapy.FormRequest(
    #         url=Url,
    #         headers = self.header,
    #         formdata=post_data,
    #         dont_filter=True,
    #         callback=self.after_login
    #     )]
    # def after_login(self,response):
    #     print(response.status)
    #     for url in self.start_urls:
    #         yield self.make_requests_from_url(url)
    #




