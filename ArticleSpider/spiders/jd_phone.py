# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy_splash import SplashRequest
from ArticleSpider.items import JDPhoneItem,ArticleItemLoader

lua_script = """
function main(splash)
    splash:go(splash.args.url)
    splash:wait(2)
    splash:runjs("document.getElementsByClassName('pn-next')[0].scrollIntoView(true)")
    splash:wait(2)
    return splash:html()
end
"""

class JdPhoneSpider(scrapy.Spider):
    name = "jd_phone"
    allowed_domains = ["search.jd.com"]
    # start_urls = ['http://list.jd.com/']
    base_url = "https://search.jd.com/Search?keyword=手机&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=手机&cid2=653&cid3=655"
    start_url = "https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&wq=%E6%89%8B%E6%9C%BA&pvid=7331c1cde7aa43498514880caa2bfe24"

    def start_requests(self):
        # 请求第一页
        yield Request(self.start_url, callback=self.parse_urls, dont_filter=True)
        # yield SplashRequest(self.start_url, endpoint='execute', args={'lua_source': lua_script}, cache_args=['lua_source'])

    def parse_urls(self,response):
        # total = int(response.css('span.p-skip em b::text').extract_first()) + 1
        total  = int(response.css('div#J_topPage i::text').extract_first()) + 1
        #page_num = total // 60 + (1 if total % 60 else 0)
        for i in range(total):
            url = "%s&page=%s" %(self.base_url, 2*i+1)
            yield SplashRequest(url, endpoint='execute', args={'images':0, 'lua_source': lua_script}, cache_args=['lua_source'])
    def parse(self, response):
        for sel in response.css('ul.gl-warp.clearfix > li.gl-item'):
            phone_name = sel.css('div.p-name.p-name-type-2').xpath('string(.//em)').extract_first()
            price = int(sel.css('div.p-price i::text').re_first('(\d+)'))
            phone_url = sel.css('div.p-name a::attr("href")').re_first('//(.*)')
            PhoneAritleItem = JDPhoneItem()
            PhoneAritleItem['phone_name'] = phone_name
            PhoneAritleItem['price'] = price
            PhoneAritleItem['phone_url'] = phone_url

            yield PhoneAritleItem

