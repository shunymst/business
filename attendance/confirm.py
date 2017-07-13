#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import copy
from util import common_module
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


# 勤怠実績明細シナリオ
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
  , r_total.sum_work_time + SUM(p.work_time) as prospects_work_time
  , r_total.sum_over_time + SUM(p.over_time) as prospects_over_time
from
  results r 
  inner join (
   select user_id,sum(work_time) as sum_work_time,sum(over_time) as sum_over_time
   from results
   where user_id = (%s)
   and attendance_date between date_trunc('month', to_date((%s), 'YYYY/MM/DD')) and date_trunc('month', to_date((%s), 'YYYY/MM/DD'))
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
  r.user_id = (%s)
  and r.attendance_date = to_date((%s), 'YYYY/MM/DD') 
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
  , r_total.sum_over_time  
        """
    param = [
        request_json["user_id"],
        request_json["attendance_date"],
        request_json["attendance_date"],
        request_json["user_id"],
        request_json["attendance_date"]
    ]
    results = db_conn.select_dict(sql, param)

    send_content = {}
    if results and len(results) > 0:
        send_content["results"] = convert_date_to_string(results[0])
        send_content["message"] = "OK"
        send_content["results_warning"] = overtime_chack(results[0]["sum_over_time"])
        send_content["prospects_warning"] = overtime_chack(results[0]["prospects_over_time"])
    else:
        send_content["message"] = 'なし'

    return send_content


# 残業超過判断
def overtime_chack(over_time):
    common_module.print_stdout(over_time)
    if (over_time > datetime.timedelta(hours=35)) and (over_time < datetime.timedelta(hours=40)):
        return "[警告]"
    elif over_time >= datetime.timedelta(hours=40):
        return "[超過]"

    return ""


# データ型変更
def convert_date_to_string(send_results):
    dic = copy.deepcopy(send_results)
    for k in dic:
        common_module.print_stdout(type(dic[k]))
        if isinstance(dic[k], datetime.timedelta):
            dic[k] = common_module.format_hour_minute(int(dic[k].total_seconds() / 60))
        elif isinstance(dic[k], datetime.date) or isinstance(dic[k], datetime.time):
            common_module.print_stdout(1)
            dic[k] = str(dic[k])

    return dic


#勤怠予定照会
def plans_work(db_conn, request_json):
    sql = "select name from users where id = (%s)"

    param = [
        request_json['id']
    ]
    results = db_conn.select_dict(sql, param)

    sql2 = """
        select r.attendance_date, to_char(r.attendance_date, 'FMDD日') as date,(ARRAY['日','月','火','水','木','金','土'])[EXTRACT(DOW FROM CAST(attendance_date AS DATE)) + 1] as dow,
        r.results_division,r.start_time,r.end_time 
        from result as r 
        where user_id = (%s) and 
        attendance_date between date_trunc('month', to_date((%s), 'YYYY/MM/DD')) and 
        date_trunc('month', to_date((%s), 'YYYY/MM/DD')) + '1 month' + '-1 Day';
        """

    param2 = [
        request_json['user_id'],
        request_json['"attendance_date'],
        request_json['"attendance_date']
    ]
    results2 = db_conn.select_dict(sql2, param2)

    sql3 = """
        select p.user_id,SUM(p.work_time) as "prospects_work_time",SUM(p.over_time) as "prospects_over_time" 
        from plans as p 
        where p.user_id = (%s) and p.attendance_date between date_trunc('month', to_date((%s), 'YYYY/MM/DD')) and 
        date_trunc('month', to_date((%s), 'YYYY/MM/DD')) + '1 month' + '-1 Day' group by p.user_id;
        """
    param3 = [
        request_json['user_id'],
        request_json['"attendance_date'],
        request_json['"attendance_date']
    ]
    results3 = db_conn.select_dict(sql3, param3)

    send_content = {}

    if (results and len(results) > 0) and (results2 and len(results2) > 0) and (results3 and len(results3) > 0):
        send_content["results"] = convert_date_to_string(results[0])
        send_content["results2"] = convert_date_to_string(results2[0])
        send_content["results3"] = convert_date_to_string(results3[0])
        send_content["message"] = "OK"


    return send_content