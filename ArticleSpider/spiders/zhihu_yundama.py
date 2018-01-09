# -*- coding: utf-8 -*-
import re
import json
import time
import scrapy
import datetime
from urllib import parse
from ArticleSpider.items import ZhiHuAnswerItem,ZhiHuQuestionItem
from scrapy.loader  import ItemLoader
#调用云打码
from ArticleSpider.tools import yundama_dama

from scrapy.cmdline import execute
import os,sys
ProjectDir = os.path.abspath(os.path.dirname(__file__))
ProjectDir = os.path.abspath(os.path.dirname(ProjectDir))
ProjectDir = os.path.abspath(os.path.dirname(ProjectDir))
sys.path.insert(0, ProjectDir)

#验证码存放位置
#获取当前文件的的绝对路径
ProjectDir = os.path.abspath(os.path.dirname(__file__))
#获取当前文件的上上级目录
Bpath = os.path.dirname(ProjectDir)
CaptchaFile = "{0}\VerificationCode\zhihulogin.jpg".format(Bpath)

class ZhihuSpider(scrapy.Spider):
    name = "zhihu_yundama"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['https://www.zhihu.com/#signin']
    #start_urls = ['https://www.zhihu.com/']
    start_answer_url = "http://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"
    agent = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0"
    header = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhihu.com",
        #'User-Agent': agent
    }

    #设置自己的settings
    custom_settings = {
        "COOKIES_ENABLED": True,
    }

    def parse(self, response):
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url,url) for url in all_urls]
        all_urls = filter(lambda x:True if x.startswith("https") else False,all_urls)
        for url in all_urls:
            MatchObj = re.match("(.*zhihu.com/question/(\d+))(/|$).*",url)
            if MatchObj:
                #print("123")
                URL = MatchObj.group(1)
                #ID = MatchObj.group(2)
                yield scrapy.Request(URL,headers=self.header,callback=self.parse_question)
            else:
                yield scrapy.Request(url, headers=self.header, callback=self.parse)
                #print(URL,ID)
    def parse_question(self,response):
        #处理question页面。从页面中提取question item
        if "QuestionHeader-title" in response.text:
            MatchObj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if MatchObj:
                ID = int(MatchObj.group(2))
            item_loader = ItemLoader(item=ZhiHuQuestionItem(),response=response)
            item_loader.add_css("title","h1.QuestionHeader-title::text")
            item_loader.add_css("content",".QuestionHeader-detail")
            item_loader.add_value("url",response.url)
            item_loader.add_value("zhihu_id",ID)
            item_loader.add_css("answer_num",".List-headerText span::text")
            item_loader.add_css("comments_num",".QuestionHeader-Comment button::text")
            item_loader.add_css("watch_user_num",".NumberBoard-value::text")
            item_loader.add_css("topics",".QuestionHeader-topics .Popover div::text")
            question_item = item_loader.load_item()
            yield scrapy.Request(self.start_answer_url.format(ID,20,0),headers=self.header,callback=self.parse_answer,)
            yield question_item

    def parse_answer(self,response):
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        #totals = ans_json["paging"]["totals"]
        Next_UrL = ans_json["paging"]["next"]
        for answer in ans_json["data"]:
            answer_item = ZhiHuAnswerItem()
            answer_item["zhihu_id"] = answer["question"]["id"]
            answer_item["answer_id"] = answer["id"]
            answer_item["author_name"] = answer["author"]["name"]
            answer_item["author_id"] = answer["author"]["id"]
            answer_item["parise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["content"] = answer["content"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()
            yield answer_item
        if not is_end:
            yield scrapy.Request(Next_UrL,headers=self.header,callback=self.parse_answer)


    def start_requests(self):
        #return [scrapy.Request("https://www.zhihu.com/#signin",headers=self.header,callback=self.login)]
        return [scrapy.Request("https://www.zhihu.com/#signin",headers=self.header,callback=self.login)]

    # def get_captcha(self):
    #     import time
    #     t = str(int(time.time()*1000))
    #     captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)

    #以下为登录操作
    def login(self,response):
        ResponseText = response.text
        MatchObj = re.findall('name="_xsrf" value="(.*?)"', ResponseText)
        # print(MatchObj)
        xsrf = ''
        if MatchObj:
            xsrf = MatchObj[0]

        if xsrf:
            post_data = {
                "_xsrf": xsrf,
                "phone_num": "18518734899",
                "password": "727585266!@#",
                "captcha": ""
            }
        #云打码
        post_data = {
            "_xsrf": xsrf,
            "phone_num": "18518734899",
            "password": "727585266!@#",
            "captcha": ""
        }
        t = str(int(time.time()*1000))
        captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)
        yield scrapy.Request(captcha_url,headers=self.header,meta={"post_data":post_data},callback=self.login_after_captcha)


    def login_after_captcha(self,response):
        PostUrl = "https://www.zhihu.com/login/phone_num"
        post_data = response.meta.get("post_data", {})
        with open(CaptchaFile,"wb") as f:
            f.write(response.body)
            f.close()
        captcha = yundama_dama.Run("zhihulogin.jpg")
        if captcha == "":
            return execute(["scrapy","crawl","zhihu_yundama"])
        post_data["captcha"] = captcha
        return [scrapy.FormRequest(
            url=PostUrl,
            formdata=post_data,
            headers=self.header,
            callback=self.check_login,
        )]
    def check_login(self,response):
        #判断是否登录成功
        #pass
        print(response)
        TextJson = json.loads(response.text)
        if "msg" in TextJson and TextJson["msg"] == "登录成功":
            for url in self.start_urls:
                yield scrapy.Request(url,dont_filter=True,headers=self.header)
        else:
            return execute(["scrapy","crawl","zhihu_yundama"])

#
# agent = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0"
#
# header = {
#         "HOST": "www.lagou.com",
#         "Referer": "https://www.lagou.com",
#         'User-Agent': agent
#     }
# FromData = {
#     'companyId':'159404',
#     'positionFirstType':'全部',
#     'pageNo':'2',
#     'pageSize':'10',
# }
# def GetPageUrl(response):
#     print(response)
#
# def start():
#     return [scrapy.FormRequest(
#                 url="https://www.lagou.com/gongsi/searchPosition.json",
#                 formdata=FromData,
#                 headers=header,
#                 callback=GetPageUrl,
#             )]
#
# start()


