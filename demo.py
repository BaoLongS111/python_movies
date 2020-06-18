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


# 创建正则表达式对象，表示规则（字符串的模式）
findLink = re.compile(r'<a class="fed-list-title fed-font-xiv fed-text-center fed-text-sm-left fed-visible fed-part-eone" href="(.*?)">')

# 详情页片名
findTitle = re.compile(r'.html">(.*)?</a></h1>')
# ID
findId = re.compile(r'<a href="/vod/detail/id/(\d*).html">')
# 主演


# 爬取网页
def getData(baseUrl):
    dataList = []
    for i in range(1, 667):
        url = baseUrl + f"/vod/show/id/1/page/{i}.html"
        html = askURL(url)      # 保存获取到的网页源码class="fed-list-item fed-padding fed-col-xs4 fed-col-sm3 fed-col-md2

        # 2.逐一解析数据
        soup = BeautifulSoup(html, "html.parser")
        # 获取详情页
        for item in soup.find_all("li", class_="fed-list-item fed-padding fed-col-xs4 fed-col-sm3 fed-col-md2"):  #查找符合要求的字符串，形成列表.
            data = []      #保存一部电影的全部信息
            item = str(item)

            # 影片详情的链接
            link = re.findall(findLink, item)[0]  #re库用来通过正则表达式查找指定的字符串
            # print(baseUrl + link)

            # 从详情页获取数据
            detailHtml = askURL(baseUrl+link)
            detailSoup = BeautifulSoup(detailHtml,"html.parser")
            textHtml = str(detailHtml)
            title = re.findall(findTitle,textHtml)[0]
            data.append(title)
            ID = re.findall(findId,textHtml)[0]
            data.append(ID)
            print(f"{ID}{title}")
            # for actor in detailSoup.find_all("")

    return dataList


# 得到指定一个URL的网页内容
def askURL(url):
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0",
        "Cookie":"user_id=1612; user_name=1138491931; group_id=2; group_name=%E9%BB%98%E8%AE%A4%E4%BC%9A%E5%91%98; user_check=99292ccc25546a32126251a7a1da3ead; user_portrait=%2Fstatic%2Fimages%2Ftouxiang.png; fed_password=bsj13770913798; fed_username=1138491931; Hm_lvt_90d65cb348742bcf35c5f677789a4216=1590583490,1590663430,1591845311,1592473239; fed_notice=1; fed_history=%7Bvideo%3A%5B%7B%22name%22%3A%22%u5927%u536B%B7%u79D1%u6CE2%u83F2%u5C14%u7684%u4E2A%u4EBA%u53F2%22%2C%22show%22%3A%22%u4E0D%u9177%u7684%u4E91%22%2C%22link%22%3A%22https%3A//kuyun.tv/vod/play/id/60772/sid/1/nid/1.html%22%2C%22num%22%3A%22BD720P%22%7D%5D%7D; Hm_lpvt_90d65cb348742bcf35c5f677789a4216=1592479987"
    }
    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        # print(html)
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
