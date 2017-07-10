#!/usr/bin/env python
# -*- coding: utf-8 -*-
CLASS_EMPLOYEE_DIVISION = "0001"
CLASS_WORK_DIVISION = "0002"
CLASS_HOLIDAY_DIVISION = "0003"
CLASS_HOLIDAY_REASON = "0004"
CLASS_INTERRUPTION_DIVISION = "0008"


def get_work_division(db_conn, request_json):
    sql = "select code, code_name from code_master where class = '0002' and division1 = (%s)"
    param = [request_json["employee_division"]]
    results = db_conn.select_dict(sql, param)

    return results


def get_holiday_division(db_conn, request_json):
    sql = "select code, code_name from code_master where class = '0003' and division1 = (%s)"
    param = [request_json["employee_division"]]
    results = db_conn.select_dict(sql, param)

    return results


def get_holiday_reason(db_conn, request_json):
    sql = "select code, code_name from code_master where class = '0004' and division1 = (%s)"
    param = [request_json["employee_division"]]
    results = db_conn.select_dict(sql, param)

    return results


def change_code_by_name(db_conn, class_code, code_name, division1=None):

    sql = "select code from code_master where class = (%s) and code_name = (%s)"
    param = [class_code, code_name]

    if division1:
        sql += " and division1 = (%s)"
        param.append(division1)

    results = db_conn.select_dict(sql, param)

    if results and len(results) > 0:
        return results[0]["code"]

    print("未登録：class={}, code_name={}, division1={}".format(class_code, code_name, division1))
    return ""


def get_code_name(db_conn, class_code, code):

    sql = "select code_name from code_master where class = (%s) and code_name = (%s)"
    param = [class_code, code]

    results = db_conn.select_dict(sql, param)

    if results and len(results) > 0:
        return results[0]["code_name"]

    print("未登録：class={}, code={}".format(class_code, code))
    return ""
