#!/usr/bin/python3
#coding=utf-8
from urllib.request import urlopen
# import lxml.html
from bs4 import BeautifulSoup
url = "http://ip.chinaz.com/202.106.0.20"
# BeautifulSoup parser
html = urlopen(url)
bsObj = BeautifulSoup(html,"html.parser")
Check_result = bsObj.findAll("span",{"class":"Whwtdhalf w50-0"})
for i in Check_result:
    if "IP" in i.get_text():
        pass
    else:
        print(i.get_text())

# lxml
#html = urlopen(url).read()
# lxmlObj = lxml.html.fromstring(html)
#
# td = lxmlObj.cssselect('.ul1 li:first-child')
# for i in td:
#   source = i.text_content().split()[0].split("：")[1]
#
# city_file = open("city_list_new","r",encoding="UTF-8")
# city = city_file.readlines()
# city_file.close()
# print(city)
# if source in city[0]:
#   print("True")
# else:
#   print("Flase")


#