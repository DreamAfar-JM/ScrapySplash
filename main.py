#!/usr/bin/env python
#coding=utf-8

from scrapy.cmdline import execute
import sys,os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#相当于系统执行scrapy crawl jobbole命令

#execute(["scrapy","crawl","jobbole"])
#execute(["scrapy","crawl","zhihu_yundama"])
#execute(["scrapy","crawl","zhihu"])
#execute(["scrapy","crawl","zhihu_nologin"])
#execute(["scrapy","crawl","duozhuan"])
#execute(["scrapy","crawl","lagou"])
#execute(["scrapy","crawl","ZhiLian"])
#execute(["scrapy","crawl","lagou_login"])
#execute(["scrapy","crawl","jd_phone"])
#execute(["scrapy","crawl","wencai"])
#execute(["scrapy","crawl","cnblog"])
# execute(["scrapy","crawl","amazon","-s", "LOG_LEVEL=DEBUG", "-s", "JOBDIR=job_info/amazon"])
# execute(["scrapy","crawl","jd_all","-s", "LOG_LEVEL=DEBUG", "-s", "JOBDIR=job_info/jd_all"])
execute(["scrapy","crawl","aliexpress","-s", "LOG_LEVEL=DEBUG", "-s", "JOBDIR=job_info/aliexpress"])

