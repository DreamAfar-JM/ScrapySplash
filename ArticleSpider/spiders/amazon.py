# -*- coding: utf-8 -*-


import json
import scrapy
import  os,sys
import requests
from scrapy.http import HtmlResponse
from scrapy.spiders import Rule,CrawlSpider
from scrapy_redis.spiders import RedisSpider
from scrapy.linkextractors import LinkExtractor
from ArticleSpider.items import AmazonItem,AmazonCommentItem

ProjectDir = os.path.abspath(os.path.dirname(__file__))
ProjectDir = os.path.abspath(os.path.dirname(ProjectDir))
ProjectDir = os.path.abspath(os.path.dirname(ProjectDir))
sys.path.insert(0, ProjectDir)

class amazonSpider(CrawlSpider,RedisSpider):
    name = 'amazon'
    allowed_domains = ['amazon.cn']
    redis_key = "amazon:start_urls"
    # start_urls = 'https://www.amazon.cn/gp/search/other/ref=sv_sa_0?ie=UTF8&pickerToList=brandtextbin&rh=n%3A2016156051'
    header = {
        "HOST": "www.amazon.cn",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests":"1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
    }
    # rules = (
    #     # 匹配类别和品牌
    #     Rule(LinkExtractor(allow=r'.*(Aapparel|ref=sr_pg_\d+).*'), follow=True),
    #     # Rule(LinkExtractor(allow=r'.*ref=sr_pg_\d+.*'), follow=True),
    #     Rule(LinkExtractor(allow=r'.*ref=sr_\d+_\d+.*'), follow=True),
    # )
    # def start_requests(self):
    #     #return [scrapy.Request("https://www.zhihu.com/#signin",headers=self.header,callback=self.login)]
    #     # 解析abcd页面
    #     print("已解析所有品牌页面")
    #     return [scrapy.Request(self.start_urls,headers=self.header,callback=self.parse_total)]


    def parse(self, response):
        print("开始解析品牌索引页")
        pattern = '.*Aapparel.*'
        le = LinkExtractor(allow=pattern)
        links = le.extract_links(response)
        for i in links:
            yield scrapy.Request(i.url,headers=self.header,callback=self.parse_brand)

    # 解析品牌函数
    def parse_brand(self,response):
        #
        print("开始解析品牌页")
        brand_pattern = '/s/ref=sr_in_[a-z]_p_\d+_\d+.*'
        brand_le = LinkExtractor(allow=brand_pattern)
        brand_links = brand_le.extract_links(response)
        for brand_link in brand_links:
            print("发现一个品牌页：【%s】" %brand_link.url)
            yield scrapy.Request(brand_link.url, headers=self.header, callback=self.parse_comm)

    # 解析商品链接函数
    def parse_comm(self, response):
        print("开始解析商品页面")
        comm_pattern = '.*ref=sr_\d+_\d+\?s=apparel.*'
        comm_le =  LinkExtractor(allow=comm_pattern)
        comm_links = comm_le.extract_links(response)
        for comm_link in comm_links:
            print("发现一个商品页：【%s】" %comm_link.url)
            yield scrapy.Request(comm_link.url, headers=self.header, callback=self.parse_shop)
        print("解析商品下页")
	    # next_pattern = '/s/ref=sr_pg_\d+.*'
        # next_le = LinkExtractor(allow=next_pattern)
        # next_links = next_le.extract_links(response)
        next_link_base = response.xpath('//a[@id="pagnNextLink"]/@href').extract_first()
        if next_link_base:
            next_url = "https://www.amazon.cn%s" %next_link_base
            yield scrapy.Request(next_url, headers=self.header, callback=self.parse_comm)


    def parse_shop(self, response):
        shop_info_item = AmazonItem()
        shop_comment_item = AmazonCommentItem()
        print("开始解析商品")
        # 商品ID
        shop_id = response.url.split("/")[4]
        # 品牌
        try:
            brand = " ".join(response.xpath('//a[@id="brand"]/text()').re("([A-Za-zA-Z0-9]+)[\n^\s+]"))
        except Exception:
            brand = response.xpath('//a[@id="brand"]/@href').re_first('/(.*)/b\?')
        # 商品链接
        url = response.url
        # 商品名称
        title = " ".join(response.xpath("//span[@id='productTitle']/text()").re("([a-zA-Z0-9]+)[\n^\s+]"))
        # 商品图url
        # image_url = response.xpath('//div[@id="imgTagWrapperId"]/img/@src').extract_first()
        price = response.xpath("//span[@id='priceblock_ourprice']/text()").re("(\d+\.\d+)")
        min_price = price[0]
        max_price = price[-1]
        # 评价数
        comment_num = response.xpath('//span[@id="acrCustomerReviewText"]/text()').re_first("(\d+)")
        try:
            shop_rank = "".join(response.xpath('//li[@id="SalesRank"]/text()').re("\d+"))
        except Exception:
            shop_rank = 0
        if comment_num:
            # 说明有评价数
            # 星级
            print("该商品有评价")
            star = response.xpath('//span[@id="acrPopover"]/@title').re_first("\d\.*\d*")
            # 解析评价
            # 获取评价url
            comment_url = "https://www.amazon.cn%s" %response.xpath('//a[@id="acrCustomerReviewLink"]/@href').extract_first()
            if int(comment_num) < 10:
                print("评价小于十条，直接在商品页面解析")
                present = response.xpath("//table[@id='histogramTable']//tr/td[last()]//text()").extract()
                five_proportion = present[0]
                four_proportion = present[1]
                three_proportion = present[2]
                two_proportion = present[3]
                one_proportion = present[4]
                comment_sel = response.xpath('//div[@id="cm-cr-dp-review-list"]/div[@id]')
                for comment in comment_sel:
                    commenter = comment.css(".a-row.a-spacing-mini>a::attr(href)").re_first(".*\.(.*)/")
                    comment_type = ",".join(comment.css("div.a-row.a-spacing-mini.review-data.review-format-strip >span.a-color-secondary::text").extract())
                    comment_text = comment.css("div.a-expander-content.a-expander-partial-collapse-content::text").extract_first()
                    comment_star = comment.css("i.a-icon.a-icon-star.a-star-5.review-rating ::text").re_first("\d+\.\d+")
                    shop_comment_item['five_proportion'] = five_proportion
                    shop_comment_item['shop_id'] = shop_id
                    shop_comment_item['four_proportion'] = four_proportion
                    shop_comment_item['three_proportion'] = three_proportion
                    shop_comment_item['two_proportion'] = two_proportion
                    shop_comment_item['one_proportion'] = one_proportion
                    shop_comment_item['comment_url'] = comment_url
                    shop_comment_item['comment_text'] = comment_text
                    shop_comment_item['comment_type'] = comment_type
                    shop_comment_item['commenter'] = commenter
                    shop_comment_item['comment_star'] = comment_star
                    yield shop_comment_item
            else:
                print("评价大于十条，return")
                yield scrapy.Request(comment_url, headers=self.header, callback=self.parse_comment)
        else:
            star = 0
            comment_num = 0
        print("开始赋值")
        shop_info_item['shop_id'] = shop_id
        shop_info_item['brand'] = brand
        shop_info_item['url'] = url
        shop_info_item['title'] = title
        # shop_info_item['image_url'] = image_url
        shop_info_item['comment_num'] = comment_num
        shop_info_item['star'] = star
        shop_info_item['min_price'] = min_price
        shop_info_item['max_price'] = max_price
        shop_info_item['shop_rank'] = shop_rank
        print("return 商品信息")
        yield shop_info_item



    def parse_comment(self,response):
        print("开始解析评价")
        shop_comment_item = AmazonCommentItem()
        # 商品ID
        try:
            shop_id = response.xpath('//div[@id="cm_cr-brdcmb"]//li[1]//a/@href').extract_first().split("/")[-2]
        except Exception:
            shop_id = response.url.split("/")[-2]
        # 评价星级占比
        present = response.xpath("//table[@id='histogramTable']//tr/td[last()]//text()").extract()
        five_proportion = present[0]
        four_proportion = present[1]
        three_proportion = present[2]
        two_proportion = present[3]
        one_proportion = present[4]

        # 评价数
        comment_num = int(response.xpath('//span[@data-hook="total-review-count"]/text()').extract_first())
        comment_url = response.url
        page_url_base = "https://www.amazon.cn%s" %response.xpath('//li[@class="a-last"]/a/@href').re_first('(.*)\d+$')
        page = (comment_num + 9) // 10
        session = requests.Session()
        if page > 1:
            for i in range(1,page+1):
                page_url = "%s%s" %(page_url_base,i)
                # url = urllib.parse.quote(page_url,safe=' /:?=.')
                # html = urlopen(url,timeout=5)
                html = session.get(page_url, headers=self.header)
                # new_response = HtmlResponse(url=url, body=html.read())
                new_response = HtmlResponse(url=page_url, body=html.text, encoding='utf-8')
                comment_sel = new_response.xpath("//div[@id='cm_cr-review_list']/div[@id]/div[@id]")
                for i in comment_sel:
                    commenter = i.xpath('./div[2]/span[1]/a/@href').re_first(".*\.(.*)/")
                    # 评价内容
                    comment_text = "".join(i.xpath('./div[4]/span/text()').extract())
                    # 评价商品类型
                    comment_type = "".join(i.xpath('./div[3]/a/text()').extract())
                    # 评价星级
                    comment_star = i.xpath('./div[1]/a/@title').re_first("\d\.*\d")
        else:
            comment_sel = response.xpath("//div[@id='cm_cr-review_list']/div[@id]/div[@id]")
            for i in comment_sel:
                commenter = i.xpath('./div[2]/span[1]/a/@href').re_first(".*\.(.*)/")
                # 评价内容
                comment_text = "".join(i.xpath('./div[4]/span/text()').extract())
                # 评价商品类型
                comment_type = "".join(i.xpath('./div[3]/a/text()').extract())
                # 评价星级
                comment_star = i.xpath('./div[1]/a/@title').re_first("\d\.*\d")

        # comment_text_all = json.dumps(comment_dic)
        shop_comment_item['five_proportion'] = five_proportion
        shop_comment_item['shop_id'] = shop_id
        shop_comment_item['four_proportion'] = four_proportion
        shop_comment_item['three_proportion'] = three_proportion
        shop_comment_item['two_proportion'] = two_proportion
        shop_comment_item['one_proportion'] = one_proportion
        # shop_comment_item['comment_text'] = comment_text_all
        # shop_comment_item['comment_response'] = response.text
        shop_comment_item['comment_url'] = comment_url
        shop_comment_item['comment_text'] = comment_text
        shop_comment_item['comment_type'] = comment_type
        shop_comment_item['commenter'] = commenter
        shop_comment_item['comment_star'] = comment_star

        return shop_comment_item