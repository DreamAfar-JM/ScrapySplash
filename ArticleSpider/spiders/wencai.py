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
    splash:wait(10)
    splash:runjs("document.getElementsById('footbarCon').scrollIntoView(true)")
    splash:wait(10)
    return splash:html()
end
"""

lua_script2 = """
function main(splash)
    splash:go(splash.args.url)
    splash:wait(5)
    splash:runjs("document.getElementsById('next').click()")
    splash:wait(5)
    return splash:html()
end
"""

lua_script3 = """
function main(splash)
    splash:go(splash.args.url)
    splash:wait(5)
    splash:runjs("document.getElementsClassName('doctor_special_page_foot adaptive_foot1').scrollIntoView(true)")
    splash:wait(5)
    return splash:html()
end
"""

class WencaiSpider(scrapy.Spider):
    name = "wencai"
    allowed_domains = ["iwencai.com"]
    start_url = "https://www.iwencai.com/stockpick?my=0&ordersignal=0"

    def start_requests(self):
        # 请求第一页
        print("开始爬取首页")
        yield Request(self.start_url, callback=self.shares_list, dont_filter=True)
        # yield SplashRequest(self.start_url, endpoint='execute', args={'lua_source': lua_script}, cache_args=['lua_source'])
    def shares_list(self,response):
        pattern = '/stockpick/.*'
        pattern_deny = '/stockpick/.+index_name.*'
        pattern_deny2 = '/stockpick/.+ts=1$'
        le = LinkExtractor(allow=pattern,deny=pattern_deny)
        links = le.extract_links(response)
        print("开始解析股票列表")
        print(response.url)
        for link in links:
            print("发现一个股票列表页面:%s" %(link.url))
            yield SplashRequest(link.url, endpoint='execute', args={'images': 0, 'lua_source': lua_script},
                                cache_args=['lua_source'], callback=self.parse_num_url)

    def parse_num_url(self,response):
        # link_list = []
        print("开始解析股票页面")
        pattern = '/stockpick/.+\d{6}$'
        le = LinkExtractor(allow=pattern)
        num_links = le.extract_links(response)
        for num_link in num_links:
            # link_list.append(num_link.url)
            # print("found url: %s"%num_link.url)
            print("解析到股票详情页：%s"%num_link.url)
            yield SplashRequest(num_link.url, endpoint='execute', args={'images': 0, 'lua_source': lua_script3}, cache_args=['lua_source'], callback=self.parse)
            print("yield: %s" %num_link.url)
            # print(link_list)
            # pass
        # if "disable_next" not in str(response.body) and "ts=1" not in response.url:
        #     print("link:%s"%num_links)
        #     print("发现还有下页的股票列表：%s" %response.url)
        #     yield SplashRequest(response.url, endpoint='execute', args={'images': 0, 'lua_source': lua_script2}, cache_args=['lua_source'], callback=self.parse_num_url,dont_filter=True)
        pattern2 = '/stockpick/.+qs=lm_.+'
        le2 = LinkExtractor(allow=pattern2)
        links2 = le2.extract_links(response)
        for link2 in links2:
            print("获取到qs股票列表页：%s" %link2.url)
            yield SplashRequest(link2.url, endpoint='execute', args={'images': 0, 'lua_source': lua_script}, cache_args=['lua_source'], callback=self.parse_num_url,dont_filter=True)

    def parse(self, response):
        # print("found_url: %s"%response.url)

        try:
            print("获取【%s】的sel"%response.url)
            sel = response.css("div.simple_table_viewport")[0]
        except IndexError:
            print("页面未解析到response,重新下载")
            yield SplashRequest(response.url, endpoint='execute', args={'images': 0, 'lua_source': lua_script3}, cache_args=['lua_source'], callback=self.parse)
            print("重新下载URL：%s" %response.url)
        else:
            print("获取到sel")
            BaseInfoItem = WencaiBaseInfo()
            ClinicSharesItem = WencaiClinicShares()
            ImportEvents = WencaiImportEvents()
            ImportNews = WencaiImportNews()
            InvestmentAnalysis = WencaiInvestmentAnalysis()
            WindyItem = WencaiWindy()
            value_list = sel.xpath(".//td//text()").extract()
            # print(value_list)
            Code = int(value_list[1])
            Abb = value_list[4]
            Industry = value_list[7]
            City = value_list[10]
            if "近期重要事件" in response.text:
                print("发现重要事件")
                important_events = response.css("div.simple_table_viewport")[1]
                for j  in important_events.xpath(".//tbody//tr"):
                    i = j.xpath(".//td//text()").extract()
                    # print(i)
                    EventName = i[7]
                    #EventContext = i[10]
                    EventContext = "".join(j.xpath(".//td//span//text()").extract())
                    EventTime = i[13]
                    ImportEvents['Code'] = Code
                    ImportEvents['EventName'] = EventName
                    ImportEvents['EventContext'] = EventContext
                    ImportEvents['EventTime'] = EventTime
                    print("yield 重要事件")
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
                print("yield重要新闻")
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
            #print("")
            for i in [BaseInfoItem,ClinicSharesItem,InvestmentAnalysis,WindyItem]:
                print("yield: %s" %i)
                yield i
            pattern3 = '/stockpick/.+&qs=stockpick_tag$'
            print("匹配到tag结尾的股票列表")
            le3 = LinkExtractor(allow=pattern3)
            links3 = le3.extract_links(response)
            for link3 in links3:
                print("tag url:%s" %link3.url)
                yield SplashRequest(link3.url, endpoint='execute', args={'images': 0, 'lua_source': lua_script},
                                    cache_args=['lua_source'], callback=self.parse_num_url,dont_filter=True)
                print("url:%s已被yield" %link3.url)




