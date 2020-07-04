# -*- coding: utf-8 -*-
import pymysql
import json
import time


# 用来操作数据库的类
class MySQLCommand(object):
    # 类的初始化
    def __init__(self):
        self.host = 'sh-cynosdbmysql-grp-4xojkzw6.sql.tencentcdb.com'
        self.port = 20410  # 端口号
        self.user = 'root'  # 用户名
        self.password = "bsj13770913798"  # 密码
        self.db = "movie"  # 库
        self.table = "movie_detail"  # 表
        self.conn = None
        self.cursor = None

    # 链接数据库
    def connect_mysql(self):
        try:
            self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user,
                                        passwd=self.password, db=self.db, charset='utf8')
            self.cursor = self.conn.cursor()
            print('connect mysql successful.')
        except Exception as e:
            print('connect mysql error.')
            print(e)

    # 插入数据，插入之前先查询是否存在，如果存在就不再插入
    def insert_data(self, my_dict):
        # 注意，这里查询的sql语句url=' %s '中%s的前后要有空格
        sql_exit = f'SELECT image FROM movie_detail  WHERE id = "{my_dict["id"]}"'
        res = self.cursor.execute(sql_exit)
        if res:  # res为查询到的数据条数如果大于0就代表数据已经存在
            print(f'{my_dict["title"]}数据已存在', res)
            return 0
        # 数据不存在才执行下面的插入操作
        try:
            cols = ', '.join(my_dict.keys())  # 用，分割
            # values = '"," '.join(my_dict.values())
            sql = f"INSERT INTO movie_detail VALUES ({my_dict["id"]},'{my_dict["title"]}','{my_dict["info"]}','{my_dict["actors"]}','{my_dict["director"]}','{my_dict["category"]}','{my_dict["area"]}','{my_dict["year"]}','{my_dict["update"]}',{my_dict["rate"]},'{my_dict["status"]}','{my_dict["image"]}','{my_dict["play_url"]}','{my_dict["detail"]}')"
            print(sql)
            # 拼装后的sql如下
            # INSERT INTO home_list (img_path, url, id, title) VALUES
            # ("https://img.huxiucdn.com.jpg"," https://www.huxiu.com90.html"," 12"," ")
            try:
                result = self.cursor.execute(sql)
                insert_id = self.conn.insert_id()  # 插入成功后返回的id
                self.conn.commit()
                # 判断是否执行成功
                if result:
                    print("插入成功", insert_id)
                    return 1
            except pymysql.Error as e:
                # 发生错误时回滚
                self.conn.rollback()
                # 主键唯一，无法插入
                if "key 'PRIMARY'" in e.args[1]:
                    print("数据已存在，未插入数据")
                else:
                    print("插入数据失败，原因 %d: %s" % (e.args[0], e.args[1]))
                    with open('./movieInsertEor.txt', 'a+', encoding="utf-8") as fp:
                        fp.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\t' + my_dict["title"] + '\t'+str(e.args[1]) + '\n')
        except pymysql.Error as e:
            print("数据库错误，原因%d: %s" % (e.args[0], e.args[1]))

    # 查询最后一条数据的id值
    def get_last_id(self):
        sql = "SELECT max(id) FROM " + self.table
        try:
            self.cursor.execute(sql)
            row = self.cursor.fetchone()  # 获取查询到的第一条数据
            if row[0]:
                return row[0]  # 返回最后一条数据的id
            else:
                return 0  # 如果表格为空就返回0
        except:
            print(sql + ' execute failed.')

    def close_mysql(self):
        self.cursor.close()
        self.conn.close()  # 关闭数据库操作类的实例
