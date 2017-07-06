#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import db_connection


def check_result(db_conn, request_json):
    sql = "select attendance_date, status from results where user_id = (%s) and attendance_date = to_date((%s)) "
    param = [request_json["user_id"], request_json["attendance_date"]]
    results = db_conn.select_dict(sql, param)

    if results and len(results) > 0:
        if results[0]["status"] == "2":
            return "承認済み"
        else:
            return "承認待ち"

    return "未登録"


if __name__ == "__main__":
    pass