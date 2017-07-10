#!/usr/bin/env python
# -*- coding: utf-8 -*-


def get_work_time(db_conn, request_json):
    sql = "select start_time, end_time from time_master where employee_division = (%s) and time_division = '1' "
    param = [request_json["employee_division"]]
    results = db_conn.select_dict(sql, param)

    if results and len(results) > 0:
        return results[0]
    return None


def get_rest_time(db_conn, request_json):
    sql = "select start_time, end_time from time_master where employee_division = (%s) and time_division = '2' "
    param = [request_json["employee_division"]]
    results = db_conn.select_dict(sql, param)

    return results


if __name__ == "__main__":
    pass
