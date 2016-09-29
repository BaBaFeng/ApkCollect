# -*- coding: utf8 -*-


import os

from APPAnalysis.utils import *
from APPAnalysis.conf import *
from APPAnalysis.mysql import mysql


class ApkCollect():
    def __init__(self, apk, tableinit=None):
        print("-" * 128)

        self.my = mysql()
        self.apk = apk
        self.apktool_apk = apk[:-4]

        if tableinit == "init":
            self.table_init()

        self.apks()
        self.insert_data_apks()
        if self.exists == False:
            self.apktool()
            self.assets()
            self.libs()
            self.smali()

            print("I: ApkCollect assets data writing.")
            self.insert_data_assets()
            print("I: ApkCollect libs data writing.")
            self.insert_data_libs()
            print("I: ApkCollect smalis data writing.")
            self.insert_data_smalis()

        print("I: ApkCollect [%s] Finished..." % self.AppName)
        logging().info("ApkCollect [%s] Finished..." % self.AppName)

        print("-" * 128)

    def table_init(self):
        print("W: ApkCollect All Table Being initialized..")
        print("W: ApkCollect Being initialized: table apks.")
        self.creat_table_apks()
        print("W: ApkCollect Being initialized: table assets.")
        self.creat_table_assets()
        print("W: ApkCollect Being initialized: table libs.")
        self.creat_table_libs()
        print("W: ApkCollect Being initialized: table smalis.")
        self.creat_table_smalis()
        print("W: ApkCollect Being initialized: table smali_count.")
        self.creat_table_smali_count()
        print("W: ApkCollect Being initialized: table assets_count.")
        self.creat_table_assets_count()
        print("W: ApkCollect Being initialized: table libs_count.")
        self.creat_table_libs_count()

    def apktool(self):
        apk = self.apk
        print("I: ApkCollect Anti compilation: %s" % apk.split("\\")[-1])
        apktool_cmd = "{0} d -f {1} -o {2}".format(APKTOOL, apk, apk[:-4])
        os.system(apktool_cmd)

    def insert_data_apks(self):
        app_name = self.AppName
        pack_name = self.AppPackName
        apk_md5 = self.AppMD5
        version_name = self.AppVersionName
        version_code = self.AppVersionCode
        if self.AppCer != "E: GET APK CERT ERROR...":
            cert = self.AppCer.split("\n")[2].split(": ")[-1]
        else:
            cert = "uncert"

        sql = "SELECT id FROM apks WHERE apk_md5 = '%s'" % self.AppMD5
        data = self.my.myselect(sql)

        if data == ():
            sql = """INSERT INTO apks(app_name,pack_name,apk_md5,version_name,version_code,cert) VALUES("%s","%s","%s","%s","%s","%s")""" % (app_name, pack_name, apk_md5, version_name, version_code, cert)
            self.my.myexec(sql)
            sql = "SELECT id FROM apks WHERE apk_md5 = '%s'" % self.AppMD5
            data = self.my.myselect(sql)
            self.aid = data[0]["id"]

            self.exists = False
        else:
            self.exists = True
            print("W: ApkCollect Apk info Already Exists.")

    def insert_data_libs(self):
        libs_list = self.libs_list
        aid = self.aid

        for libs in libs_list:
            libs = libs.split("\\")
            lib_plat = libs[0]
            lib_name = libs[1]

            sql = """INSERT INTO libs(aid,lib_name,lib_plat) VALUES(%d,"%s","%s")""" % (int(aid), lib_name, lib_plat)
            self.my.myexec(sql)

            sql = "SELECT count FROM libs_count WHERE lib_name = '%s' AND lib_plat = '%s'" % (lib_name, lib_plat)
            data = self.my.myselect(sql)
            if data == ():
                sql = """INSERT INTO libs_count(lib_name,lib_plat,count) VALUES("%s","%s",%d)""" % (lib_name, lib_plat, 1)
                self.my.myexec(sql)
            else:
                sql = "UPDATE libs_count SET count = %d WHERE lib_name = '%s' AND lib_plat = '%s'" % (int(data[0]["count"]) + 1, lib_name, lib_plat)
                self.my.myexec(sql)

    def insert_data_assets(self):
        asstes_list = self.asstes_list
        aid = self.aid

        for asset in asstes_list:
            asset = asset.replace("\\", "/")
            sql = """INSERT INTO assets(aid,asset) VALUES(%d,"%s")""" % (int(aid), asset)
            self.my.myexec(sql)

            sql = "SELECT count FROM assets_count WHERE asset = '%s'" % asset
            data = self.my.myselect(sql)
            if data == ():
                sql = """INSERT INTO assets_count(asset,count) VALUES("%s",%d)""" % (asset, 1)
                self.my.myexec(sql)
            else:
                sql = """UPDATE assets_count SET count = %d WHERE asset='%s'""" % (int(data[0]["count"]) + 1, asset)
                self.my.myexec(sql)

    def insert_data_smalis(self):
        smali_list = self.smali_list
        aid = self.aid

        for smali_name in smali_list:
            sql = """INSERT INTO smalis(aid,smali) VALUES(%d,"%s")""" % (int(aid), smali_name)
            self.my.myexec(sql)

            sql = "SELECT count FROM smali_count WHERE smali = '%s'" % smali_name
            data = self.my.myselect(sql)
            if data == ():
                sql = """INSERT INTO smali_count(smali,count) VALUES("%s",%d)""" % (smali_name, 1)
                self.my.myexec(sql)
            else:
                sql = """UPDATE smali_count SET count = %d WHERE smali='%s'""" % (int(data[0]["count"]) + 1, smali_name)
                self.my.myexec(sql)

    def creat_table_assets(self):
        sql = "SET FOREIGN_KEY_CHECKS=0;"
        self.my.myexec(sql)
        sql = "DROP TABLE IF EXISTS `assets`;"
        self.my.myexec(sql)
        sql = "CREATE TABLE `assets` (\n  `id` int(16) NOT NULL AUTO_INCREMENT,\n  `aid` int(16) NOT NULL,\n  `asset` varchar(512) NOT NULL,\n  PRIMARY KEY (`id`,`aid`),\n  KEY `aid` (`aid`),\n  KEY `id` (`id`) USING BTREE,\n  KEY `asset` (`asset`) USING BTREE,\n  CONSTRAINT `aid_asset` FOREIGN KEY (`aid`) REFERENCES `apks` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION\n) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"
        self.my.myexec(sql)

    def creat_table_libs(self):
        sql = "SET FOREIGN_KEY_CHECKS=0;"
        self.my.myexec(sql)
        sql = "DROP TABLE IF EXISTS `libs`;"
        self.my.myexec(sql)
        sql = "CREATE TABLE `libs` (\n  `id` int(16) NOT NULL AUTO_INCREMENT,\n  `aid` int(16) NOT NULL,\n  `lib_name` varchar(64) NOT NULL,\n  `lib_plat` varchar(64) NOT NULL,\n  PRIMARY KEY (`id`,`aid`),\n  KEY `aid_lib` (`aid`),\n  KEY `id` (`id`) USING BTREE,\n  KEY `lib_name` (`lib_name`) USING BTREE,\n  CONSTRAINT `aid_lib` FOREIGN KEY (`aid`) REFERENCES `apks` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION\n) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"
        self.my.myexec(sql)

    def creat_table_smalis(self):
        sql = "SET FOREIGN_KEY_CHECKS=0;"
        self.my.myexec(sql)
        sql = "DROP TABLE IF EXISTS `smalis`;"
        self.my.myexec(sql)
        sql = "CREATE TABLE `smalis` (\n  `id` int(16) NOT NULL AUTO_INCREMENT,\n  `aid` int(16) NOT NULL,\n  `smali` varchar(512) NOT NULL,\n  PRIMARY KEY (`id`,`aid`),\n  KEY `aid_smali` (`aid`),\n  KEY `id` (`id`) USING BTREE,\n  KEY `smali` (`smali`) USING BTREE,\n  CONSTRAINT `aid_smali` FOREIGN KEY (`aid`) REFERENCES `apks` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION\n) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"
        self.my.myexec(sql)

    def creat_table_apks(self):
        sql = "SET FOREIGN_KEY_CHECKS=0;"
        self.my.myexec(sql)
        sql = "DROP TABLE IF EXISTS `apks`;"
        self.my.myexec(sql)
        sql = "CREATE TABLE `apks` (\n  `id` int(16) NOT NULL AUTO_INCREMENT,\n  `app_name` varchar(64) NOT NULL,\n  `pack_name` varchar(64) NOT NULL,\n  `apk_md5` varchar(32) NOT NULL,\n  `version_name` varchar(64) NOT NULL,\n  `version_code` int(16) NOT NULL,\n  `cert` varchar(64) DEFAULT NULL,\n  PRIMARY KEY (`id`),\n  KEY `id` (`id`) USING BTREE,\n  KEY `pack_name` (`pack_name`) USING BTREE\n) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"
        self.my.myexec(sql)

    def creat_table_smali_count(self):
        sql = "SET FOREIGN_KEY_CHECKS=0;"
        self.my.myexec(sql)
        sql = "DROP TABLE IF EXISTS `smali_count`;"
        self.my.myexec(sql)
        sql = "CREATE TABLE `smali_count` (\n  `id` int(16) NOT NULL AUTO_INCREMENT,\n  `smali` varchar(512) NOT NULL,\n  `count` int(16) NOT NULL,\n  PRIMARY KEY (`id`),\n  KEY `id` (`id`) USING BTREE,\n  KEY `smali` (`smali`) USING BTREE,\n  KEY `count` (`count`) USING BTREE\n) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"
        self.my.myexec(sql)

    def creat_table_assets_count(self):
        sql = "SET FOREIGN_KEY_CHECKS=0;"
        self.my.myexec(sql)
        sql = "DROP TABLE IF EXISTS `assets_count`;"
        self.my.myexec(sql)
        sql = "CREATE TABLE `assets_count` (\n  `id` int(16) NOT NULL AUTO_INCREMENT,\n  `asset` varchar(512) NOT NULL,\n  `count` int(16) NOT NULL,\n  PRIMARY KEY (`id`),\n  KEY `id` (`id`) USING BTREE,\n  KEY `asset` (`asset`) USING BTREE,\n  KEY `count` (`count`) USING BTREE\n) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"
        self.my.myexec(sql)

    def creat_table_libs_count(self):
        sql = "SET FOREIGN_KEY_CHECKS=0;"
        self.my.myexec(sql)
        sql = "DROP TABLE IF EXISTS `libs_count`;"
        self.my.myexec(sql)
        sql = "CREATE TABLE `libs_count` (\n  `id` int(16) NOT NULL AUTO_INCREMENT,\n  `lib_name` varchar(512) NOT NULL,\n  `lib_plat` varchar(64) NOT NULL,\n  `count` int(16) NOT NULL,\n  PRIMARY KEY (`id`),\n  KEY `id` (`id`) USING BTREE,\n  KEY `lib_name` (`lib_name`) USING BTREE,\n  KEY `lib_plat` (`lib_plat`) USING BTREE,\n  KEY `count` (`count`) USING BTREE\n) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"
        self.my.myexec(sql)

    def assets(self):
        asstes_list = []
        assets = os.path.join(self.apktool_apk, "assets")
        for dirs, Folders, Files in os.walk(assets):
            for File in Files:
                ass = os.path.join(dirs, File)
                asstes_list.append(ass.replace(self.apktool_apk, "")[1:])

        self.asstes_list = asstes_list

    def libs(self):
        libs_list = []
        libs = os.path.join(self.apktool_apk, "lib")
        for dirs, Folders, Files in os.walk(libs):
            for File in Files:
                ass = os.path.join(dirs, File)
                libs_list.append(ass.replace(self.apktool_apk, "")[5:])

        self.libs_list = libs_list

    def smali(self):
        smali_list = []
        smali = os.path.join(self.apktool_apk, "smali")
        for dirs, Folders, Files in os.walk(smali):
            for File in Files:
                ass = os.path.join(dirs, File)
                smali_list.append(ass.replace(self.apktool_apk, "")[7:-6].replace("\\", "."))

        self.smali_list = smali_list

    def apks(self):
        # Apk basic info
        appinfo = AppInfo(self.apk)
        self.AppName = appinfo.AppName()
        self.AppPackName = appinfo.AppPackName()
        self.AppHomeActivity = appinfo.AppHomeActivity()
        self.AppVersionName = appinfo.AppVersionName()
        self.AppVersionCode = appinfo.AppVersionCode()
        self.AppCer = appinfo.AppCer()
        self.AppMD5 = appinfo.AppMD5()
        self.SdkVersion = appinfo.SdkVersion()
