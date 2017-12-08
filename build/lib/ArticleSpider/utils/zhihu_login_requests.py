#!/usr/bin/env python
#coding=utf-8

import re
import requests
import http.cookiejar as cookielib

#利用requests创建session对象
session = requests.session()
#调用cookielib的LWPCookieJar用于保存当前的cookie到Cookie.txt
session.cookies = cookielib.LWPCookieJar(filename="Cookie.txt")

#用保存的cookie信息尝试登陆
try:
    session.cookies.load(ignore_discard=True)
except:
    print("Cookie未能加载")
else:
    print("Cookie加载成功")

agent = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0"
header = {
    "HOST": "www.zhihu.com",
    "Referer": "https://www.zhihu.com",
    'User-Agent': agent
}

def is_login():
    #判断是否为登录状态
    InboxUrl = "https://www.zhihu.com/settings/profile"
    response = session.get(InboxUrl,headers=header,allow_redirects=False)
    print(response)
    print(response.status_code)
    if response.status_code != 200:
        return False
    else:
        return True
def get_xsrf():
    #获取xsrf
    response = session.get("https://www.zhihu.com",headers=header)
    #匹配出xsrf
    MatchObj = re.findall('name="_xsrf" value="(.*?)"', response.text)
    #print(MatchObj)
    if MatchObj:
        #print( MatchObj.group(1))
        return MatchObj[0]
    else:
        return ""

def login(account,password):
    if re.match("^1\d{10}",account):
        print("手机号码登录")
        PostUrl = "https://www.zhihu.com/login/phone_num"
        PostData = {
            "_xsrf" : get_xsrf(),
            "phone_num": account,
            "password": password
        }
    else:
        if "@" in account:
            print("邮箱登录")
            PostUrl = "https://www.zhihu.com/login/email"
            PostData = {
                "_xsrf" : get_xsrf(),
                "email": account,
                "password": password
            }
    ResponseText = session.post(PostUrl,data=PostData,headers=header)
    print(ResponseText)
    #print(PostData["_xsrf"])
    session.cookies.save()

login("18518734899","Dotbalo!@#")
Result = is_login()
print(Result)
