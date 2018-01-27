# -*- coding: utf-8 -*-
import scrapy
import os,sys
ProjectDir = os.path.abspath(os.path.dirname(__file__))
ProjectDir = os.path.abspath(os.path.dirname(ProjectDir))
ProjectDir = os.path.abspath(os.path.dirname(ProjectDir))
sys.path.insert(0, ProjectDir)
import json
from ArticleSpider.items import ALIExpressItem,ALIExpressCommentItem
from scrapy.linkextractors import LinkExtractor
from scrapy_redis.spiders import RedisSpider
from scrapy.xlib.pydispatch import dispatcher
from scrapy.http import HtmlResponse
from scrapy import signals
from selenium import webdriver
import re

class AliexpressSpider(RedisSpider):
    name = "aliexpress"
    allowed_domains = ["aliexpress.com"]
    # start_urls = ['https://www.aliexpress.com/all-wholesale-products.html?spm=2114.11010108.22.1.7c337f90UDp63a']
    cate_header = {
        ':authority': 'www.aliexpress.com',
        ':method': 'GET',
        ':path': '/all-wholesale-products.html',
        ':scheme': 'https',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, sdch',
        'accept-language': 'zh-CN,zh;q=0.8',
        'upgrade-insecure-requests': '1',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://www.aliexpress.com/all-wholesale-products.html?spm=2114.11010108.22.1.7c337f90UDp63a',
    }
    comment_header = {
        ':authority': 'feedback.aliexpress.com',
        ':method': 'POST',
        ':path': '/display/productEvaluation.htm',
        ':scheme': 'https',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'zh-CN,zh;q=0.8',
        'cache-control': 'max-age=0',
        'content-length': '379',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://feedback.aliexpress.com',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'
    }

    # def __init__(self):
    #     self.browser = webdriver.PhantomJS(executable_path="D:/python/scrapy/scrapy/tools/phantomjs-2.1.1-windows/phantomjs-2.1.1-windows/bin/phantomjs.exe")
    #     super(AliexpressSpider, self).__init__()
    #     dispatcher.connect(self.spider_closed, signals.spider_closed)
    #
    # def spider_closed(self, spider):
    #     # 当爬虫退出的时候关闭chrome
    #     print("spider closed")
    #     self.browser.quit()

    def parse(self, response):
        # 获取所有分类URL
        cate_pattern = ".*category/\d+/.*"
        cate_le = LinkExtractor(allow=cate_pattern)
        links = cate_le.extract_links(response)
        print("获取商品分类共计：【%s】" %len(links))
        for link in links:
            if "isCates=y" in link.url:
                yield scrapy.Request(link.url, callback=self.parse)
            else:
                print("下载商品分类页：【%s】" %link.url)
                yield scrapy.Request(link.url,headers=self.cate_header,callback=self.parse_cate)

    def parse_cate(self, response):
        shop_header = {
            ':authority': 'www.aliexpress.com',
            ':method': 'GET',
            ':path': '/all-wholesale-products.html',
            ':scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, sdch',
            'accept-language': 'zh-CN,zh;q=0.8',
            'upgrade-insecure-requests': '1',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': response.url,
        }
        # 解析当前分类的商品
        print("开始解析商品分类页商品")
        shop_pattern = ".*item.*\d+\.html.*"
        shop_le = LinkExtractor(allow=shop_pattern)
        shop_links = shop_le.extract_links(response)
        current_cate_url = response.url
        for shop_link in shop_links:
            print("yield商品页面【%s】" %shop_link.url)
            yield scrapy.Request(shop_link.url, meta={'shop_cate_url': current_cate_url}, headers=shop_header, callback=self.parse_shop)

        # 解析商品下页
        next_le = LinkExtractor(restrict_css='a.page-next.ui-pagination-next')
        if next_le:
            print("下载下页")
            next_links = next_le.extract_links(response)
            next_url = next_links[0].url
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>已被yield")
            yield scrapy.Request(next_url, headers=self.cate_header, callback=self.parse_cate)

    def parse_shop(self, response):
    # def parse(self, response):
        # 解析商品信息
        print("开始解析商品信息")
        shop_url = response.url
        shop_cate_url = response.meta.get('shop_cate_url')
        shop_id = shop_url.split(".html")[0].split("/")[-1]
        owner_member_id = response.xpath("//a[@data-id1]/@data-id1").extract_first()
        shop_title = response.xpath("//h1[@class='product-name']/text()").extract_first()
        brand = response.xpath("//li[@id='product-prop-2']/@data-title").extract_first()
        store_url = response.xpath("//a[@class='store-lnk']/@href").extract_first()
        store_name = response.xpath("//a[@class='store-lnk']/@title").extract_first()
        store_address = response.xpath("//dd[@class='store-address']/text()").extract_first().strip("\n").strip("\t")
        min_price = response.xpath("//span[@id='j-sku-price']//text()").re("(\d+.\d+)")[0]
        max_price = response.xpath("//span[@id='j-sku-price']//text()").re("(\d+.\d+)")[-1]
        discount_price = response.xpath("//span[@id='j-sku-discount-price']//text()").re("(\d+.\d+)")
        try:
            min_discount_price = discount_price[0]
            max_discount_price = discount_price[-1]
        except:
            min_discount_price = "None"
            max_discount_price = "None"
        # try:
        #     shop_color = "|".join(response.xpath("//ul[@id='j-sku-list-1']//li/a/@title").extract())
        # except:
        #     shop_color = "None"
        shop_info = {}
        shop_info_ele = response.xpath("//div[@id='j-product-info-sku']/dl")
        print("解析商品info")
        for i in shop_info_ele:
            key = i.xpath("./dt/text()").extract_first().strip(":")
            if key == 'Color':
                value = "|".join(i.xpath("./dd/ul//li/a/@title").extract())
            else:
                value = "|".join(i.xpath("./dd/ul//li/a//text()").extract())
            shop_info[key] = value
        shop_info = json.dumps(shop_info)
        shop_star_ele = response.xpath("//div[@class='product-star-order util-clearfix']")
        if shop_info_ele:
            shop_star = response.xpath("//span[@class='percent-num']/text()").extract_first()
            shop_comment_num = response.xpath("//span[@class='rantings-num']/text()").re_first("(\d+)")
            order_num = response.xpath("//span[@id='j-order-num']/text()").re_first("(\d+)")
        else:
            shop_star = 0
            shop_comment_num = 0
            order_num = 0
        ALIItem = ALIExpressItem()
        ALIItem["shop_url"] = shop_url
        ALIItem["shop_cate_url"] = shop_cate_url
        ALIItem["shop_id"] = shop_id
        ALIItem["owner_member_id"] = owner_member_id
        ALIItem["shop_title"] = shop_title
        ALIItem["brand"] = brand
        ALIItem["store_url"] = store_url
        ALIItem["store_name"] = store_name
        ALIItem["store_address"] = store_address
        ALIItem["min_price"] = min_price
        ALIItem["max_price"] = max_price
        ALIItem["min_discount_price"] = min_discount_price
        ALIItem["max_discount_price"] = max_discount_price
        ALIItem["shop_info"] = shop_info
        ALIItem["shop_star"] = shop_star
        ALIItem["shop_comment_num"] = shop_comment_num
        ALIItem["order_num"] = order_num
        # yield ALIItem
        # print(ALIItem)
        if int(shop_comment_num) > 0:
            # csrf = response.xpath("//input[@name='_csrf_token']/@value").extract_first()
            # post_data = {
            #     'ownerMemberId': owner_member_id,
            #     'memberType': 'seller',
            #     'productId': shop_id,
            #     'companyId': '',
            #     'evaStarFilterValue': 'all+Stars',
            #     'evaSortValue': 'sortdefault%40feedback',
            #     'startValidDate': '',
            #     'i18n': 'false',
            #     'withPictures': 'false',
            #     'withPersonalInfo': 'false',
            #     'withAdditionalFeedback': 'false',
            #     'onlyFromMyCountry': 'false',
            #     'version': 'evaNlpV1_2',
            #     'isOpened': 'true',
            #     'translate': 'N',
            #     'jumpToTop': 'true',
            #     '_csrf_token': csrf,
            #     'cookie':"ali_apache_id=10.181.239.78.1516929500833.251809.3; ali_beacon_id=10.181.239.78.1516929500833.251809.3; cna=t06cErYUG2ICAXzMJ3J5ywv2; xman_f=EsLE6yMtAlhB57s3ff1SQ79aJBSyGdW7I9us836itrXzEwdNrlUwGy/Yr9nJtS5NoDB0sliTjef0ihOZldfZi9lUpWHqYuYcOhd5gkKIoCmn6vvndSAZ7Q==; xman_t=z7aYzmi5qFcwg24eFWPhtAnr1eMEd+L5mn+bNTM6rHpNZWLluAJDIWpKiD2BMzmD; JSESSIONID=FF6YLB92P2-V82SHB0WSOKWNOF4POHU1-AJ8HQWCJ-U2H1; _ga=GA1.2.1985639487.1516929540; _gid=GA1.2.1158165113.1516929540; aep_history=keywords%5E%0Akeywords%09%0A%0Aproduct_selloffer%5E%0Aproduct_selloffer%0932833357781%0932848247976%0932845079303%0932822314757%0932788550019%0932812756937%0932830536197%0932796690098; acs_usuc_t=acs_rt=72d60d830beb4aeeb1edaa43954fe860&x_csrf=9z5dhs1c0g1e; xman_us_f=x_l=1&x_locale=en_US; aep_usuc_f=site=glo&region=US&b_locale=en_US&c_tp=USD; intl_locale=en_US; intl_common_forever=xCC7hc9bR42HFpGckGxZkNWUncmbi2ztfLDnvKKYzB1u6AHeHdBm5w==; ae_eva_app_forever=transalte_eva_content_flag=Y; _mle_tmp0=eNotyEkOgjAAAMAHGD%2FhGUKLpSyeRISKSMEGGokJMbUQoqIsB5f4dy%2FOcciUrRnb0LjcUW8dgeOnOTsz38eHyLX1RFdzS2fEBZzRLY%2BpjxJKMqguQ4ukfBWqmU7gTBGjAw1ogjmysAnMuXIS%2FzCwDRBCyu3pgO%2BkFENfleP9IluwqKVM01c1xDkTta2JQV4fQdvxZv%2FKoDZgjx7k%2BA5F1AVQw4bHmn7Zc6vKC6P4AXWGNhQ%3D; isg=BBMTRtryTVZxIAEENL14KFGkrJc9yKeKlBnEucUwbzJpRDPmTZg32nGWerYqf_-C"
            # }
            page_num = (int(shop_comment_num) + 9) // 10
            comment_base_url = "https://feedback.aliexpress.com/display/productEvaluation.htm?productId={shop_id}&ownerMemberId={member_id}".format(shop_id=shop_id,member_id=owner_member_id)
            # yield ALIItem, self.parse_comment(shop_id,page_num,comment_base_url)
            print("商品有评价【%s】条，yield商品和评价"%shop_comment_num)
            yield ALIItem,  self.parse_comment(shop_id,page_num,comment_base_url)
        else:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>商品无评价，直接yield商品信息")
            yield ALIItem
    def parse_comment(self,shop_id,page_num, comment_base_url):
        print("开始解析评价，创建browser")
        # browser = webdriver.PhantomJS(executable_path="D:/python/scrapy/scrapy/tools/phantomjs-2.1.1-windows/phantomjs-2.1.1-windows/bin/phantomjs.exe")
        # linux
        browser = webdriver.PhantomJS("phantomjs")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>打开页面")
        browser.get(comment_base_url)
        comment_index_response = HtmlResponse(url=browser.current_url, body=browser.page_source, encoding="utf-8")
        yield self.yield_comment(comment_index_response,shop_id)
        if page_num >= 1:
            print("评价页数为【%s】超过1，开始点击下页" %page_num)
            for i in range(page_num):
                browser.find_element_by_css_selector(".ui-pagination-next.ui-goto-page").click()
                print("已点击第【%s】页" %i+1)
                new_response = HtmlResponse(url=browser.current_url, body=browser.page_source, encoding="utf-8")
                print("新response已创建，准备yield")
                yield self.yield_comment(new_response,shop_id)
        print("此商品评价页面已经全部yield，退出关闭browser")
        browser.quit()

    def yield_comment(self,response,shop_id):
        ALIEComment = ALIExpressCommentItem()
        print("开始解析页数不为1的评价")
        shop_id = shop_id
        comment_le = response.xpath("//div[@class='feedback-list-wrap']//div[@class='feedback-item clearfix']")
        for i in comment_le:
            member_id = i.xpath(".//span[@class='user-name']/a/@href").re_first("ownerMemberId=(.*)&memberType=.*")
            member_country = i.xpath(".//div[@class='user-country']//text()").extract_first()
            comment_time = i.xpath(".//dd[@class='r-time']//text()").extract_first()
            order_info = re.sub(r'\s+','',"|".join(i.xpath(".//div[@class='user-order-info']//text()").extract()))
            comment_text = i.xpath(".//dt[@class='buyer-feedback']/span/text()").extract_first()
            comment_thumpup = i.xpath(".//span[@class='r-digg-count']/text()").re_first("(\d+)")
            append_comment = i.xpath(".//dt[@class='buyer-addition-feedback']/text()").extract_first()
            if append_comment:
                append_comment_time = i.xpath(".//dl[@class='buyer-additional-review']/dd[@class='r-time']/text()").extract_first()
            else:
                append_comment = "None"
                append_comment_time = "None"

            seller_replay = i.xpath(".//dl[@class='seller-reply']")
            if seller_replay:
                replay_text = seller_replay.xpath("./dd[@class='r-fulltxt']/text()").extract_first()
                replay_text_time = seller_replay.xpath("./dd[@class='r-time']/text()").extract_first()
            else:
                replay_text = "None"
                replay_text_time = "None"

            ALIEComment['shop_id'] = shop_id
            ALIEComment['member_id'] = member_id
            ALIEComment['member_country'] = member_country
            ALIEComment['comment_time'] = comment_time
            ALIEComment['order_info'] = order_info
            ALIEComment['comment_text'] = comment_text
            ALIEComment['comment_thumpup'] = comment_thumpup
            ALIEComment['append_comment'] = append_comment
            ALIEComment['append_comment_time'] = append_comment_time
            ALIEComment['replay_text'] = replay_text
            ALIEComment['replay_text_time'] = replay_text_time
            print("yield 评价")
            yield ALIEComment
            # print(ALIEComment)
