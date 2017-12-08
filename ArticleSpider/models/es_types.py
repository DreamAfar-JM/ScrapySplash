#!/usr/bin/env python
#coding=utf-8

from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerObjectWrapper, Completion, Keyword, Text, Integer
from elasticsearch_dsl.connections import connections
# from ArticleSpider.settings import REDIS_HOST
# connections.create_connection(hosts=[REDIS_HOST])
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}
ik_analyzer = CustomAnalyzer("ik_max_word",filter = ["lowercase"])

class JobboleArticle(DocType):
    #定义搜索引擎可以有补全功能
    suggest = Completion(analyzer=ik_analyzer)
    Title = Text(analyzer="ik_max_word")
    CreateTime = Date()
    URL = Keyword()
    VoteNum = Integer()
    BookMarkNum = Integer()
    ArticleComment = Integer()
    # 文章内容
    Content = Text(analyzer="ik_max_word")
    class Meta:
        index = "jobbole"
        doc_type = "article"
def jobrun():
    suggest = Completion(analyzer=ik_analyzer)
    job_name = Text(analyzer="ik_max_word")
    salary_min = Integer()
    salary_max = Integer()
    job_exp_min = Integer()
    job_exp_max = Integer()
    edu = Text(analyzer="ik_max_word")  # input_processor = MapCompose(DelStr))
    job_type = Text(analyzer="ik_max_word")
    company_name = Text(analyzer="ik_max_word")
    work_city = Text(analyzer="ik_max_word")  # input_processor = MapCompose(DelStr))
    work_addr = Keyword()
    # feedback = scrapy.Field()#input_processor = MapCompose(DelStr))
    create_date = Date()
    job_url = Keyword()
    company_url = Keyword()
    job_advantage = Keyword()
    job_desc = Keyword()
    tag = Text(analyzer="ik_max_word")  # input_processor = Join(","))
class ZhilianJob(DocType):
    jobrun()
    class Meta:
        index = "zhilian"
        doc_type = "job"

class LagouJob(DocType):
    jobrun()
    class Meta:
        index = "lagou"
        doc_type = "job"

if __name__ == "__main__":
    #执行后会在ES中创建相应的索引和类型
    LagouJob.init()
