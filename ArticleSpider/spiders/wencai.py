# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy_splash import SplashRequest
from ArticleSpider.items import WencaiBaseInfo,WencaiClinicShares,WencaiImportEvents,WencaiImportNews,WencaiInvestmentAnalysis,WencaiWindy
from scrapy.linkextractors import LinkExtractor

import sys
lua_script = """
function main(splash)
    splash:go(splash.args.url)
    splash:wait(2)
    splash:runjs("document.getElementsByClassName('next')[0].scrollIntoView(true)")
    splash:wait(2)
    return splash:html()
end
"""

lua_script2 = """
function main(splash)
    splash:go(splash.args.url)
    splash:wait(2)
    splash:runjs("document.getElementsById('next').click()")
    splash:wait(2)
    return splash:html()
end
"""

lua_script3 = """
function main(splash)
    splash:go(splash.args.url)
    splash:wait(2)
    splash:runjs("document.getElementsById('stockpick_shadow_iframe').scrollIntoView(true)")
    splash:wait(3)
    return splash:html()
end
"""

class WencaiSpider(scrapy.Spider):
    name = "wencai"
    allowed_domains = ["iwencai.com"]
    start_url = "https://www.iwencai.com/stockpick?my=0&ordersignal=0"

    def start_requests(self):
        # 请求第一页
        yield Request(self.start_url, callback=self.shares_list, dont_filter=True)
        # yield SplashRequest(self.start_url, endpoint='execute', args={'lua_source': lua_script}, cache_args=['lua_source'])
    def shares_list(self,response):
        pattern = '/stockpick/.*'
        le = LinkExtractor(allow=pattern)
        links = le.extract_links(response)
        for link in links:
            yield SplashRequest(link.url, endpoint='execute', args={'images': 0, 'lua_source': lua_script},
                                cache_args=['lua_source'], callback=self.parse_num_url)

    def parse_num_url(self,response):
        # link_list = []
        pattern = '/stockpick/.+\d{6}$'
        le = LinkExtractor(allow=pattern)
        num_links = le.extract_links(response)
        for num_link in num_links:
            # link_list.append(num_link.url)
            # print("found url: %s"%num_link.url)
            yield SplashRequest(num_link.url, endpoint='execute', args={'images': 0, 'lua_source': lua_script3}, cache_args=['lua_source'], callback=self.parse)
            # print(link_list)
            # pass
        if "disable_next" not in str(response.body):
            yield SplashRequest(response.url, endpoint='execute', args={'images': 0, 'lua_source': lua_script2}, cache_args=['lua_source'], callback=self.parse_num_url)


    def parse(self, response):
        # print("found_url: %s"%response.url)
        BaseInfoItem = WencaiBaseInfo()
        ClinicSharesItem = WencaiClinicShares()
        ImportEvents = WencaiImportEvents()
        ImportNews = WencaiImportNews()
        InvestmentAnalysis = WencaiInvestmentAnalysis()
        WindyItem = WencaiWindy()
        #try:
        sel = response.css("div.simple_table_viewport")[0]
        #except Exception as e:
            # log_file = 'wencai.log'
            # f = open(log_file,'a')
            # f.write(e)
            # f.write(response.url)
            # f.close()
        value_list = sel.xpath(".//td//text()").extract()
        # print(value_list)
        Code = int(value_list[1])
        Abb = value_list[4]
        Industry = value_list[7]
        City = value_list[10]
        if "近期重要事件" in response.text:
            important_events = response.css("div.simple_table_viewport")[1]
            for i  in important_events.xpath(".//tbody//tr"):
                i = i.xpath(".//td//text()").extract()
                # print(i)
                EventName = i[7]
                EventContext = i[10]
                EventTime = i[13]
                ImportEvents['Code'] = Code
                ImportEvents['EventName'] = EventName
                ImportEvents['EventContext'] = EventContext
                ImportEvents['EventTime'] = EventTime
                yield ImportEvents
        InvestmentContext = "".join(response.css(".zcwylw_comment").extract())
        if len(InvestmentContext) == 0:
            InvestmentContext = "".join(response.css(".btc_area").extract())
        for news in response.css(".frontpage_item.pro_baidu_news.pro_baidu_news2"):
            NewUrl = news.xpath('.//a/@href').extract_first()
            NewTitle = news.xpath('.//span[@class="news_title"]/text()').extract_first()
            NewContext = news.xpath('.//p[contains(@class, "summm")]').extract()
            ImportNews['Code'] = Code
            ImportNews['NewUrl'] = NewUrl
            ImportNews['NewTitle'] = NewTitle
            ImportNews['NewContext'] = NewContext
            yield ImportNews

        WindyContext = "".join(response.css(".tag_cloud_subbox.relative").extract())
        Score = "".join(response.css(".point.pt15.tc::text").extract())
        Title = response.css(".head_text.fb.f14 a::text").extract_first()
        ClinicShareUrl = response.css(".head_text.fb.f14 a::attr('href')").extract_first()
        Context = "".join(response.css(".desc_text.lh20").extract())
        # Trend = response.css(".item_list.clearfix li em::text").extract()
        ShortTrend =response.css(".item_list.clearfix>li:nth-child(1)::text").extract()
        MiddleTrend = response.css(".item_list.clearfix>li:nth-child(2)::text").extract()
        LongTrend = response.css(".item_list.clearfix>li:nth-child(3)::text").extract()

        BaseInfoItem['Code'] = Code
        BaseInfoItem['Abb'] = Abb
        BaseInfoItem['Industry'] = Industry
        BaseInfoItem['City'] = City

        ClinicSharesItem['Code'] = Code
        ClinicSharesItem['Title'] = Title
        ClinicSharesItem['Context'] = Context
        ClinicSharesItem['ClinicShareUrl'] = ClinicShareUrl
        ClinicSharesItem['Score'] = Score
        ClinicSharesItem['ShortTrend'] = ShortTrend
        ClinicSharesItem['MiddleTrend'] = MiddleTrend
        ClinicSharesItem['LongTrend'] = LongTrend

        InvestmentAnalysis['InvestmentContext'] = InvestmentContext
        InvestmentAnalysis['Code'] = Code

        WindyItem['Code'] = Code
        WindyItem['WindyContext'] = WindyContext

        for i in [BaseInfoItem,ClinicSharesItem,InvestmentAnalysis,WindyItem]:
            yield i




