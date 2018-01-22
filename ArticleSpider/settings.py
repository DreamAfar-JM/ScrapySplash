# -*- coding: utf-8 -*-
import sys,os
#获取当前文件工作路径
ProjectDir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, ProjectDir)
# Scrapy settings for ArticleSpider project
# ###
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
    # splash 所用
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
    'ArticleSpider.pipelines.MysqlTwistedPipline': 404,
    # 'scrapy_redis.pipelines.RedisPipeline' : 300,
    # 'ArticleSpider.pipelines.saveToRedisPipeline': 404,
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

# MYSQL_HOST = "192.168.1.241"
# MYSQL_DBNAME = "wencai"
# MYSQL_USER = "wencai"
# MYSQL_PASSWORD = "wencai"




SQL_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SQL_DATE_FORMAT = "%Y-%m-%d"

UserAgentType = "random"

#禁用cookie,需要登录的不能设置禁用，比如知乎
COOKIES_ENABLED=True
#下载延迟
# DOWNLOAD_DELAY=1

AUTOTHROTTLE_ENABLED = True

DOWNLOAD_TIMEOUT = 300


# #HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
REDIS_URL = 'redis://192.168.1.241:6379'
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
REDIS_HOST = "192.168.1.241"
REDIS_PORT = 6379
SCHEDULER_PERSIST = True
REDIS_DB_INDEX = 1
# FILTER_URL = None
# FILTER_HOST = '192.168.1.241'
# FILTER_PORT = 6379
# FILTER_DB = 0
# SCHEDULER = "ArticleSpider.scrapy_redis_plus.scheduler.Scheduler"
# REDIS_URL = 'redis://192.168.1.241:6379'
# DUPEFILTER_CLASS = "ArticleSpider.scrapy_redis_plus.dupefilter.RFPDupeFilter"
# REDIS_QUEUE_NAME = 'OneName'   # 如果不设置或者设置为None，则使用默认的，每个spider使用不同的去重队列和种子队列。如果设置了，则不同spider共用去重队列和种子队列
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
# SPLASH_URL = 'http://192.168.1.241:8051'
# nginx反代地址
SPLASH_URL = 'http://192.168.1.234'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

#COOKIE="__xsptplus30=30.1.1481802176.1481802176.1%234%7C%7C%7C%7C%7C%23%23mL-91KF7jli9GC0W05jm6QEbQUMK7frI%23; dywem=95841923.y; dywez=95841923.1505216440.4.1.dywecsr=(direct)|dyweccn=(direct)|dywecmd=(none)|dywectr=undefined; FSSBBIl1UgzbN7N443S=byxF1iTJrcdrNuLEW2tfWL4Tr2i43W2lILGes4HOj_HyKlviRWpCYidwAs7mANUW; _jzqa=1.3185897859120813600.1486780644.1505216441.1511359793.3; LastCity=%e4%b8%8a%e6%b5%b7; LastCity%5Fid=538; pcc=r=2090671765&t=0; __zpWAM=1513511627247.440852.1513511627.1513511627.1; __zpWAMs2=1; utype=683575905; Hm_lvt_38ba284938d5eddca645bb5e02a02006=1511359793,1513511617; Hm_lpvt_38ba284938d5eddca645bb5e02a02006=1513512217; qrcodekey=54b39b3842bd4a7cb8556748bec76cf1; urlfrom=121126445; urlfrom2=121126445; adfcid=none; adfcid2=none; adfbid=0; adfbid2=0; JsOrglogin=2050727717; at=729741867753471e89c5faa66467c26b; Token=729741867753471e89c5faa66467c26b; rt=447b6cc0fc26432ea9702b6400911366; uiioit=3D672038046A52644F64436F5D6753380C6A5D644764456F536726387D6A59644364416F506751380B6A5C644764486F53677; lastchannelurl=https%3A//passport.zhaopin.com/org/login; JsNewlogin=683575905; ihrtkn=; cgmark=2; NewPinLoginInfo=; NewPinUserInfo=; isNewUser=1; RDpUserInfo=; RDsUserInfo=2F792773596653645C7156685C6A4D7956735D66556451715E68256A34795E7314660C640A710D681B6A1B79077309660C640A715E683C6A34795E733CE68E3BDB0F2D683B6A417921732066586450715468516A4F7951735C6655645C715E682B6A34795E737335C92A7B17D60431EA9126DC0DB51FE5066D1635FE053B822A587330662864597154682F6A41792673296658640C711768296A0A790A730A660E6411710468006A02790A7305660B644A710668066A177958733766316459715468526A3B7937735966546456714868586A4D794373566655645E715668516A417927732066586450715468516A4F7951735C6655645C715E682D6A34795E737335C92A7B17D60431EA9126DC0DB51FE5066D1635FE053B822A58732866286459715568596A4A7952735F662664207158685C6A497953735F66306430715868586A4A7951735F662664257158682A6A3979577355665D6451715768516A4A795B7356665E6420712468546A39792073506654645C7150685B6A427953735C6657645F7121682A6A477953735F6636642D7158685A6A41792A7334665864567151685B6A54795273556654645F712468256A477953735F667; SearchHead_Erd=rd; __utmt=1; getMessageCookie=1; FSSBBIl1UgzbN7N80S=Gwp0dYC2JoKN2osfK122FXGRWEvJ6b7.GAlxJRK3mC8.W5lGoQl7l_kfXm12bgQO; NTKF_T2D_CLIENTID=guest708152E5-985C-23B3-DCD8-6453453DC9A8; nTalk_CACHE_DATA={uid:kf_9051_ISME9754_guest708152E5-985C-23,tid:1513511667005852}; FSSBBIl1UgzbN7N443T=1dTQLQmWfj7eGu40ZFyGRwZn7p9E3zQSklNEnHWzLW2enxWsjjGJV6vprFW.xTQe0H_1SgnR0RZO38B0NE0Vh4ntcy_8EZxoxq1Azkn51Cv6GPNxzJfxseSBcDs0B.0L6398L.PKtPsjO4JG1BCDs9adVaTnAcGZbbG3sihOJBF7YkuB2ivMCN43arhArUrCiXOpICYKC6M_4H4_NJQpe9xOiCDL0g9MjwfImyz58BkmUVv69uXXxHTIXX2NkqJJX30cdEwPReTbxBM.Hg8xRMeXW.fto27D6w3jHCTOS3i9Vo7FJg8miYsD5UfC23W0CZCzfgeZAJ28J5SVPU3v4GHSN; dywea=95841923.1329001883085103000.1466427597.1513511617.1513514273.7; dywec=95841923; dyweb=95841923.96.9.1513516803402; __utma=269921210.1711695420.1466427597.1513511617.1513514273.8; __utmb=269921210.63.9.1513516803407; __utmc=269921210; __utmz=269921210.1505216441.5.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=269921210.|2=Member=683575905=1; Home_ResultForCustom_orderBy=DATE_MODIFIED%2C1; Home_ResultForCustom_searchFrom=custom"