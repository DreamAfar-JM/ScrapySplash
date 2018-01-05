# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy_splash import SplashRequest
from ArticleSpider.items import SaveToRedisItem
from scrapy.linkextractors import LinkExtractor
from scrapy_redis.spiders import RedisSpider

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

class WencaiSpider(RedisSpider):
    name = "wencai"
    allowed_domains = ["iwencai.com"]
    # start_url = "https://www.iwencai.com/stockpick?my=0&ordersignal=0"
    url_list = []
    def parse(self,response):
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
            # SplashRequest(link.url, endpoint='execute', args={'images': 0, 'lua_source': lua_script},cache_args=['lua_source'], callback=self.parse_num_url, splash_url=)

    def parse_num_url(self,response):
        # link_list = []
        print("开始解析股票页面")
        pattern = '/stockpick/.+\d{6}$'
        le = LinkExtractor(allow=pattern)
        num_links = le.extract_links(response)
        for num_link in num_links:
            print("解析到股票详情页：%s" % num_link.url)
            saveItem = SaveToRedisItem()
            url = num_link.url
            id = url.split('=')[-1]
            saveItem['id'] = id
            saveItem['url'] = url
            yield saveItem
        pattern2 = '/stockpick/.+qs=lm_.+'
        le2 = LinkExtractor(allow=pattern2)
        links2 = le2.extract_links(response)
        for link2 in links2:
            print("获取到qs股票列表页：%s" %link2.url)
            #if link2.url not in self.url_list:
                #self.url_list.append(link2.url)
            yield SplashRequest(link2.url, endpoint='execute', args={'images': 0, 'lua_source': lua_script}, cache_args=['lua_source'], callback=self.parse_num_url)

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



    # def save_to_redis(self, num_links):





