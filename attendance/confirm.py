#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import copy
from util import common_module
from attendance import users
from attendance import department


# 実績・見込取得処理（個人）
def get_results_prospects_person(db_conn, user_id, attendance_date):
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
  , to_char(date_trunc('month', to_date(%(r.attendance_date)s, 'YYYY/MM/DD')),'FMMM月FMDD日') first_day
  , to_char(date_trunc('month', to_date(%(r.attendance_date)s, 'YYYY/MM/DD'))
   + '1 month' + '-1 Day','FMMM月FMDD日') last_day
  , r_total.sum_work_time
  , r_total.sum_over_time
  , coalesce(r_total.sum_work_time, interval '0') + coalesce(p.sum_work_time, interval '0') as prospects_work_time
  , coalesce(r_total.sum_over_time, interval '0') + coalesce(p.sum_over_time, interval '0') as prospects_over_time 
from
  results r 
  inner join ( 
    select
      user_id
      , sum(work_time) as sum_work_time
      , sum(over_time) as sum_over_time 
    from
      results 
    where
      user_id = %(user_id)s 
      and attendance_date between %(attendance_date_start)s and %(attendance_date_end)s
    group by
      user_id
  ) r_total 
    on r.user_id = r_total.user_id 
  left outer join ( 
    select
      user_id
      , sum(work_time) as sum_work_time
      , sum(over_time) as sum_over_time 
    from
      plans 
    where
      user_id = %(user_id)s 
      and attendance_date between %(attendance_date_start)s and %(attendance_date_end)s
      and not exists ( 
        select
          * 
        from
          results 
        where
          user_id = plans.user_id 
          and attendance_date = plans.attendance_date
      ) 
    group by
      user_id
  ) p
    on r.user_id = p.user_id 
  inner join users u 
    on u.id = r.user_id 
where
  r.user_id = %(user_id)s 
  and r.attendance_date = %(attendance_date)s
"""

    dt_attendance_date = common_module.convert_date(attendance_date)
    param = {
        "user_id": user_id,
        "attendance_date": dt_attendance_date,
        "attendance_date_start": common_module.get_first_day(dt_attendance_date),
        "attendance_date_end": common_module.get_last_day(dt_attendance_date)
    }

    return db_conn.select_dict(sql, param)


def work_confirm(db_conn, request_json):

    results = get_results_prospects_person(db_conn, request_json["user_id"], request_json["attendance_date"])

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


# 勤怠実績照会
def plans_inquiry(db_conn, request_json):

    results = get_results_prospects_person(db_conn, request_json["user_id"], request_json["attendance_date"])

    sql2 = """
            select r.attendance_date, to_char(r.attendance_date, 'FMDD日') as date,
            (ARRAY['日','月','火','水','木','金','土'])[EXTRACT(DOW FROM CAST(attendance_date AS DATE)) + 1] as dow,
            r.results_division,r.start_time,r.end_time 
            from results r 
            where user_id = %(user_id)s and 
            attendance_date between date_trunc('month', to_date(%(attendance_date)s, 'YYYY/MM/DD')) and 
            date_trunc('month', to_date(%(attendance_date)s, 'YYYY/MM/DD')) + '1 month' + '-1 Day'
            order by r.attendance_date
            """

    # param2 = [
    #     request_json["user_id"],
    #     request_json["attendance_date"],
    #     request_json["attendance_date"]
    # ]
    param2 = {
        "user_id": request_json["user_id"],
        "attendance_date": request_json["attendance_date"]
    }
    results2 = db_conn.select_dict(sql2, param2)

    send_content = {}
    plan_list = ""

    if (results and len(results) > 0) and (results2 and len(results2) > 0):
        send_content["results"] = convert_date_to_string(results[0])
        for plan_rec in results2:
            plan_list += common_module.format_date(plan_rec["attendance_date"], "%d日") + "(" + plan_rec["dow"] + ")" + \
                common_module.format_time(plan_rec["start_time"], "%H:%M") + "～" + \
                common_module.format_time(plan_rec["end_time"], "%H:%M") + "\n"
        send_content["result2"] = plan_list
        send_content["message"] = "OK"

    return send_content


# 勤怠予定照会
def plans_work(db_conn, request_json):
    sql = """
        select p.attendance_date, to_char(p.attendance_date, 'FMDD日') as date,
        to_char(date_trunc('month', to_date(%(attendance_date)s, 'YYYY/MM/DD')),'FMMM月FMDD日') first_day,
        to_char(date_trunc('month', to_date(%(attendance_date)s, 'YYYY/MM/DD')) + '1 month' + '-1 Day','FMMM月FMDD日') last_day,
        (ARRAY['日','月','火','水','木','金','土'])[EXTRACT(DOW FROM CAST(attendance_date AS DATE)) + 1] as dow,
        p.results_division,p.start_time,p.end_time
        from plans p 
        where user_id = %(user_id)s and 
        attendance_date between date_trunc('month', to_date(%(attendance_date)s, 'YYYY/MM/DD')) and 
        date_trunc('month', to_date(%(attendance_date)s, 'YYYY/MM/DD')) + '1 month' + '-1 Day'
        order by p.attendance_date
        """

    param = {
        "user_id": request_json["user_id"],
        "attendance_date": request_json["attendance_date"]
    }
    results = db_conn.select_dict(sql, param)

    sql_name = "select name from users where id = %(user_id)s"

    param_name = {
        "user_id": request_json["user_id"]
    }
    results_name = db_conn.select_dict(sql_name, param_name)

    send_content = {}
    plan_nnn = ""

    if results and len(results):
        send_content["results"] = convert_date_to_string(results[0])

        send_content["results_name"] = results_name[0]
        for plan_rec in results:
            plan_nnn += common_module.format_date(plan_rec["attendance_date"], "%d日") + "(" + plan_rec["dow"] + ")" + \
                            common_module.format_time(plan_rec["start_time"], "%H:%M") + "～" + \
                            common_module.format_time(plan_rec["end_time"], "%H:%M") + "\n"
        send_content["results_list"] = plan_nnn
        send_content["message"] = "OK"

    return send_content


# 勤怠実績・見込照会(部門別)
def results_department(db_conn, request_json):

    user_info = users.get(db_conn, request_json)
    department_short_name = department.get_short_name(db_conn, user_info["department_id"])

    send_content = {
        "info": {
            "department_short_name": department_short_name,
            "ym": common_module.format_date(common_module.convert_date(request_json["attendance_date"]), "MM月")
        }
    }
    return send_content
