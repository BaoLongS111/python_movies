# -*- coding = utf-8 -*-
# @Time :  18:52
# @Author : balon
# @File : demo.py
# @Software : PyCharm

import requests
import re
import time
from bs4 import BeautifulSoup
from w3lib.html import remove_tags
from lxml import etree

# 线路② 2  https://youku.com-youku.com/share/kt46gVOU5qznTlQU
# https://jx.cbi88.com/?url=https://zj.cbi88.com/20200510/wK9VwSdM/index.m3u8
# //www.dplayer.tv/?url=https://youku.com-youku.com/20180122/OgFJZjkT/index.m3u8
# //www.dplayer.tv/?url=https://youku.com-youku.com/20180122/DQtDPzYV/index.m3u8


def main():
    base_url = "https://kuyun.tv"
    params = "/vod/show/id/1/page/{}.html"
    # 1.爬取网页
    data_list = get_data(base_url)
    save_path = ".\\酷云电影.xls"
    # 3.保存数据
    save_data(data_list, save_path)


# 创建正则表达式对象，表示规则（字符串的模式）
find_link = re.compile(r'<a class="fed-list-title fed-font-xiv fed-text-center fed-text-sm-left fed-visible '
                       'fed-part-eone" href="(.*?)">')
# 详情页片名
find_title = re.compile('.html">(.*?)</a></h1>')
# ID
find_id = re.compile(r'<a href="/vod/detail/id/(\d*).html">')
# 分类
find_category = re.compile(r'<a href="/vod/type/id/\d*.html" target="_blank">(.*?)</a>')
# 地区
find_area = re.compile('<li class="fed-col-xs6 fed-col-md3 fed-part-eone"><span class="fed-text-muted">'
                       '地区：</span>(.*?)</li>')
# 年份
find_year = re.compile(r'<li class="fed-col-xs6 fed-col-md3 fed-part-eone">'
                       r'<span class="fed-text-muted">年份：</span>(.*?)</li>')
# 更新日期
find_update = re.compile('<li class="fed-col-xs6 fed-col-md3 fed-part-eone"><span class="fed-text-muted">'
                         '更新：</span>(.*?)</li>')
# 主演
find_actors = re.compile('<li class="fed-col-xs12 fed-col-md6 fed-part-eone">'
                         '<span class="fed-text-muted">主演：</span>(.*?)</li>')
# 导演
find_director = re.compile('<li class="fed-col-xs12 fed-col-md6 fed-part-eone"><span class="fed-text-muted">'
                           '导演：</span>(.*?)</li>')
# 简介
find_info = re.compile('<div class="fed-tabs-item fed-hidden">(.*?)</div>')
# 视频来源
find_video = re.compile('')


# 获取数据
def get_data(base_url):
    data_list = []
    for i in range(1, 4):
        url = base_url + f"/vod/show/id/1/page/{i}.html"
        print(f"正在爬取第{i}页的数据")
        html = ask_url(url)      # 保存获取到的网页源码
        if html:
            # 2.逐一解析数据
            soup = BeautifulSoup(html, "html.parser")
            # 查找符合要求的字符串，形成列表.
            title = ''
            for item in soup.find_all("li", class_="fed-list-item fed-padding fed-col-xs4 fed-col-sm3 fed-col-md2"):
                item = str(item)
                try:
                    # 影片详情的链接
                    link = find_link.findall(item)[0]
                    detail_url = base_url + link
                    # 从详情页获取数据
                    detail_html = ask_url(detail_url)
                    # xpath解析
                    doc = etree.HTML(detail_html)
                    detail_soup = BeautifulSoup(detail_html, "html.parser")
                    str_detail_html = str(detail_html)
                    title = find_title.findall(str_detail_html)[0]
                    movie_id = find_id.findall(str_detail_html)[0]
                    category = find_category.findall(str_detail_html)[0]
                    area = remove_tags(find_area.findall(str_detail_html)[0]).replace('&nbsp;', ',')
                    year = remove_tags(find_year.findall(str_detail_html)[0]).replace('&nbsp;', ',')
                    update = find_update.findall(str_detail_html)[0]
                    actors = remove_tags(find_actors.findall(str_detail_html)[0]).replace('&nbsp;', ',')
                    director = remove_tags(find_director.findall(str_detail_html)[0]).replace('&nbsp;', ',')
                    info = str(doc.xpath('//div[@class="fed-tabs-boxs"]//p/text()')[0])\
                        .replace('酷云在线播放电影网站酷云在线播放电影网站', '').strip()
                    # 线路② 酷云备用等标题和链接
                    fin_list = []
                    fin_dict = {}
                    i = 0
                    a_url = doc.xpath('/html/body/div[3]/div/div[2]/div/div[1]/div[1]/ul/li/a/@href')
                    a_text = doc.xpath('/html/body/div[3]/div/div[2]/div/div[1]/div[1]/ul/li/a/text()')
                    for url_fin in a_url:
                        fin_dict[a_text[i]] = get_movie_url(url_fin)
                        fin_list.append(fin_dict)
                        i = i+1
                    # tuple_url = zip(a_url, a_text)
                    # dict_url = [{i[1]:i[0]} for i in tuple_url]
                    print(title)
                    # print(list(dict_url))
                    data = {
                        'title': title,
                        'ID': movie_id,
                        'detailUrl': base_url+link,
                        'category': category,
                        'area': area,
                        'year': year,
                        'update': update,
                        'actors': actors,
                        'director': director,
                        'info': info,
                        'video': fin_list
                    }
                    # print(data)
                    data_list.append(data)
                except Exception as e:
                    print(f"爬取第{i}页的{title}数据失败！")
                    print(e)
                    continue
            # print(f'第{i}页{dataList}')
        else:
            print(f"爬取第{i}页数据失败！")
            continue
        time.sleep(3)

    return data_list


# 线路②: [1-108url]
def get_movie_url(url):
    data_dict = {}
    i = 0
    html = ask_url(url)
    doc = etree.HTML(html)
    all_url = doc.xpath("/html/body/div[3]/div/div[2]/div/div[1]/div[2]/div[1]/ul[2]/li/a/@href")
    all_title = doc.xpath("/html/body/div[3]/div/div[2]/div/div[1]/div[2]/div[1]/ul[2]/li/a/text()")
    print(all_url)
    print('正在爬取视频链接中')
    for url in all_url:
        movie_html = ask_url('https://kuyun.tv'+url)
        movie_doc = etree.HTML(movie_html)
        # print(movie_html)
        movie_url = movie_doc.xpath('//iframe[@id="fed-play-iframe"]/@data-play')[0]
        data_dict[f"{all_title[i]}"] = movie_url
        i = i+1
    return data_dict


# 得到指定一个URL的网页内容
def ask_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0",
        "Cookie": "user_id=1612; user_name=1138491931; group_id=2; group_name=%E9%BB%98%E"
                  "8%AE%A4%E4%BC%9A%E5%91%98; user_check=99292ccc25546a32126251a7a1da3ead; "
                  "user_portrait=%2Fstatic%2Fimages%2Ftouxiang.png; fed_password=bsj13770913798; "
                  "fed_username=1138491931; Hm_lvt_90d65cb348742bcf35c5f677789a4216=1590583490,1590663430,"
                  "1591845311,1592473239; fed_notice=1; "
                  "fed_history=%7Bvideo%3A%5B%7B%22name%22%3A%22%u5927%u536B%B7%u79D1%u6CE2%u83F2%u5C14%u768"
                  "4%u4E2A%u4EBA%u53F2%22%2C%22show%22%3A%22%u4E0D%u9177%u7684%u4E91%22%2C%22link%22%3A%22https"
                  "%3A//kuyun.tv/vod/play/id/60772/sid/1/nid/1.html%22%2C%22num%22%3A%22BD720P%22%7D%5D%7D; "
                  "Hm_lpvt_90d65cb348742bcf35c5f677789a4216=1592479987"
    }
    html = ""
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            html = res.content.decode("utf-8")
            return html
        else:
            return False
    except Exception as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
        return False


# 保存数据
def save_data(data_list, save_path):
    print("save...")


if __name__ == "__main__":
    main()
    # get_movie_url('https://kuyun.tv/vod/play/id/6636/sid/1/nid/1.html')

