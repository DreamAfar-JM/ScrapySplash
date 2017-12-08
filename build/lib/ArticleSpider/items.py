# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import re,os,sys
import scrapy
import datetime
from w3lib.html import remove_tags
from ArticleSpider.settings import SQL_DATE_FORMAT,SQL_DATETIME_FORMAT
from ArticleSpider.utils.common import GetNum
from scrapy.loader  import ItemLoader
from scrapy.loader.processors import MapCompose,TakeFirst,Join
from ArticleSpider.models.es_types import JobboleArticle
from elasticsearch_dsl.connections import connections
import redis
redis_cli = redis.StrictRedis(host="172.16.10.189")

es = connections.create_connection(JobboleArticle._doc_type.using,hosts=["172.16.10.189"])
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
        MatchObj = re.match("(\d+).*", value)
        min = MatchObj.group(1)
        max = 100
    elif "以下" in value:
        MatchObj = re.match("(\d+).*", value)
        max = MatchObj.group(1)
        min = 0
    elif "-" in value:
        MatchObj = re.match(".*?(\d+).*?(\d+).*",value)
        if MatchObj:
            min = MatchObj.group(1)
            max = MatchObj.group(2)
        if "k" in value:
            min = min*1000
            max = max*1000
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
        redis_cli.incr("jobbole_count")
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
    job_url_id = scrapy.Field()
    company_url = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field(input_processor = Join(","))
    tag = scrapy.Field(input_processor = Join(","))

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
        job_url_id = self["job_url_id"]
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

