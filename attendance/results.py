#!/usr/bin/env python
# -*- coding: utf-8 -*-
from attendance import code_master
from attendance import interruption
from util import common_module


def check_result(db_conn, request_json):
    sql = "select attendance_date, results_division, status, work_division, start_time, end_time, holiday_division, holiday_reason, remarks from results where user_id = (%s) and attendance_date = to_date((%s), 'yyyy/mm/dd') "  # noqa
    param = [
        request_json["user_id"],
        request_json["attendance_date"]
    ]
    results = db_conn.select_dict(sql, param)
    status = "未登録"
    division = ""
    work_time = ""
    remarks = ""

    if results and len(results) > 0:
        result = results[0]
        if results[0]["status"] == "2":
            status = "承認済み"
        else:
            status = "承認待ち"

        if results[0]["results_division"] == "1":
            work_division = code_master.get_code_name(
                db_conn,
                code_master.CLASS_WORK_DIVISION,
                result["work_division"]
            )
            division = "勤務区分：{}".format(work_division)

            work_time = "勤務時間：{}～{}".format(str(result["start_time"]), str(result["end_time"]))
        else:
            holiday_division = code_master.get_code_name(
                db_conn,
                code_master.CLASS_HOLIDAY_DIVISION,
                result["holiday_division"]
            )
            division = "休暇区分：{}".format(holiday_division)

            holiday_reason = code_master.get_code_name(
                db_conn,
                code_master.CLASS_HOLIDAY_REASON,
                result["holiday_reason"]
            )
            work_time = "休暇事由：{}".format(holiday_reason)

        remarks = result["remarks"]

    return_result = {
        "status": status,
        "division": division if division else "なし",
        "work_time": work_time if work_time else "なし",
        "remarks": remarks if remarks else "なし",
        "interruption_time": "なし",
        "outside_work_time": "なし",
        "message": "OK"
    }

    return return_result


def insert_work(db_conn, request_json):
    sql = "insert into results values((%s), to_date((%s), 'yyyy/mm/dd'), '1', (%s), '1', (%s), to_timestamp((%s), 'yyyy/mm/dd hh24:mi:ss'), to_timestamp((%s), 'yyyy/mm/dd hh24:mi:ss'), to_timestamp((%s), 'hh24:mi:ss'), to_timestamp((%s), 'hh24:mi:ss'), to_timestamp((%s), 'hh24:mi:ss'), (%s), null, null, (%s), null) "  # noqa

    # 勤務区分コード変換
    work_division = code_master.change_code_by_name(
        db_conn, code_master.CLASS_WORK_DIVISION,
        request_json["work_division"],
        request_json["employee_division"]
    )

    param = [
        request_json["user_id"],
        request_json["attendance_date"],
        request_json["employee_division"],
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
    sql = "insert into results values((%s), to_date((%s), 'yyyy/mm/dd'), '1', (%s), '2', null, null, null, null, null, null, null, (%s), (%s), (%s), null) "  # noqa

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
        request_json["employee_division"],
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


# 実績取得処理
def get(db_conn, user_id, attendance_date):
    sql = """
select
  user_id
  , attendance_date
  , status
  , employee_division
  , results_division
  , work_division
  , start_time
  , end_time
  , work_time
  , rest_time
  , over_time
  , delay_reason
  , holiday_division
  , holiday_reason
  , remarks
  , approver_id
from
  results r 
where
  r.user_id = %(user_id)s 
  and r.attendance_date = %(attendance_date)s
"""

    dt_attendance_date = common_module.convert_date(attendance_date)
    param = {
        "user_id": user_id,
        "attendance_date": dt_attendance_date
    }

    return db_conn.select_dict(sql, param)


# 月別実績取得処理（個人）
def get_monthly_results_of_parson(db_conn, user_id, base_date):
    sql = """
select
  r.user_id
  , sum(r.work_time) as work_time
  , sum(r.over_time) as over_time 
  , sum(case when c.holiday_flag = '1' then 1 else 0 end) holiday_work_count
  , sum(case when r.results_division = '2' then 1 when cm.division3 = '1' then 0.5 else 0 end) holiday_count
from
  results r
inner join
  calendar c
  on c.employee_division = r.employee_division
  and c.calendar_date = r.attendance_date
inner join
  code_master cm
  on cm.class = %(class_work_division)s
  and cm.code = r.work_division
where
  r.user_id = %(user_id)s 
  and r.attendance_date between %(attendance_date_start)s and %(attendance_date_end)s
group by
  r.user_id
"""

    dt_base_date = common_module.convert_date(base_date)
    param = {
        "user_id": user_id,
        "attendance_date_start": common_module.get_first_day(dt_base_date),
        "attendance_date_end": common_module.get_last_day(dt_base_date),
        "class_work_division": code_master.CLASS_WORK_DIVISION
    }

    return db_conn.select_dict(sql, param)


# 月別実績取得処理（部門）
def get_monthly_results_of_department(db_conn, user_id, base_date):
    sql = """
select
  r.department_id
  , sum(r.work_time) as work_time
  , sum(r.over_time) as over_time 
  , sum(case when c.holiday_flag = '1' then 1 else 0 end) holiday_work_count
  , sum(case when r.results_division = '2' then 1 when cm.division3 = '1' then 0.5 else 0 end) holiday_count
from
  users u
inner join
  results r
  on r.user_id = u.id
inner join
  calendar c
  on c.employee_division = r.employee_division
  and c.calendar_date = r.attendance_date
inner join
  code_master cm
  on cm.class = %(class_work_division)s
  and cm.code = r.work_division
where
  u.department_id = %(user_id)s 
  and r.attendance_date between %(attendance_date_start)s and %(attendance_date_end)s
group by
  r.user_id
"""

    dt_base_date = common_module.convert_date(base_date)
    param = {
        "user_id": user_id,
        "attendance_date_start": common_module.get_first_day(dt_base_date),
        "attendance_date_end": common_module.get_last_day(dt_base_date),
        "class_work_division": code_master.CLASS_WORK_DIVISION
    }

    return db_conn.select_dict(sql, param)
