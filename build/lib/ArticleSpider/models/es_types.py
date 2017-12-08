#!/usr/bin/env python
#coding=utf-8

from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerObjectWrapper, Completion, Keyword, Text, Integer
from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["172.16.10.189"])
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

if __name__ == "__main__":
    #执行后会在ES中创建相应的索引和类型
    JobboleArticle.init()
