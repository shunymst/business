#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import attendans_util


def insert(db_conn, request_json):

    sql = "insert into interruption values((%s), to_date((%s), 'yyyy/mm/dd'), (%s), (%s), to_timestamp((%s), 'hh24:mi:ss'), to_timestamp((%s), 'hh24:mi:ss'), (%s)) "  # noqa

    # 中断時間登録
    interruption_time_list = attendans_util.convert_time_list(request_json["interruption_time_list"])
    interruption_division = "1"
    for i, interruption_time in enumerate(interruption_time_list):
        param = [
            request_json["user_id"],
            request_json["attendance_date"],
            interruption_division,
            i + 1,
            interruption_time["start_time"],
            interruption_time["end_time"],
            interruption_time["reason"]
        ]
        db_conn.update(sql, param)

    # # 業務外作業時間登録
    # outside_work_time_list = attendans_util.convert_time_list(request_json["outside_work_time_list"])
    # interruption_division = "2"
    # for i, outside_work_time in enumerate(outside_work_time_list):
    #     param = [
    #         request_json["user_id"],
    #         request_json["attendance_date"],
    #         interruption_division,
    #         i + 1,
    #         outside_work_time["start_time"],
    #         outside_work_time["end_time"],
    #         outside_work_time["reason"]
    #     ]
    #     db_conn.update(sql, param)

    return "OK"


def delete(db_conn, request_json):
    sql = "delete from interruption where user_id = (%s) and attendance_date = to_date((%s), 'yyyy/mm/dd') "
    param = [
        request_json["user_id"],
        request_json["attendance_date"]
    ]
    db_conn.update(sql, param)

    return "OK"
