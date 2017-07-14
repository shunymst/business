#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 新規ファイル
from util import db_connection
from util import common_module


def main():
    pass


if __name__ == "__main__":
    conn = db_connection.DBConn()

    common_module.print_stdout(conn.select_dict("select %(test)s, %(test2)s, %(test)s", {"test": "a", "test2": "b", }))