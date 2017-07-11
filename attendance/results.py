#!/usr/bin/env python
# -*- coding: utf-8 -*-
from attendance import code_master
from attendance import interruption


def check_result(db_conn, request_json):
    sql = "select attendance_date, results_division, status, start_time, end_time, holiday_division, holiday_reason, remarks from results where user_id = (%s) and attendance_date = to_date((%s), 'yyyy/mm/dd') "  # noqa
    param = [
        request_json["user_id"],
        request_json["attendance_date"]
    ]
    results = db_conn.select_dict(sql, param)
    status = "未登録"
    work_time = None
    remarks = None

    if results and len(results) > 0:
        result = results[0]
        if results[0]["status"] == "2":
            status = "承認済み"
        else:
            status = "承認待ち"

        if results[0]["results_division"] == "1":
            work_time = "勤務時間：{}～{}".format(str(result["start_time"]), str(result["end_time"]))
        else:
            holiday_reason = code_master.get_code_name(
                db_conn,
                code_master.CLASS_HOLIDAY_REASON,
                result["holiday_reason"]
            )
            work_time = "休暇事由：" + holiday_reason

        remarks = result["remarks"]

    return_result = {
        "status": status,
        "work_time": work_time if work_time else "なし",
        "remarks": remarks if remarks else "なし",
        "interruption_time": "なし",
        "outside_work_time": "なし",
        "message": "OK"
    }

    return return_result


def insert_work(db_conn, request_json):
    sql = "insert into results values((%s), to_date((%s), 'yyyy/mm/dd'), '1', '1', (%s), to_timestamp((%s), 'yyyy/mm/dd hh24:mi:ss'), to_timestamp((%s), 'yyyy/mm/dd hh24:mi:ss'), to_timestamp((%s), 'hh24:mi:ss'), to_timestamp((%s), 'hh24:mi:ss'), to_timestamp((%s), 'hh24:mi:ss'), (%s), null, null, (%s), null) "  # noqa

    # 勤務区分コード変換
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
        request_json["over_time"],
        request_json["delay_reason"],
        request_json["remarks"]
    ]
    db_conn.update(sql, param)

    interruption.insert(db_conn, request_json)

    return "OK"


def insert_holiday(db_conn, request_json):
    sql = "insert into results values((%s), to_date((%s), 'yyyy/mm/dd'), '1', '2', null, null, null, null, null, null, null, (%s), (%s), (%s), null) "  # noqa

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
        holiday_division,
        holiday_reason,
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

    interruption.delete(db_conn, request_json)

    return "OK"
