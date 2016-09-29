#-*- coding:utf8 -*-


import pymysql.cursors
from APPAnalysis.utils import *



class mysql():
    def __init__(self):
        myini = myconf()
        host = myini.host
        port = myini.port
        user = myini.user
        passwd = myini.passwd
        db = myini.db
        self.connection = pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            passwd=passwd,
            db=db,
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor
        )

    def myexec(self, sql):
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
        except Exception as err:
            print("pymysql error:", err)
            logging().error("pymysql error:%s" % err)

    def myselect(self, sql):
        try:
            cursor = self.connection.cursor()
            # with self.connection.cursor() as cursor:
            #     cursor.execute(sql)
            cursor.execute(sql)
            data = cursor.fetchall()
            return data
        except Exception as err:
            print("pymysql error:", err)
            logging().error("pymysql error:%s" % err)

    def __del__(self):
        self.connection.close()
