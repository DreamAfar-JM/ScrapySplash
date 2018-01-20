# -*- coding: utf-8 -*-

import os,sys
ProjectDir = os.path.abspath(os.path.dirname(__file__))
ProjectDir = os.path.abspath(os.path.dirname(ProjectDir))
ProjectDir = os.path.abspath(os.path.dirname(ProjectDir))
sys.path.insert(0, ProjectDir)
import scrapy
import json
import requests
from scrapy.linkextractors import LinkExtractor
# from scrapy.spiders import Rule,CrawlSpider
from scrapy.spiders.splashcrawl import Rule,CrawlSpider
from ArticleSpider.scrapy_redis_plus.spiders import RedisSpider
from ArticleSpider.items import JDAllItem

class JdAllSpider(RedisSpider, CrawlSpider):
    name = "jd_all"
    redis_key = "jd:start_urls"
    allowed_domains = ["jd.com"]
    header = {
        'Host': 'club.jd.com',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
    }
    rules = {
        # 商品列表
        Rule(LinkExtractor(allow=r'https://list\.jd\.com/list\.html\?cat=.*'), follow=True,callback="parse_shop"),
        # 匹配商品
        # Rule(LinkExtractor(allow=r'.*item\.jd\.com/\d+\.html$'), callback="parse_shop",follow=True),
        # 匹配下一页
        Rule(LinkExtractor(restrict_css='a.pn-next'), follow=True,callback="parse_shop"),
    }

    def parse_shop(self, response):
        sel_list = response.xpath('//div[@id="plist"]').xpath('.//li[@class="gl-item"]')
        for sel in sel_list:
            print("开始解析list页面，商品信息")
            url = "http:%s" %sel.css(".p-name a::attr('href')").extract_first()
            shop_id = url.split("/")[-1].split(".")[0]
            title = sel.css(".p-name a em::text").extract_first().strip("\n").strip(" ")
            brand = sel.css(".p-shop ::attr('data-shop_name')").extract_first()
            brand_url = sel.css(".p-shop span a::attr('href')").extract_first()
            price = sel.css(".p-price strong i::text").extract_first()
            session = requests.Session()
            print("获取%s商品评价页面" %title)
            comment_url = "https://club.jd.com/comment/skuProductPageComments.action?productId={shop_id}&score=0&sortType=5&page={page_num}&pageSize=10&isShadowSku=0&fold=1".format(shop_id=shop_id,page_num=0)
            html = session.get(comment_url, headers=self.header)
            print("获取商品评价页 json")
            try:
                comment_json = json.loads(html.text)
            except:
                continue
            # 获取评价信息
            public_comment = comment_json['productCommentSummary']
            # 评价数
            comment_num = public_comment['commentCount']
            # 获取好评率
            good_comment_rate = public_comment['goodRate']
            # 好评数
            good_comment =public_comment['goodCount']
            # 中评数
            general_count = public_comment['generalCount']
            # 差评
            poor_count = public_comment['poorCount']
            # 默认好评
            default_comment_num = public_comment['defaultGoodCount']
            # 获取热评信息
            hot_comment = comment_json['hotCommentTagStatistics']
            if len(hot_comment) == 0:
                hot_comment_dict = "Null"
            else:
                hot_comment_dict = {}
                for i in hot_comment:
                    hot_comment_dict[i['id']] = {'name': i['name'], 'count': i['count']}
                hot_comment_dict = json.dumps(hot_comment_dict)
            shop_info = {
                'url': url,
                'shop_id': shop_id,
                'title': title,
                'brand': brand,
                'brand_url': brand_url,
                'price': price,
                'comment_num': comment_num,
                'good_comment_rate': good_comment_rate,
                'good_comment': good_comment,
                'general_count': general_count,
                'poor_count': poor_count,
                'hot_comment_dict': hot_comment_dict,
                'default_comment_num': default_comment_num,
            }
            page_num = (comment_num + 9) // 10
            if page_num >= 100:
                page_num = 100
            print("%s评价页面共计%s" %(title,page_num))
            for page in range(0,page_num):
                comment_url = "https://club.jd.com/comment/skuProductPageComments.action?productId={shop_ids}&score=0&sortType=5&page={page_nums}&pageSize=10&isShadowSku=0&fold=1".format(shop_ids=shop_id,page_nums=page)
                print("yield评价第%s页"%page)
                yield  scrapy.Request(comment_url,meta=shop_info,headers=self.header)


    def parse_comment(self,response):
        print("开始解析评价")
        shop_id = response.meta.get("shop_id")
        url = response.meta.get("url")
        title = response.meta.get("title")
        brand = response.meta.get("brand")
        brand_url = response.meta.get("brand_url")
        price = response.meta.get("price")
        comment_num = response.meta.get("comment_num")
        good_comment_rate = response.meta.get("good_comment_rate")
        good_comment = response.meta.get("good_comment")
        general_count = response.meta.get("general_count")
        poor_count = response.meta.get("poor_count")
        hot_comment_dict = response.meta.get("hot_comment_dict")
        default_comment_num = response.meta.get("default_comment_num")
        comment_json = json.loads(response.text)
        comment_info = comment_json['comments']
        for comment in comment_info:
            JDItem = JDAllItem()
            # 主键 评论ID
            comment_id = comment['id']
            comment_context = comment['content']
            comnent_time = comment['creationTime']
            # 用户评分
            comment_score = comment['score']
            # 来源
            comment_source = comment['userClientShow']
            if comment_source == []:
                comment_source = "非手机端"
            # 型号
            produce_size = comment['productSize']
            # 颜色
            produce_color = comment['productColor']
            # 用户级别
            user_level = comment['userLevelName']
            # 用户京享值
            user_exp = comment['userExpValue']
            # 评价点赞数
            comment_thumpup = comment['usefulVoteCount']
            # 店铺回复
            try:
                comment_reply = comment['replies']
            except:
                comment_reply = []
            if len(comment_reply) == 0:
                comment_reply_content = "Null"
                comment_reply_time = "Null"
            else:
                comment_reply_content = comment_reply[0]["content"]
                comment_reply_time = comment_reply[0]["creationTime"]
            JDItem["shop_id"] = shop_id
            JDItem["url"] = url
            JDItem["title"] = title
            JDItem["brand"] = brand
            JDItem["brand_url"] = brand_url
            JDItem["price"] = price
            JDItem["comment_num"] = comment_num
            JDItem["good_comment_rate"] = good_comment_rate
            JDItem["good_comment"] = good_comment
            JDItem["general_count"] = general_count
            JDItem["poor_count"] = poor_count
            JDItem["hot_comment_dict"] = hot_comment_dict
            JDItem["default_comment_num"] = default_comment_num
            JDItem["comment_id"] = comment_id
            JDItem["comment_context"] = comment_context
            JDItem["comnent_time"] = comnent_time
            JDItem["comment_score"] = comment_score
            JDItem["comment_source"] = comment_source
            JDItem["produce_size"] = produce_size
            JDItem["produce_color"] = produce_color
            JDItem["user_level"] = user_level
            JDItem["user_exp"] = user_exp
            JDItem["comment_thumpup"] = comment_thumpup
            JDItem["comment_reply_content"] = comment_reply_content
            JDItem["comment_reply_time"] = comment_reply_time
            print("yield评价")
            yield  JDItem

