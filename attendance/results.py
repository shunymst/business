#!/usr/bin/env python
# -*- coding: utf-8 -*-


def check_result(db_conn, request_json):
    sql = "select attendance_date, status from results where user_id = (%s) and attendance_date = to_date((%s), 'yyyy/mm/dd') "
    param = [
        request_json["user_id"],
        request_json["attendance_date"]
    ]
    results = db_conn.select_dict(sql, param)

    if results and len(results) > 0:
        if results[0]["status"] == "2":
            return "承認済み"
        else:
            return "承認待ち"

    return "未登録"


def calc_time(db_conn, request_json):
    sql = "select attendance_date, status from results where user_id = (%s) and attendance_date = to_date((%s), 'yyyy/mm/dd') "
    param = [
        request_json["user_id"],
        request_json["attendance_date"]
    ]
    results = db_conn.select_dict(sql, param)

    if results and len(results) > 0:
        if results[0]["status"] == "2":
            return "承認済み"
        else:
            return "承認待ち"

    return "未登録"


def insert_work(db_conn, request_json):
    sql = "insert into results values((%s), to_date((%s), 'yyyy/mm/dd'), '1', '1', (%s), to_time((%s), 'yyyy/mm/dd hh24:mi:ss'), to_time((%s), 'yyyy/mm/dd hh24:mi:ss'), to_time((%s), 'hh24:mi:ss'), to_time((%s), 'hh24:mi:ss'), (%s), null, null, (%s), null) "
    param = [
        request_json["user_id"],
        request_json["attendance_date"],
        request_json["work_division"],
        request_json["start_time"],
        request_json["end_time"],
        request_json["work_time"],
        request_json["rest_time"],
        request_json["delay_reason"],
        request_json["remarks"]
    ]
    db_conn.update(sql, param)

    return "OK"


def insert_holiday(db_conn, request_json):
    sql = "insert into results values((%s), to_date((%s), 'yyyy/mm/dd'), '1', '2', null, null, null, null, null, null, (%s), (%s), (%s), null) "
    param = [
        request_json["user_id"],
        request_json["attendance_date"],
        request_json["work_division"],
        request_json["start_time"],
        request_json["end_time"],
        request_json["work_time"],
        request_json["rest_time"],
        request_json["delay_reason"],
        request_json["remarks"]
    ]
    db_conn.update(sql, param)

    return "OK"


if __name__ == "__main__":
    pass