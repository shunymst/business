#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 新規ファイル
from util import db_connection
from util import common_module
import json


def main():
    pass


if __name__ == "__main__":
    # INIファイル設定
    g_ini_def = common_module.read_ini("conf/environment.ini")["DEFAULT"]
    # DB Connection作成
    g_db_conn = db_connection.DBConn(g_ini_def["DB_CONNECTION_STR"])
    resuls = g_db_conn.select_dict("select %(test)s as a, %(test2)s as b, %(test)s as c", {"test": "a", "test2": "b", })

    print(json.dumps(resuls, indent=4, separators=(",", ": "), ensure_ascii=False))