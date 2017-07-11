#!/usr/bin/env python
# -*- coding: utf-8 -*-
from attendance import code_master
from attendance import interruption


def check_result(db_conn, request_json):
    sql = "select attendance_date, results_division, status, start_time, end_time, holiday_division, remarks from results where user_id = (%s) and attendance_date = to_date((%s), 'yyyy/mm/dd') "  # noqa
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
            work_time = "{}～{}".format(str(result["start_time"]), str(result["end_time"]))
        else:
            work_time = code_master.get_code_name(
                db_conn,
                code_master.CLASS_HOLIDAY_DIVISION,
                result["holiday_division"]
            )

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
    sql = "insert into results values((%s), to_date((%s), 'yyyy/mm/dd'), '1', '2', null, null, null, null, null, null, (%s), (%s), (%s), null) "  # noqa

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


def work_confirm(db_conn, request_json):
    sql = """
      select
  u.name
  , r.results_division
  , r.attendance_date
  , r.start_time
  , r.end_time
  , r.work_time
  , r.holiday_division
  , r.holiday_reason
  , r.remarks
  , r_total.sum_work_time
  , r_total.sum_over_time
  , r_total.sum_work_time + SUM(p.work_time) as "予定作業時間"
  , r_total.sum_over_time + SUM(p.over_time) as "予定時間外"
from
  results r 
  inner join (
  	select user_id,sum(work_time) as sum_work_time,sum(over_time) as sum_over_time
  	from results
  	where user_id = '003'
  	and attendance_date between date_trunc('month', attendance_date) and date_trunc('month', attendance_date)
     + '1 month' + '-1 Day'
     group by user_id
   ) r_total
   on r.user_id = r_total.user_id
     
  left outer join plans p 
    on r.user_id = p.user_id 
              and p.attendance_date between date_trunc('month', r.attendance_date) and date_trunc('month', r.attendance_date) + '1 month' + '-1 Day' 
    and not exists ( 
      select
        * 
      from
        results 
      where
        user_id = p.user_id 
        and attendance_date =p.attendance_date 
    ) 
  inner join users u 
    on u.id = r.user_id 
where
  r.user_id = '003'
  and r.attendance_date = to_date('2017/07/15', 'YYYY/MM/DD') 
group by
  r.results_division
  , u.name
  , r.attendance_date
  , r.start_time
  , r.end_time
  , r.work_time
  , r.holiday_division
  , r.holiday_reason
  , r.remarks
  , r_total.sum_work_time
  , r_total.sum_over_time;  
        """
    param = [
        request_json["user_id"],
        request_json["attedance_date"]
    ]
    results = db_conn.select_dict(sql, param)

    send_content = {}
    if results and len(results) > 0:
        send_content["results"] = results[0]
        send_content["message"] = "OK"
        send_content["sum_work_time"] = overtime_chack(results[0]["sum_work_time"])
        send_content["sum_over_time"] = overtime_chack(results[0]["sum_over_time"])
    else:
        send_content["message"] = 'なし'

    return send_content


def overtime_chack(over_time):
    if over_time > "35:00:00" and over_time < "40:00:00":
        return "[警告]"
        if over_time >= "40:00:00":
            return "[超過]"

    return "安全"
