#!/usr/bin/env python
# -*- coding: utf-8 -*-


def get_holiday_flag(db_conn, request_json):

    sql = "select holiday_flag from calendar where employee_division = (%s)"
    param = [request_json["employee_division"]]
    results = db_conn.select_dict(sql, param)

    if results and len(results) > 0:
        return results[0]
    return "0"

