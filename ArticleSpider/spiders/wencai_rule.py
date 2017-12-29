# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy_splash import SplashRequest
from ArticleSpider.items import WencaiBaseInfo,WencaiClinicShares,WencaiImportEvents,WencaiImportNews,WencaiInvestmentAnalysis,WencaiWindy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders.splash_crawl import CrawlSpider, Rule

lua_script3 = """
function main(splash)
    splash:go(splash.args.url)
    splash:wait(2)
    splash:runjs("document.getElementsClassName('doctor_special_page_foot adaptive_foot1').scrollIntoView(true)")
    splash:wait(2)
    return splash:html()
end
"""

class WencaiRuleSpider(CrawlSpider):
    name = "wencai_rule"
    allowed_domains = ["iwencai.com"]
    # start_url = "https://www.iwencai.com/stockpick?my=0&ordersignal=0"
    start_urls = ['https://www.iwencai.com']
    rules = (
        # 如果url匹配到这些结果，follow是深度查询
        Rule(LinkExtractor(allow=r'/stockpick/.+\d{6}$'), callback='parse_info', follow=True),
        Rule(LinkExtractor(allow=r'/stockpick/.*$'), follow=True),
        # Rule(LinkExtractor(allow=r'/stockpick/.+qs=lm_.+'), follow=True),
        # Rule(LinkExtractor(allow=r'/stockpick/.+&qs=stockpick_tag$'), follow=True),

    )

    def parse_info(self, response):
        # print("found_url: %s"%response.url)

        try:
            print("获取【%s】的sel"%response.url)
            sel = response.css("div.simple_table_viewport")[0]
        except IndexError:
            print("页面未解析到response,重新下载")
            yield SplashRequest(response.url, endpoint='execute', args={'images': 0, 'lua_source': lua_script3}, cache_args=['lua_source'], callback=self.parse_info,dont_filter=True)
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





