# -*- coding: utf-8 -*-

from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi

import MySQLdb
import MySQLdb.cursors

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item

#同步下载可用
class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect("192.168.7.191","root","Scrapy_Pass","jd_phone",charset="utf8",use_unicode=True)
        self.cursor = self.conn.cursor()
    def process_item(self,item,spider):

        insert_sql = """
            insert into phone_list(phone_name,price,phone_url)  VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE phone_name=VALUES(phone_name),price=VALUES(price),phone_url=VALUES(phone_url)
                """
        self.cursor.execute(insert_sql,(item["phone_name"],item["price"],item["phone_url"]))

        self.conn.commit()

#MySQL异步
class MysqlTwistedPipline(object):
    def __init__(self,dbpool):
        self.dbpool = dbpool
    @classmethod
    def from_settings(cls,settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb",**dbparms)
        return cls(dbpool)

    def process_item(self,item,spider):
        query = self.dbpool.runInteraction(self.do_insert,item)
        query.addErrback(self.handle_error,item,spider)

    def handle_error(self,failure,item,spider):
        print (failure)

    def do_insert(self,cursor,item):
        print("写入数据库")
        insert_sql,params = item.get_insert_sql()
        cursor.execute(insert_sql,params)

        # insert_sql = """
        #                     insert into JobBole(Title,URL,CreateTime,VoteNum,BookMarkNum,Content,FrontImageUrl,ArticleComment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        #                 """
        #
        # cursor.execute(insert_sql, (item["Title"], item["URL"], item["CreateTime"], item["VoteNum"],item["BookMarkNum"],item["Content"],item["FrontImageUrl"][0],item["ArticleComment"]))



#下载图片
class ArticleImagePipeline(ImagesPipeline):
    #重写ImagesPipeline的item_completed函数
    def item_completed(self, results, item, info):
        if "FrontImageUrl" in item:
            #ok为执行状态，value是一个字典
            for ok,value in results:
                #获取文件路径
                ImageFilePath = value["path"]
            #将文件路径发送给items的FrontImagePath
            item["FrontImagePath"] = ImageFilePath
        return item


#将数据写入到ES中
class ESPiplines(object):
    def process_item(self,item,spider):
        item.savedata_to_es()
        return item


import redis
from scrapy import Item

class saveToRedisPipeline:
    def open_spider(self, spider):
        db_host = spider.settings.get('REDIS_HOST', 'localhost')
        db_port = spider.settings.get('REDIS_PORT', 6379)
        db_index = spider.settings.get('REDIS_DB_INDEX', 0)
        self.db_conn = redis.StrictRedis(host=db_host, port=db_port, db=db_index)

    def close_spider(self, spider):
        self.db_conn.connection_pool.disconnect()

    def process_item(self, item, spider):
        self.insert_db(item)

        return item

    def insert_db(self, item):
        if isinstance(item, Item):
            item = dict(item)
        self.db_conn.set(item['id'],item['url'])



