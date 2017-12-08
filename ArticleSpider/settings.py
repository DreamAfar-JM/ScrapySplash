# -*- coding: utf-8 -*-
import sys,os
#获取当前文件工作路径
ProjectDir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, ProjectDir)
# Scrapy settings for ArticleSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'ArticleSpider'

SPIDER_MODULES = ['ArticleSpider.spiders']
NEWSPIDER_MODULE = 'ArticleSpider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ArticleSpider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
#    'ArticleSpider.middlewares.ArticlespiderSpiderMiddleware': 543,
    # 启用SplashDeduplicateArgsMiddleware中间件
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   #'ArticleSpider.middlewares.MyCustomDownloaderMiddleware': 543,
    'ArticleSpider.middlewares.RandomUserAgentMiddlware': 3,
    #'ArticleSpider.middlewares.RandomProxyMiddlware': 2,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,

}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   #'ArticleSpider.pipelines.ArticlespiderPipeline': 300,
    #开启下载图片功能,数字代表优先级
    #'scrapy.pipelines.images.ImagesPipeline': 1,
    #开启自动义图片下载
    #'ArticleSpider.pipelines.ArticleImagePipeline': 1,
    #保存到mysql数据库
    # 'ArticleSpider.pipelines.MysqlPipeline': 1,
    #异步保存数据到mysql
    'ArticleSpider.pipelines.MysqlTwistedPipline': 2,
    #保存数据到es
    #'ArticleSpider.pipelines.ESPiplines': 1,
    #'scrapy_redis.pipelines.RedisPipeline': 300,
    #'ArticleSpider.middlewares.JSPageMiddleware': 2,
}
#配置图片路径，去items中找FrontImageUrl的值并下载图片
IMAGES_URLS_FIELD = "FrontImageUrl"
#下载到ProjectDir的images下，也就是当前工作目录的images目录下
IMAGES_STORE = os.path.join(ProjectDir,"images")
# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

MYSQL_HOST = "192.168.7.191"
MYSQL_DBNAME = "jd_phone"
MYSQL_USER = "scrapy"
MYSQL_PASSWORD = "Scrapy_Pass"


SQL_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SQL_DATE_FORMAT = "%Y-%m-%d"

UserAgentType = "random"

#禁用cookie,需要登录的不能设置禁用，比如知乎
COOKIES_ENABLED=False
#下载延迟
#DOWNLOAD_DELAY=1

AUTOTHROTTLE_ENABLED = True




# #HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
# SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# #REDIS_URL = 'redis://172.16.10.189:6379'
# DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# REDIS_HOST = "172.16.10.189"
# REDIS_PORT = 6379
# FILTER_URL = None
# FILTER_HOST = '172.16.10.189'
# FILTER_PORT = 6379
# FILTER_DB = 0
# # REDIS_QUEUE_NAME = 'OneName'   # 如果不设置或者设置为None，则使用默认的，每个spider使用不同的去重队列和种子队列。如果设置了，则不同spider共用去重队列和种子队列
#
# """
#     这是去重队列的Redis信息。
#     原先的REDIS_HOST、REDIS_PORT只负责种子队列；由此种子队列和去重队列可以分布在不同的机器上。
# """
#
#
# #REDIRECT_ENABLED = False
# ES_HOST = "172.16.10.189"

# DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
SPLASH_URL = 'http://192.168.7.191:8050'
# HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'