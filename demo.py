# -*- coding = utf-8 -*-
# @Time :  18:52
# @Author : balon
# @File : demo.py
# @Software : PyCharm

import re
import time

import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from w3lib.html import remove_tags
from lxml import etree
# from concurrent.futures import ThreadPoolExecutor

from movie_db import MySQLCommand


def main():
    base_url = "https://kuyun.tv"
    params = "/vod/show/id/1/page/{}.html"
    # 爬取网页(循环存储数据库)
    get_data(base_url)


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
# 状态
find_status = re.compile('<span class="fed-list-remarks fed-font-xii fed-text-white fed-text-center">(.*?)</span>')
# 评分
find_rate = re.compile('<span class="fed-list-score fed-font-xii fed-back-green">(.*?)</span>')
# 图片url
find_img = re.compile('<a class="fed-list-pics fed-lazy fed-part-2by3" .* data-original="(.*?)"')


# 获取数据
def get_data(base_url):
    for i in range(1, 725):
        url = base_url + f"/vod/show/id/1/page/{i}.html"
        print(f"正在爬取第{i}页的数据")
        # 保存获取到的网页源码
        html = ask_url(url)
        if html:
            # 2.逐一解析数据
            soup = BeautifulSoup(html, "html.parser")
            # 查找符合要求的字符串，形成列表.
            for item in soup.find_all("li", class_="fed-list-item fed-padding fed-col-xs4 fed-col-sm3 fed-col-md2"):
                try:
                    item = str(item)
                    # 影片详情的链接
                    link = find_link.findall(item)[0]
                    detail_url = base_url + link
                    # 从详情页获取数据
                    detail_html = ask_url(detail_url)
                    # xpath解析
                    doc = etree.HTML(detail_html)
                    str_detail_html = str(detail_html)
                    title = find_title.findall(str_detail_html)[0]
                    movie_id = int(find_id.findall(str_detail_html)[0])
                    category = find_category.findall(str_detail_html)[0]
                    area = remove_tags(find_area.findall(str_detail_html)[0]).replace('&nbsp;', ',')
                    year = remove_tags(find_year.findall(str_detail_html)[0]).replace('&nbsp;', ',')
                    update = find_update.findall(str_detail_html)[0]
                    actors = remove_tags(find_actors.findall(str_detail_html)[0]).replace('&nbsp;', ',')
                    director = remove_tags(find_director.findall(str_detail_html)[0]).replace('&nbsp;', ',')
                    status = find_status.findall(str_detail_html)[0]
                    rate = float(find_rate.findall(str_detail_html)[0])
                    img = find_img.findall(str_detail_html)[0]
                    info = str(doc.xpath('//div[@class="fed-tabs-boxs"]//p/text()')[0])\
                        .replace('酷云在线播放电影网站酷云在线播放电影网站', '').replace('酷云在线播放电影网站=酷云在线播放电影网站', '').strip()
                    # 线路② 酷云备用等标题和链接
                    fin_dict = {}
                    j = 0
                    a_url = doc.xpath('/html/body/div[3]/div/div[2]/div/div[1]/div[1]/ul/li/a/@href')
                    a_text = doc.xpath('/html/body/div[3]/div/div[2]/div/div[1]/div[1]/ul/li/a/text()')
                    print('正在爬取链接中\t'+title)
                    for url_fin in a_url:
                        fin_dict[a_text[j]] = get_movie_url(base_url+url_fin)
                        j = j+1
                    # tuple_url = zip(a_url, a_text)
                    # dict_url = [{i[1]:i[0]} for i in tuple_url]
                    # print(list(dict_url))
                    data = {
                        'id': movie_id,
                        'title': title,
                        'info': info,
                        'actors': actors,
                        'director': director,
                        'category': category,
                        'area': area,
                        'year': year,
                        'update': update,
                        'rate': rate,
                        'status': status,
                        'image': base_url+img,
                        'play_url': fin_dict,
                        'detail': base_url + link
                    }
                    try:
                        # 插入数据，如果已经存在就不在重复插入
                        mysql_command.insert_data(data)
                    except Exception as e:
                        print("插入数据失败", str(e))  # 输出插入失败的报错语句
                        with open('./movieInsertEor.txt', 'a+', encoding="utf-8") as fp:
                            fp.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\t' + str(i) + '\t' + title+'\t'+str(e)+'\n')
                    # 将dict转换为json数据，中文不用ascii码表示.
                    # print(json.dumps(data, ensure_ascii=False))
                    # data_list.append(data)
                except Exception as e:
                    print(f"爬取第{i}页的{title}数据失败！")
                    with open('./movieLog.txt', 'a+', encoding="utf-8") as fp:
                        fp.writelines(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\t' + str(i)+'\t'+title+'\t'+str(e)+'\n')
                    continue
        else:
            print(f"请求第{i}页失败！")
            with open('./requestLog.txt', 'a+', encoding="utf-8") as fp:
                fp.writelines(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\t'+str(i)+'\n')
            continue
        time.sleep(2)


def get_movie_url(url):
    data_dict = {}
    i = 0
    html = ask_url(url)
    doc = etree.HTML(html)
    # 所有级数的a标签和文本
    all_url = doc.xpath('//div[@class="fed-play-item fed-drop-item fed-visible"]//ul[@class="fed-part-rows"]/li/a/@href')
    all_title = doc.xpath('//div[@class="fed-play-item fed-drop-item fed-visible"]'
                          '//ul[@class="fed-part-rows"]/li/a/text()')
    # print('正在爬取视频链接中')
    for url in all_url:
        # 用selenium获取iframe里的src
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        option.add_argument('--no-sandbox')
        option.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome('/usr/bin/chromedriver', options=option)
        browser.get('https://kuyun.tv'+url)
        movie_url = browser.find_element_by_id('fed-play-iframe').get_attribute('src')
        browser.close()
        data_dict[all_title[i]] = movie_url
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


if __name__ == "__main__":
    # 连接数据库
    mysql_command = MySQLCommand()
    mysql_command.connect_mysql()
    # 创建线程池
    # pool = ThreadPoolExecutor(max_workers=3)
    main()
    # 关闭线程池
    # pool.shutdown()
    # 关闭数据库
    mysql_command.close_mysql()
    print("爬取完毕！")
