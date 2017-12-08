#!/usr/bin/env python
#coding=utf-8

#放置常用函数

import re
import hashlib
def get_md5(url):
    if isinstance(url,str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

def GetNum(value):
    MatchRE = re.match(".*?(\d+).*", value)
    if MatchRE:
        NUMS = int(MatchRE.group(1))
    else:
        NUMS = 0
    return NUMS

# if __name__ == "__main__":
#     print(get_md5("www.baidu.com"))