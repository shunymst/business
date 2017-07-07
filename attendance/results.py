#!/usr/bin/env python
# -*- coding: utf-8 -*-
from attendance import code_master

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
    sql = "insert into results values((%s), to_date((%s), 'yyyy/mm/dd'), '1', '1', (%s), to_timestamp((%s), 'yyyy/mm/dd hh24:mi:ss'), to_timestamp((%s), 'yyyy/mm/dd hh24:mi:ss'), to_timestamp((%s), 'hh24:mi:ss'), to_timestamp((%s), 'hh24:mi:ss'), (%s), null, null, (%s), null) "

    # コード変換
    work_division = code_master.change_code_by_name(
        db_conn, code_master.CLASS_WORK_DIVISION,
        request_json["work_division"],
        request_json["employee_division"]
    )

    param = [
        request_json["user_id"],
        request_json["attendance_date"],
        work_division,
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

    # コード変換
    holiday_division = code_master.change_code_by_name(
        db_conn, code_master.CLASS_HOLIDAY_DIVISION,
        request_json["holiday_division"],
        request_json["employee_division"]
    )
    holiday_reason = code_master.change_code_by_name(
        db_conn, code_master.CLASS_HOLIDAY_REASON,
        request_json["holiday_reason"],
        request_json["employee_division"]
    )

    param = [
        request_json["user_id"],
        request_json["attendance_date"],
        request_json["holiday_division"],
        request_json["holiday_reason"],
        request_json["remarks"]
    ]
    db_conn.update(sql, param)

    return "OK"


def delete(db_conn, request_json):
    sql = "delete from results where user_id = (%s) and attendance_date = to_date((%s), 'yyyy/mm/dd') "
    param = [
        request_json["user_id"],
        request_json["attendance_date"]
    ]
    db_conn.update(sql, param)

    return "OK"


if __name__ == "__main__":
    pass
