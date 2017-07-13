#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 新規ファイル
import psycopg2
import psycopg2.extras
from util import common_module


# DB接続クラス
class DBConn(object):
    __conn = None

    # 初期化
    def __init__(self, connection_str):
        self.__conn = psycopg2.connect(connection_str)

    # デストラクタ
    def __del__(self):
        # print("DEBUG: DBConn.__del__")
        if self.__conn and not self.__conn.closed:
            # コネクション破棄
            self.__conn.close()
            # print("DEBUG: DBConn.__del__:self.__conn.close()")

    # 参照系 SQL実行
    def select(self, sql, params=None):
        try:

            # TODO: 辞書型カーソルを定義しているつもりだが、keyが付与されていない
            # カーソル取得
            dict_cur = self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # SQL実行
            dict_cur.execute(sql, params)
            result = dict_cur.fetchall()

            # コミット(※execute時に参照でもトランザクションが自動で開始されてしまうので明示的にコミットが必要)
            self.__conn.commit()

            # カーソル破棄
            dict_cur.close()

            result_dict = []
            for row in result:
                result_dict.append(dict(row))

            return result

        except psycopg2.Error:
            # ロールバック
            self.__conn.rollback()
            raise
        except Exception:
            # ロールバック
            self.__conn.rollback()
            raise

    # 参照系 SQL実行(カラム名のdict型で返却)
    def select_dict(self, sql, params=None):
        try:
            common_module.print_stdout("---------------SQL---------------")
            common_module.print_stdout(sql)
            common_module.print_stdout("---------------PARAM---------------")
            common_module.print_stdout(params)
            # Dictに格納 fetchall不可、順序保持不可
            # カーソル取得
            dict_cur = self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # SQL実行
            dict_cur.execute(sql, params)
            result = []
            for cur_row in dict_cur:
                result.append(dict(cur_row))

            # コミット(※execute時に参照でもトランザクションが自動で開始されてしまうので明示的にコミットが必要)
            self.__conn.commit()

            # カーソル破棄
            dict_cur.close()

            common_module.print_stdout("---------------COUNT---------------")
            common_module.print_stdout(len(result))

            return result

        except psycopg2.Error:
            # ロールバック
            self.__conn.rollback()
            raise
        except Exception:
            # ロールバック
            self.__conn.rollback()
            raise

    # 更新系 SQL実行
    def update(self, sql, params=None):
        try:

            # カーソル取得
            cur = self.__conn.cursor()

            # SQL実行
            cur.execute(sql, params)

            # コミット
            self.__conn.commit()

        except psycopg2.Error:
            # ロールバック
            self.__conn.rollback()
            raise
        except Exception:
            # ロールバック
            self.__conn.rollback()
            raise
