#!/usr/bin/env python
# -*- coding: utf-8 -*-


def get_holiday_flag(db_conn, request_json):

    sql = "select holiday_flag from calendar where employee_division = (%s) and calendar_date = (%s)"
    param = [request_json["employee_division"], request_json["attendance_date"]]
    results = db_conn.select_dict(sql, param)

    if results and len(results) > 0:
        return results[0]["holiday_flag"]
    return "0"

