#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask import Flask
from util import common_module
from util import db_connection

# Flaskサーバー設定
app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)  # セッション情報を暗号化するためのキーを設定
app.config["JSON_AS_ASCII"] = False  # 日本語文字化け対策

# INIファイル設定
g_ini_def = common_module.read_ini("conf/environment.ini")["DEFAULT"]
# DB Connection作成
g_db_conn = db_connection.DBConn(g_ini_def["DB_CONNECTION_STR"])

# Routing読込
from routing import attendance  # noqa
from routing import business  # noqa
