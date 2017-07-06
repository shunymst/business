#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import db_connection


def get_work_division(db_conn, request_json):
    sql = "select code, code_name from code_master where class = '0002' and remarks1 = (%s)"
    param = [request_json["employee_division"]]
    results = db_conn.select_dict(sql, param)

    return results


def get_holiday_division(db_conn,request_json):
    sql = "select code, code_name from code_master where class = '0003' and remarks1 = (%s)"
    param = [request_json["holiday_division"]]
    results = db_conn.select_dict(sql, param)

    return results


def get_holiday_reason(db_conn,request_json):
    sql = "select code, code_name from code_master where class = '0004' and remarks1 = (%s)"
    param = [request_json["holiday_reason"]]
    results = db_conn.select_dict(sql, param)

    return results


if __name__ == "__main__":
    pass