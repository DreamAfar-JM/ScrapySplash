# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import re,os,sys
ProjectDir = os.path.abspath(os.path.dirname(__file__))
ProjectDir = os.path.abspath(os.path.dirname(ProjectDir))
sys.path.insert(0, ProjectDir)
import scrapy
import datetime
from w3lib.html import remove_tags
from ArticleSpider.settings import SQL_DATE_FORMAT,SQL_DATETIME_FORMAT
from ArticleSpider.utils.common import GetNum
from scrapy.loader  import ItemLoader
from scrapy.loader.processors import MapCompose,TakeFirst,Join
from .models.es_types import JobboleArticle,ZhilianJob,LagouJob
from elasticsearch_dsl.connections import connections
# from ArticleSpider.settings import REDIS_HOST,ES_HOST
import redis
# redis_cli = redis.StrictRedis(host=REDIS_HOST)

# es = connections.create_connection(JobboleArticle._doc_type.using,hosts=[ES_HOST])
ProjectDir = os.path.abspath(os.path.dirname(__file__))
LogFile = "%s\Log\Error.log"%(ProjectDir)
#print(LogFile)

class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

def TimeDeal(value):
    if ":" in value or "刚刚" in value or "小时" in value or "今天" in value:
        CreateTime = datetime.datetime.now().strftime(SQL_DATE_FORMAT)
    elif "-" in value:
        MatchObj = re.match(".*?(\d+-\d+-\d+).*", value)
        CreateTime = MatchObj.group(1)
        #CreateTime = GetDate(CreateTime)
    else:
        if "昨天" in value:
            Day = 1
        elif "前天" in value:
            Day = 2
        # elif len(value) == 0:
        #     Day = 15
        else:
            MatchObj = re.match(".*(\d+).*", value)
            Day = int(MatchObj.group(1))
        Time = datetime.datetime.now() +  datetime.timedelta(days = -Day)
        CreateTime = Time.strftime(SQL_DATE_FORMAT)

    return  CreateTime
def GetDate(value):
    value = value.strip().replace(" ·","")
    try:
        CreateTime = datetime.datetime.strptime(value,"%Y/%m/%d")
    except Exception as e:
        CreateTime = datetime.datetime.now().date()
    return CreateTime

def gen_suggests(index, info_tuple):
    #根据字符串生成搜索建议数组
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            #调用es的analyze接口分析字符串
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter':["lowercase"]}, body=text)
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"])>1])
            new_words = anylyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input":list(new_words), "weight":weight})

    return suggests

def DelStr(value):
    #去除/和\n
    #value = "".join(value)
    value = value.replace("%","")
    value = value.replace("\r\n","")
    value = value.strip("\n").strip("/").strip("\r").strip(" ")
    # if "-" in value:
    #     value = 0
    return value
def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if "地图"not in item.strip()]
    return "".join(addr_list)

def DealSalary(value):

    if "应届毕业生" in value:
        min = 1
        max = 1
    elif "以上" in value:
        MatchObj = re.match(".*(\d+).*", value)
        min = MatchObj.group(1)
        max = 100
    elif "以下" in value:
        MatchObj = re.match(".*(\d+).*", value)
        max = MatchObj.group(1)
        min = 0
    elif "-" in value:
        MatchObj = re.match(".*?(\d+).*?(\d+).*",value)
        if MatchObj:
            min = MatchObj.group(1)
            max = MatchObj.group(2)
        if "k" in value:
            min = int(min)*1000
            max = int(max)*1000
    else:
        min = 0
        max = 0

    return [min,max]

def ReturnValue(value):
    return  value



class ArticleItemLoader(ItemLoader):
    #自定义itemloader，自定义default_output_processor = TakeFirst()表示取itemloader的第一个值
    default_output_processor = TakeFirst()


class JobBoleArticleItem(scrapy.Item):
    #保存到数据库
    Title = scrapy.Field()
    #input_processor是接收到赋值以后进行什么操作，MapCompose是进行操作的函数
    CreateTime = scrapy.Field(input_processor = MapCompose(GetDate))
    URL = scrapy.Field()
    #FrontImageUrl = scrapy.Field(
    #    output_processor = MapCompose(ReturnValue)
    #)
    #图片URL MD5
    #FrontImageMD5 = scrapy.Field()
    #封面图保存
    FrontImagePath = scrapy.Field()
    VoteNum = scrapy.Field(input_processor = MapCompose(GetNum))
    BookMarkNum = scrapy.Field(input_processor = MapCompose(GetNum))
    ArticleComment = scrapy.Field(input_processor = MapCompose(GetNum))
    #文章内容
    Content = scrapy.Field()
    def get_insert_sql(self):
        insert_sql = """
                                    insert into JobBole(Title,URL,CreateTime,VoteNum,BookMarkNum,Content,ArticleComment)
                                    VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE Content=VALUES(Content),VoteNum=VALUES(VoteNum),ArticleComment=VALUES(ArticleComment),BookMarkNum=VALUES(BookMarkNum)
                                """
        params = (self["Title"], self["URL"], self["CreateTime"], self["VoteNum"],self["BookMarkNum"],self["Content"],self["ArticleComment"])
        return insert_sql, params
    def savedata_to_es(self):
        #保存到elasticsearch
        article = JobboleArticle()
        article.Title = self["Title"]
        article.CreateTime = self["CreateTime"]
        article.URL = self["URL"]
        article.VoteNum = self["VoteNum"]
        article.BookMarkNum = self["BookMarkNum"]
        article.ArticleComment = self["ArticleComment"]
        # 文章内容
        article.Content = self["Content"]
        #定义title和Content的权重，可以自己补全
        article.suggest = gen_suggests(JobboleArticle._doc_type.index, ((article.Title, 10), (article.Content, 7)))
        article.save()
        #记录爬取的多条
        # redis_cli.incr("jobbole_count")
        return

class ZhiHuAnswerItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    answer_id = scrapy.Field()
    author_name = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    parise_num = scrapy.Field()
    comments_num = scrapy.Field()
    crawl_time = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_answer(zhihu_id,answer_id,author_name,author_id,content,parise_num,comments_num,
            crawl_time,create_time,update_time
            )  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE content=VALUES(content),comments_num=VALUES(comments_num),parise_num=VALUES(parise_num),update_time=VALUES(update_time),crawal_update_time=VALUES(crawl_time)
        """
        #获取的是时间戳  格式化时间戳
        create_time = datetime.datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATETIME_FORMAT)
        params = (
            self["zhihu_id"],self["answer_id"],self["author_name"],self["author_id"],
            self["content"],self["parise_num"],self["comments_num"],
            self["crawl_time"].strftime(SQL_DATETIME_FORMAT),create_time,update_time,
        )
        return insert_sql,params

class ZhiHuQuestionItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crwal_time = scrapy.Field()

    def get_insert_sql(self):

        insert_sql = """
            insert into zhihu_question(zhihu_id, topics, url, title, content,
            answer_num, comments_num, watch_user_num, click_num, crwal_time
            )  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE content=VALUES(content),comments_num=VALUES(comments_num),watch_user_num=VALUES(watch_user_num),click_num=VALUES(click_num),answer_num=VALUES(answer_num),crwal_update_time=VALUES(crwal_time)
        """
        zhihu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title = "".join(self["title"])
        content = "".join(self["content"])
        answer_num = GetNum("".join(self["answer_num"]))
        comments_num = GetNum("".join(self["comments_num"]))
        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0])
            click_num = int(self["watch_user_num"][1])
        else:
            watch_user_num = int(self["watch_user_num"][0])
            click_num = 0
        crwal_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        params = (zhihu_id, topics, url, title, content, answer_num, comments_num, watch_user_num, click_num, crwal_time)

        return insert_sql,params


class LaGouItem(scrapy.Item):
    job_name = scrapy.Field()
    salary = scrapy.Field(output_processor = MapCompose(DealSalary))
    job_exp = scrapy.Field(output_processor = MapCompose(DealSalary))
    edu = scrapy.Field(input_processor = MapCompose(DelStr))
    job_type = scrapy.Field()
    company_name = scrapy.Field()
    work_city = scrapy.Field(input_processor = MapCompose(DelStr))
    work_addr = scrapy.Field(input_processor = MapCompose(remove_tags,handle_jobaddr))
    feedback = scrapy.Field(input_processor = MapCompose(DelStr))
    create_date = scrapy.Field(input_processor = MapCompose(TimeDeal))
    job_url = scrapy.Field()
    #job_url_id = scrapy.Field()
    company_url = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field(input_processor = Join(","))
    tag = scrapy.Field(input_processor = Join(","))
    #保存到数据库
    def get_insert_sql(self):
        job_name = self["job_name"]
        salary_min = self["salary"][0]
        salary_max =  self["salary"][1]
        job_exp_min = self["job_exp"][0]
        job_exp_max = self["job_exp"][1]
        edu = self["edu"]
        job_type = self["job_type"]
        company_name = self["company_name"]
        work_city = self["work_city"]
        work_addr = self["work_addr"]
        feedback = self["feedback"]
        create_date = self["create_date"]
        job_url = self["job_url"]
        #job_url_id = self["job_url_id"]
        company_url = self["company_url"]
        job_advantage = self["job_advantage"]
        job_desc = self["job_desc"]
        tag = self["tag"]
        crawl_time = datetime.datetime.now().strftime(SQL_DATE_FORMAT)

        insert_sql = """
            insert into LaGou(job_name, salary_min,salary_max, job_exp_min, job_exp_max, edu, job_type, company_name, work_city,work_addr, feedback, create_date, job_url, job_url_id, company_url, job_advantage, job_desc, tag, crawl_time)  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE salary_min=VALUES(salary_min),salary_max=VALUES(salary_max),job_exp_min=VALUES(job_exp_min),job_exp_max=VALUES(job_exp_max),edu=VALUES(edu),create_date=VALUES(create_date),crawl_time=VALUES(crawl_time)
        """


        params = (job_name, salary_min,salary_max, job_exp_min, job_exp_max, edu, job_type, company_name, work_city,work_addr, feedback, create_date, job_url, job_url_id, company_url, job_advantage, job_desc, tag, crawl_time)

        return insert_sql,params

        #保存到es
    def savedata_to_es(self):
        #保存到elasticsearch
        article = LagouJob()
        article.job_name = self["job_name"]
        article.salary_min = self["salary"][0]
        article.salary_max = self["salary"][1]
        article.job_exp_min = self["job_exp"][0]
        article.job_exp_max = self["job_exp"][1]
        article.edu = self["edu"]
        article.work_city = self["work_city"]
        article.work_addr = self["work_addr"]
        article.job_type = self["job_type"]
        article.company_name = self["company_name"]
        # feedback = self["feedback"]
        article.create_date = self["create_date"]
        article.job_url = self["job_url"]
        #article.job_url_id = self["job_url_id"]
        article.company_url = self["company_url"]
        article.job_advantage = self["job_advantage"]
        article.job_desc = self["job_desc"]
        article.tag = self["tag"]
        article.crawl_time = datetime.datetime.now().strftime(SQL_DATE_FORMAT)
        #定义title和Content的权重，可以自己补全
        article.suggest = gen_suggests(ZhilianJob._doc_type.index, ((article.job_name, 10), (article.company_name, 7)))
        article.save()
        #记录爬取的多条
        # redis_cli.incr("lagou_count")
        return

class ZhiLianItem(scrapy.Item):
    job_name = scrapy.Field()
    salary = scrapy.Field(output_processor = MapCompose(DealSalary))
    job_exp = scrapy.Field(output_processor = MapCompose(DealSalary))
    edu = scrapy.Field()#input_processor = MapCompose(DelStr))
    job_type = scrapy.Field()
    company_name = scrapy.Field()
    work_city = scrapy.Field()#input_processor = MapCompose(DelStr))
    work_addr = scrapy.Field(input_processor = MapCompose(remove_tags,DelStr))
    #feedback = scrapy.Field()#input_processor = MapCompose(DelStr))
    create_date = scrapy.Field(input_processor = MapCompose(TimeDeal))
    job_url = scrapy.Field()
    job_url_id = scrapy.Field()
    company_url = scrapy.Field()
    job_advantage = scrapy.Field(input_processor = Join(","))
    job_desc = scrapy.Field(input_processor = Join(","))
    tag = scrapy.Field()#input_processor = Join(","))
    #保存数据到数据库
    def get_insert_sql(self):
        try:
            job_name = self["job_name"]
            salary_min = self["salary"][0]
            salary_max =  self["salary"][1]
            job_exp_min = self["job_exp"][0]
            job_exp_max = self["job_exp"][1]
            edu = self["edu"]
            work_city = self["work_city"]
            work_addr = self["work_addr"]
            job_type = self["job_type"]
            company_name = self["company_name"]
            #feedback = self["feedback"]
            create_date = self["create_date"]
            job_url = self["job_url"]
            job_url_id = self["job_url_id"]
            company_url = self["company_url"]
            job_advantage = self["job_advantage"]
            job_desc = self["job_desc"]
            tag = self["tag"]
            crawl_time = datetime.datetime.now().strftime(SQL_DATE_FORMAT)
        except Exception as e:
            LogInfo = """Info:%s,URl:%s,Date:%s\n"""%(e,self["job_url"],datetime.datetime.now().strftime(SQL_DATE_FORMAT))
            with open(LogFile,"a") as f:
                f.write(LogInfo)
            if e in ["salary_min","salary_max","job_exp_min","job_exp_min"]:
                a = e
                a = 0
            else:
                a = e
                e = "获取失败"
        finally:

            insert_sql = """
                insert into ZhiLian(job_name, salary_min,salary_max, job_exp_min, job_exp_max, edu, job_type, company_name, work_city,work_addr, create_date, job_url, job_url_id, company_url, job_advantage, job_desc, tag, crawl_time)  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE salary_min=VALUES(salary_min),salary_max=VALUES(salary_max),job_exp_min=VALUES(job_exp_min),job_exp_max=VALUES(job_exp_max),edu=VALUES(edu),create_date=VALUES(create_date),crawl_time=VALUES(crawl_time)
            """


            params = (job_name, salary_min,salary_max, job_exp_min, job_exp_max, edu, job_type, company_name, work_city,work_addr, create_date, job_url, job_url_id, company_url, job_advantage, job_desc, tag, crawl_time)

            return insert_sql,params

    def savedata_to_es(self):
        #保存到elasticsearch
        article = ZhilianJob()
        article.job_name = self["job_name"]
        article.salary_min = self["salary"][0]
        article.salary_max = self["salary"][1]
        article.job_exp_min = self["job_exp"][0]
        article.job_exp_max = self["job_exp"][1]
        article.edu = self["edu"]
        article.work_city = self["work_city"]
        article.work_addr = self["work_addr"]
        article.job_type = self["job_type"]
        article.company_name = self["company_name"]
        # feedback = self["feedback"]
        article.create_date = self["create_date"]
        article.job_url = self["job_url"]
        #article.job_url_id = self["job_url_id"]
        article.company_url = self["company_url"]
        article.job_advantage = self["job_advantage"]
        article.job_desc = self["job_desc"]
        article.tag = self["tag"]
        article.crawl_time = datetime.datetime.now().strftime(SQL_DATE_FORMAT)
        #定义title和Content的权重，可以自己补全
        article.suggest = gen_suggests(ZhilianJob._doc_type.index, ((article.job_name, 10), (article.company_name, 7)))
        article.save()
        #记录爬取的多条
        # redis_cli.incr("zhilian_count")
        return



class JDPhoneItem(scrapy.Item):
    phone_name = scrapy.Field()
    price = scrapy.Field()
    phone_url = scrapy.Field()
    #保存数据到数据库
    def get_insert_sql(self):

        phone_name = self["phone_name"]
        price = self["price"]
        phone_url =  self["phone_url"]

        insert_sql = """
            insert into phone_list(phone_name,price,phone_url)  VALUES (%s,%s,%s)
        """

        params = (phone_name,price,phone_url)

        return insert_sql,params

class WencaiBaseInfo(scrapy.Item):
    # 基本信息
    Code = scrapy.Field()
    Abb = scrapy.Field()
    Industry = scrapy.Field()
    City = scrapy.Field()
    def get_insert_sql(self):
        Code = self["Code"]
        Abb = self["Abb"]
        Industry =  self["Industry"]
        City =  self["City"]

        insert_sql = """
            insert into BaseInfo(Code,Abb,Industry,City)  VALUES (%s,%s,%s,%s)
        """
        params = (Code,Abb,Industry,City)
        return insert_sql,params
class WencaiClinicShares(scrapy.Item):
    # 牛叉诊股
    Code = scrapy.Field()
    Title = scrapy.Field()
    Context = scrapy.Field()
    ClinicShareUrl = scrapy.Field()
    Score = scrapy.Field()
    ShortTrend = scrapy.Field()
    MiddleTrend = scrapy.Field()
    LongTrend = scrapy.Field()
    #ClinicShares = scrapy.Field()
    def get_insert_sql(self):
        Code = self["Code"]
        Title = self["Title"]
        Context =  self["Context"]
        ClinicShareUrl =  self["ClinicShareUrl"]
        Score =  self["Score"]
        ShortTrend =  self["ShortTrend"][0]
        MiddleTrend =  self["MiddleTrend"][0]
        LongTrend =  self["LongTrend"][0]
        #ClinicShares =  self["ClinicShares"]

        insert_sql = """
            insert into ClinicShares(Code,Title,Context,ClinicShareUrl,Score,ShortTrend,MiddleTrend,LongTrend)  VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """
        params = (Code,Title,Context,ClinicShareUrl,Score,ShortTrend,MiddleTrend,LongTrend)
        return insert_sql,params

class WencaiImportEvents(scrapy.Item):
    # 重要事件
    Code = scrapy.Field()
    EventName= scrapy.Field()
    EventContext= scrapy.Field()
    EventTime= scrapy.Field()
    def get_insert_sql(self):
        Code = self["Code"]
        EventName = self["EventName"]
        EventContext =  self["EventContext"]
        EventTime =  self["EventTime"]

        insert_sql = """
            insert into ImportEvents(Code,EventName,EventContext,EventTime)  VALUES (%s,%s,%s,%s)
        """
        params = (Code,EventName,EventContext,EventTime)
        return insert_sql,params
class WencaiImportNews(scrapy.Item):
    # 重要新闻
    Code = scrapy.Field()
    NewTitle = scrapy.Field()
    NewContext = scrapy.Field()
    NewUrl = scrapy.Field()

    def get_insert_sql(self):
        Code = self["Code"]
        NewTitle = self["NewTitle"]
        NewContext =  self["NewContext"][0]
        NewUrl =  self["NewUrl"]

        insert_sql = """
            insert into ImportNews(Code,NewTitle,NewContext,NewUrl)  VALUES (%s,%s,%s,%s)
        """
        params = (Code,NewTitle,NewContext,NewUrl)
        return insert_sql,params

class WencaiInvestmentAnalysis(scrapy.Item):
    # 投顾分析
    Code = scrapy.Field()
    InvestmentContext = scrapy.Field()

    def get_insert_sql(self):
        Code = self["Code"]
        InvestmentContext = self["InvestmentContext"]

        insert_sql = """
               insert into InvestmentAnalysis(Code,InvestmentContext)  VALUES (%s,%s)
           """
        params = (Code, InvestmentContext)
        return insert_sql, params

class WencaiWindy(scrapy.Item):
    # 技术风向标
    Code = scrapy.Field()
    WindyContext = scrapy.Field()

    def get_insert_sql(self):
        Code = self["Code"]
        WindyContext = self["WindyContext"]

        insert_sql = """
               insert into Windy(Code,WindyContext)  VALUES (%s,%s)
           """
        params = (Code, WindyContext)
        return insert_sql, params

class SaveToRedisItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    url = scrapy.Field()


class CNBlogItem(scrapy.Item):
    # 技术风向标
    author = scrapy.Field()
    fans = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    post_date = scrapy.Field()
    class_ification = scrapy.Field()
    tag = scrapy.Field()
    url = scrapy.Field()

    def get_insert_sql(self):
        author = self["author"]
        fans = self["fans"]
        title = self["title"]
        content = self["content"]
        post_date = self["post_date"]
        class_ification = self["class_ification"]
        tag = self["tag"]
        url = self["url"]

        insert_sql = """
               insert into cnblog(author,fans,title,content,post_date,class_ification,tag,url)  VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
           """
        params = (author,fans,title,content,post_date,class_ification,tag,url)
        return insert_sql, params

class AmazonItem(scrapy.Item):
    # 商品信息
    # 商品ID
    shop_id = scrapy.Field()
    # 品牌
    brand = scrapy.Field()
    # 商品链接
    url = scrapy.Field()
    # 商品名称
    title = scrapy.Field()
    # 商品图url
    image_url = scrapy.Field()
    # 评价数
    comment_num = scrapy.Field()
    # 星级
    star = scrapy.Field()
    # 价格
    min_price = scrapy.Field()
    max_price = scrapy.Field()
    # 商品源码
    # response_text = scrapy.Field()
    # 商品排名
    shop_rank = scrapy.Field()
    def get_insert_sql(self):
        shop_id = self["shop_id"]
        brand = self["brand"]
        url = self["url"]
        title = self["title"]
        # image_url = self["image_url"]
        comment_num = self["comment_num"]
        min_price = self["min_price"]
        max_price = self["min_price"]
        # response_text = self["response_text"]
        star = self["star"]
        shop_rank = self["shop_rank"]
        insert_sql = """
               insert into Amazon(shop_id,brand,url,title,comment_num,star,min_price,max_price,shop_rank)  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
           """
        params = (shop_id,brand,url,title,comment_num,star,min_price,max_price,shop_rank)
        return insert_sql, params

class AmazonCommentItem(scrapy.Item):
    # 商品评价
    # 商品ID
    shop_id = scrapy.Field()
    # 评价内容
    comment_text = scrapy.Field()
    # 评价星级占比
    five_proportion = scrapy.Field()
    four_proportion = scrapy.Field()
    three_proportion = scrapy.Field()
    two_proportion = scrapy.Field()
    one_proportion = scrapy.Field()
    comment_url = scrapy.Field()
    # comment_response = scrapy.Field()
    comment_type = scrapy.Field()
    commenter = scrapy.Field()
    comment_star = scrapy.Field()
    def get_insert_sql(self):
        shop_id = self["shop_id"]
        comment_text = self["comment_text"]
        five_proportion = self["five_proportion"]
        four_proportion = self["four_proportion"]
        three_proportion = self["three_proportion"]
        two_proportion = self["two_proportion"]
        one_proportion = self["one_proportion"]
        comment_url = self["comment_url"]
        comment_type = self["comment_type"]
        commenter = self["commenter"]
        # comment_response = self["comment_response"]
        comment_star = self["comment_star"]
        insert_sql = """
               insert into AmazonComment(shop_id,comment_text,five_proportion,four_proportion,three_proportion,two_proportion,one_proportion,comment_url,comment_type,commenter,comment_star)  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
           """
        params = (shop_id,comment_text,five_proportion,four_proportion,three_proportion,two_proportion,one_proportion,comment_url,comment_type,commenter,comment_star)
        return insert_sql, params

class JDAllItem(scrapy.Item):
    # 商品信息
    shop_id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    brand = scrapy.Field()
    brand_url = scrapy.Field()
    price = scrapy.Field()
    comment_num = scrapy.Field()
    good_comment_rate = scrapy.Field()
    good_comment = scrapy.Field()
    general_count = scrapy.Field()
    poor_count = scrapy.Field()
    hot_comment_dict = scrapy.Field()
    default_comment_num = scrapy.Field()
    # 主键 评论ID
    comment_id = scrapy.Field()
    comment_context = scrapy.Field()
    comnent_time = scrapy.Field()
    # 用户评分
    comment_score = scrapy.Field()
    # 来源
    comment_source = scrapy.Field()
    # 型号
    produce_size = scrapy.Field()
    # 颜色
    produce_color = scrapy.Field()
    # 用户级别
    user_level = scrapy.Field()
    # 用户京享值
    user_exp = scrapy.Field()
    # 评价点赞数
    comment_thumpup = scrapy.Field()
    # 商家回复
    comment_reply_content = scrapy.Field()
    comment_reply_time = scrapy.Field()
    append_comment = scrapy.Field()
    append_comment_time = scrapy.Field()

    def get_insert_sql(self):
        shop_id = self["shop_id"]
        url = self["url"]
        title = self["title"]
        brand = self["brand"]
        brand_url = self["brand_url"]
        price = self["price"]
        comment_num = self["comment_num"]
        good_comment_rate = self["good_comment_rate"]
        good_comment = self["good_comment"]
        general_count = self["general_count"]
        poor_count = self["poor_count"]
        hot_comment_dict = self["hot_comment_dict"]
        default_comment_num = self["default_comment_num"]
        comment_id = self["comment_id"]
        comment_context = self["comment_context"]
        comnent_time = self["comnent_time"]
        comment_score = self["comment_score"]
        comment_source = self["comment_source"]
        produce_size = self["produce_size"]
        produce_color = self["produce_color"]
        user_level = self["user_level"]
        user_exp = self["user_exp"]
        comment_thumpup = self["comment_thumpup"]
        comment_reply_content = self["comment_reply_content"]
        comment_reply_time = self["comment_reply_time"]
        append_comment = self["append_comment"]
        append_comment_time = self["append_comment_time"]

        insert_sql = """
                       insert into JDAll(shop_id,url,title,brand,brand_url,price,comment_num,good_comment_rate,good_comment,general_count,poor_count,hot_comment_dict,default_comment_num,comment_id,comment_context,comnent_time,comment_score,comment_source,produce_size,produce_color,user_level,user_exp,comment_thumpup,comment_reply_content,comment_reply_time,append_comment,append_comment_time)  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   """
        params = (
        shop_id, url, title, brand, brand_url, price, comment_num, good_comment_rate, good_comment, general_count,
        poor_count, hot_comment_dict, default_comment_num, comment_id, comment_context, comnent_time, comment_score,
        comment_source, produce_size, produce_color, user_level, user_exp, comment_thumpup, comment_reply_content,
        comment_reply_time, append_comment, append_comment_time)
        print("return SQL 语句")
        return insert_sql, params


class ALIExpressItem(scrapy.Item):
    # 商品url
    shop_url = scrapy.Field()
    shop_cate_url = scrapy.Field()
    shop_id = scrapy.Field()
    owner_member_id = scrapy.Field()
    shop_title = scrapy.Field()
    brand = scrapy.Field()
    store_url = scrapy.Field()
    store_name = scrapy.Field()
    store_address = scrapy.Field()
    min_price = scrapy.Field()
    max_price = scrapy.Field()
    min_discount_price = scrapy.Field()
    max_discount_price = scrapy.Field()
    shop_info = scrapy.Field()
    shop_star = scrapy.Field()
    shop_comment_num = scrapy.Field()
    order_num = scrapy.Field()
    def get_insert_sql(self):
        shop_url = self["shop_url"]
        shop_cate_url = self["shop_cate_url"]
        shop_id = self["shop_id"]
        owner_member_id = self["owner_member_id"]
        shop_title = self["shop_title"]
        brand = self["brand"]
        store_url = self["store_url"]
        store_name = self["store_name"]
        store_address = self["store_address"]
        min_price = self["min_price"]
        max_price = self["max_price"]
        min_discount_price = self["min_discount_price"]
        max_discount_price = self["max_discount_price"]
        shop_info = self["shop_info"]
        shop_star = self["shop_star"]
        shop_comment_num = self["shop_comment_num"]
        order_num = self["order"]

        insert_sql = """
                       insert into ALIExpress(shop_url,shop_cate_url,shop_id,owner_member_id,shop_title,brand,store_url,store_name,store_address,min_price,max_price,min_discount_price,max_discount_price,shop_info,shop_star,shop_comment_num,order_num)  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   """
        params = (shop_url,shop_cate_url,shop_id,owner_member_id,shop_title,brand,store_url,store_name,store_address,min_price,max_price,min_discount_price,max_discount_price,shop_info,shop_star,shop_comment_num,order_num)
        print("return 商品信息 SQL 语句")
        return insert_sql, params

class ALIExpressCommentItem(scrapy.Item):
    shop_id = scrapy.Field()
    member_id = scrapy.Field()
    member_country = scrapy.Field()
    comment_time = scrapy.Field()
    order_info = scrapy.Field()
    comment_text = scrapy.Field()
    comment_thumpup = scrapy.Field()
    append_comment = scrapy.Field()
    append_comment_time = scrapy.Field()
    replay_text = scrapy.Field()
    replay_text_time = scrapy.Field()

    def get_insert_sql(self):
        shop_id = self['shop_id']
        member_id = self['member_id']
        member_country = self['member_country']
        comment_time = self['comment_time']
        order_info = self['order_info']
        comment_text = self['comment_text']
        comment_thumpup = self['comment_thumpup']
        append_comment = self['append_comment']
        append_comment_time = self['append_comment_time']
        replay_text = self['replay_text']
        replay_text_time = self['replay_text_time']
        insert_sql = """
                               insert into ALIExpressComment(shop_id,member_id,member_country,comment_time,order_info,comment_text,comment_thumpup,append_comment,append_comment_time,replay_text,replay_text_time)  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                           """
        params = (
            shop_id, member_id, member_country, comment_time, order_info, comment_text, comment_thumpup, append_comment,
            append_comment_time, replay_text, replay_text_time)
        print("return 商品信息 SQL 语句")
        return insert_sql, params


