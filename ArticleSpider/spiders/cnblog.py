# -*- coding: utf-8 -*-

from scrapy.linkextractors import LinkExtractor
# from scrapy.spiders.splashcrawl import Rule,CrawlSpider
from scrapy_redis.spiders import RedisSpider
from ArticleSpider.items import CNBlogItem
from scrapy.spiders import Rule,CrawlSpider


class cnblogSpider(CrawlSpider,RedisSpider):
    name = 'cnblog'
    allowed_domains = ['www.cnblogs.com']
    redis_key = "cnblog:start_urls"
    url_list = []
    deny = ['www.cnblogs.com/new/']
    rules = (
        # 获取网站分类
        # Rule(LinkExtractor(allow=r'/cate/.*/$'), follow=True),
        # 匹配博主
        Rule(LinkExtractor(allow=r'/\w+/$',deny_domains=deny), follow=True),
        # 匹配下页
        Rule(LinkExtractor(allow=r'/sitehome/p/\d+$',deny_domains=deny), follow=True),
        Rule(LinkExtractor(allow=r'/cate/all/($|\d+)',deny_domains=deny), follow=True),
        # 匹配博客
        Rule(LinkExtractor(allow=r'.*/p/.+\.html$',deny_domains=deny), callback="parse_job", follow=True),
        # Rule(LinkExtractor(allow=r'.*/page/\d+/$',deny_domains=deny), callback="parse_job", follow=True),

    )

    def parse_job(self, response):
        print("正在解析:%s" %response.url)
        author = response.url.split("/")[3]
        fans = response.css('#author_profile_detail>a:last-child::text').re_first('(\d+)')
        # author_total_comment =  response.css('#blog_stats>span:last-child::text').re_first('(\d+)')
        title = response.css('#cb_post_title_url::text').extract_first()
        content = response.css('#cnblogs_post_body').extract_first()
        post_date = response.css('#post-date::text').extract_first()
        class_ification = ",".join(response.css("#BlogPostCategory a::text").extract())
        tag = ",".join(response.css("#EntryTag a::text").extract())
        url = response.url
        BlogItem = CNBlogItem()
        BlogItem['author'] = author
        BlogItem['fans'] = fans
        BlogItem['title'] = title
        BlogItem['content'] = content
        BlogItem['post_date'] = post_date
        BlogItem['class_ification'] = class_ification
        BlogItem['tag'] = tag
        BlogItem['url'] = url
        return BlogItem





