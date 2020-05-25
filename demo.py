# -*- coding = utf-8 -*-
# @Time :  18:52
# @Author : balon
# @File : demo.py
# @Software : PyCharm

from bs4 import BeautifulSoup
import re
import urllib.request, urllib.error
import xlwt
import sqlite3

def main():
    baseUrl = "https://kuyun.tv"

    params = "/vod/show/id/1/page/1.html"
    # 1.爬取网页
    dataList = getData(baseUrl)
    savepath = ".\\酷云电影.xls"
    # 3.保存数据
    # saveData(savepath)
    # askURL(baseUrl + params)

# 爬取网页
def getData(baseUrl):
    dataList = []
    for i in range(1, 667):
        url = baseUrl + f"/vod/show/id/1/page/{i}.html"
        html = askURL(url)      # 保存获取到的网页源码

    # 2.逐一解析数据
    return dataList


# 得到指定一个URL的网页内容
def askURL(url):
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"
    }
    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        print(html)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html

# 保存数据
def saveData(savepath):
    print("save...")

if __name__ == "__main__":
    main()
