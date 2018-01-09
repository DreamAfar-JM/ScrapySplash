# -*- coding: utf-8 -*-
from urllib import parse

from ArticleSpider.items import JobBoleArticleItem,ArticleItemLoader
from scrapy.http import Request
from scrapy_redis.spiders import RedisSpider
import os,sys
ProjectDir = os.path.abspath(os.path.dirname(__file__))
ProjectDir = os.path.abspath(os.path.dirname(ProjectDir))
ProjectDir = os.path.abspath(os.path.dirname(ProjectDir))
sys.path.insert(0, ProjectDir)

#class JobboleSpider(scrapy.Spider):
#基于分布式redis
class JobboleSpider(RedisSpider):
    name = "jobbole"
    allowed_domains = ["blog.jobbole.com"]
    #start_urls = ['http://blog.jobbole.com/all-posts/']
    redis_key = "jobbole:start_urls"
    start_urls = ['http://blog.jobbole.com/all-posts/']
    def parse(self, response):
        #获取当前页所有的文章的url
        #AllUrl = response.css("#archive .post-thumb a::attr(href)").extract()
        PostNodes = response.css("#archive .post-thumb a") #首先获取这个对象，之后在进行取值
        for PostNode in PostNodes:
            #ImageUrl = PostNode.css("img::attr(src)").extract_first("") #获取当前文章的封面图
            URL = PostNode.css("::attr(href)").extract_first("")       #获取当前文章的URL
            yield Request(url=parse.urljoin(response.url,URL),callback=self.parse_func)
            #yield Request(url=parse.urljoin(response.url, URL),meta={"FrontImageUrl": ImageUrl}, callback=self.parse_func)

        #获取下一页的url
        NextPage = response.xpath("//a[@class='next page-numbers']/@href").extract()
        #CSS获取下一页response.css(".next.page-numbers::attr(href)").extract()
        if NextPage:
            yield Request(url=parse.urljoin(response.url,NextPage[0]),callback=self.parse)


    def parse_func(self,response):
        #获取文章封面图片,用上述request代码的meta获取
        #FrontImageUrl = response.meta.get("FrontImageUrl","")
        # #获取文章标题
        # Title =  response.xpath('//div[@class="entry-header"]/h1/text()').extract()[0]
        # #获取文章创建时间
        # CreateTime = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace(" ·","")
        # try:
        #     CreateTime = datetime.datetime.strptime(CreateTime,"%Y/%m/%d")
        # except Exception as e:
        #     CreateTime = datetime.datetime.now().date()
        # #获取点赞数
        # VoteNum = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract()
        # #如果数目为空则为0次
        # if VoteNum:
        #     VoteNum = int(VoteNum[0])
        # else:
        #     VoteNum = 0
        # #获取收藏数
        # BookMarkNum = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract()[0].strip("收藏").strip()
        # if not BookMarkNum:
        #     BookMarkNum = 0
        # else:
        #     BookMarkNum = int(BookMarkNum)
        # #获取评论数
        # ArticleComment = response.xpath('//a[@href="#article-comment"]/span/text()').extract()[0].replace("评论","").strip()
        # if not ArticleComment:
        #     ArticleComment = 0
        # else:
        #     ArticleComment = int(ArticleComment)
        #获取文章内容
        #Content = response.css("div.entry").extract()[0]

        #实例化items的JobBoleArticleItem，并填充自定义的值
        # ArticleItem = JobBoleArticleItem()
        # ArticleItem["FrontImageMD5"] = get_md5(response.url)
        # ArticleItem["Title"] = Title
        # ArticleItem["URL"] = response.url
        # ArticleItem["CreateTime"] = CreateTime
        # #下载图片需要用集合形式的URL
        # ArticleItem["FrontImageUrl"] = FrontImageUrl
        # ArticleItem["VoteNum"] = VoteNum
        # ArticleItem["BookMarkNum"] = BookMarkNum
        # ArticleItem["ArticleComment"] = ArticleComment
        # ArticleItem["Content"] = Content
        #通过itemloader机制填充ArticleItem的值
        ArticleItem = ArticleItemLoader(item=JobBoleArticleItem(),response=response)
        ArticleItem.add_css("Title",".entry-header h1::text")
        ArticleItem.add_value("URL",response.url)
        #ArticleItem.add_value("FrontImageMD5",get_md5(response.url))
        #ArticleItem.add_css("CreateTime","p.entry-meta-hide-on-mobile::text".strip().replace(" ·",""))
        ArticleItem.add_xpath("CreateTime",'//p[@class="entry-meta-hide-on-mobile"]/text()')
        #ArticleItem.add_value("FrontImageUrl",[FrontImageUrl])
        ArticleItem.add_css("VoteNum",".vote-post-up h10::text")
        ArticleItem.add_css("ArticleComment","a[href='#article-comment'] span::text")
        ArticleItem.add_css("BookMarkNum",".bookmark-btn::text")
        ArticleItem.add_css("Content","div.entry")
        ArticleItemLoder = ArticleItem.load_item()

        yield ArticleItemLoder

        #pass
