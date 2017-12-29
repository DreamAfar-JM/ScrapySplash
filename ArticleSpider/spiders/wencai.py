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
    splash:runjs("document.getElementsById('footbarCon').scrollIntoView(true)")
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
    splash:runjs("document.getElementsClassName('doctor_special_page_foot adaptive_foot1').scrollIntoView(true)")
    splash:wait(2)
    return splash:html()
end
"""

class WencaiSpider(scrapy.Spider):
    name = "wencai"
    allowed_domains = ["iwencai.com"]
    start_url = "https://www.iwencai.com/stockpick?my=0&ordersignal=0"
    url_list = []
    def start_requests(self):
        # 请求第一页
        print("开始爬取首页")
        yield Request(self.start_url, callback=self.shares_list)
        # yield SplashRequest(self.start_url, endpoint='execute', args={'lua_source': lua_script}, cache_args=['lua_source'])
    def shares_list(self,response):
        pattern = '/stockpick/.*'
        pattern_deny = '/stockpick/.+index_name.*'
        pattern_deny2 = '/stockpick/.+ts=1$'
        le = LinkExtractor(allow=pattern,deny=pattern_deny)
        links = le.extract_links(response)
        print("开始解析股票列表")
        # print(response.url)
        for link in links:
            print("发现一个股票列表页面:%s" %(link.url))
            yield SplashRequest(link.url, endpoint='execute', args={'images': 0, 'lua_source': lua_script},
                                cache_args=['lua_source'], callback=self.parse_num_url)
            # SplashRequest(link.url, endpoint='execute', args={'images': 0, 'lua_source': lua_script},cache_args=['lua_source'], callback=self.parse_num_url, splash_url=)

    def parse_num_url(self,response):
        # link_list = []
        # pattern2 = '/stockpick/.+qs=lm_.+'
        # le2 = LinkExtractor(allow=pattern2)
        # links2 = le2.extract_links(response)
        # for link2 in links2:
        #     print("获取到qs股票列表页：%s" % link2.url)
        #     # if link2.url not in self.url_list:
        #     # self.url_list.append(link2.url)
        #     yield SplashRequest(link2.url, endpoint='execute', args={'images': 0, 'lua_source': lua_script},
        #                         cache_args=['lua_source'], callback=self.parse_num_url)
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


        page_num = response.css("span.num::text").re_first("(\d+)")
        print(page_num)
        # 总条数除以每页显示的数目如果大于一即有下页
        page_count = int(page_num) // 30 + 1
        print("总共股票代码数：%s，页数：%s" % (page_num, page_count))
        if page_count != 1:
            # 判断当前页面是否已经点击过下页标签
            if response.url not in self.url_list:
                # 如果没有被点击过就先把他加入到已经点击过的列表中，然后执行点击操作
                self.url_list.append(response.url)
                # 根据时间情况进行标签提取，然后点击对应的标签
                for i in range(2, page_count + 1):
                    lua_script2 = """
                            function main(splash)
                                splash:go(splash.args.url)
                                splash:wait(2)
                                splash:runjs("$('.pagination > a')[%s].click()")
                                splash:wait(2)
                                return splash:html()
                            end
                            """ % (i)
                    print("获取第%s页" % i)
                    # 进行点击操作，使用的是上面的lua脚本，此项目是点击class name为pagination下的a标签的按钮
                    # 其中[%s]表示第几个，此项目为第几页，按需分析
                    # dont_filter开启，避免被scrapy去重
                    yield SplashRequest(response.url, endpoint='execute', args={'images': 0, 'lua_source': lua_script2},
                                        cache_args=['lua_source'], callback=self.parse_num_url, dont_filter=True)



    def parse(self, response):
        # print("found_url: %s"%response.url)

        try:
            print("获取【%s】的sel"%response.url)
            sel = response.css("div.simple_table_viewport")[0]
        except IndexError:
            print("页面未解析到response,重新下载")
            yield SplashRequest(response.url, endpoint='execute', args={'images': 0, 'lua_source': lua_script3}, cache_args=['lua_source'], callback=self.parse,dont_filter=True)
            print("重新下载URL：%s" %response.url)
        else:
            print("获取到sel")
            # pattern3 = '/stockpick/.+&qs=stockpick_tag$'
            # print("匹配到tag结尾的股票列表")
            # le3 = LinkExtractor(allow=pattern3)
            # links3 = le3.extract_links(response)
            # for link3 in links3:
            #     print("tag url:%s" %link3.url)
            #     #if link3.url not in self.url_list:
            #     yield SplashRequest(link3.url, endpoint='execute', args={'images': 0, 'lua_source': lua_script},
            #                             cache_args=['lua_source'], callback=self.parse_num_url)
            #     print("url:%s已被yield" %link3.url)
                    #self.url_list.append(link3.url)
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





