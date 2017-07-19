#!/usr/bin/env python
# -*- coding: utf-8 -*-
from attendance import code_master
from attendance import interruption
from util import common_module
import datetime


# 予定取得処理
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
  , holiday_division
  , holiday_reason
  , remarks
  , approver_id
from
  plans 
where
  user_id = %(user_id)s 
  and attendance_date = %(attendance_date)s
"""

    dt_attendance_date = common_module.convert_date(attendance_date)
    param = {
        "user_id": user_id,
        "attendance_date": dt_attendance_date
    }

    return db_conn.select_dict(sql, param)


# 月別見込予定取得処理（個人）
def get_monthly_prospects_of_parson(db_conn, user_id, base_date):
    sql = """
select
  p.user_id
  , sum(p.work_time) as work_time
  , sum(p.over_time) as over_time 
  , sum(case when c.holiday_flag = '1' then 1 else 0 end) holiday_work_count
  , sum(case when p.results_division = '2' then 1 when cm.division3 = '1' then 0.5 else 0 end) holiday_count
from
  plans p
inner join
  calendar c
  on c.employee_division = p.employee_division
  and c.calendar_date = p.attendance_date
left outer join
  code_master cm
  on cm.class = %(class_work_division)s
  and cm.code = p.work_division
where
  p.user_id = %(user_id)s 
  and p.attendance_date between %(attendance_date_start)s and %(attendance_date_end)s
  and not exists(select * from results r where r.user_id = p.user_id and r.attendance_date = p.attendance_date)
group by
  p.user_id
"""

    dt_base_date = common_module.convert_date(base_date)
    param = {
        "user_id": user_id,
        "attendance_date_start": common_module.get_first_day(dt_base_date),
        "attendance_date_end": common_module.get_last_day(dt_base_date),
        "class_work_division": code_master.CLASS_WORK_DIVISION
    }

    return db_conn.select_dict(sql, param)


# 月別見込予定取得処理（部門）
def get_monthly_prospects_of_department(db_conn, department_id, base_date):
    sql = """
select
    u.department_id
  , count(distinct u.id) as user_count
  , sum(p.work_time) as work_time
  , sum(p.over_time) as over_time 
  , sum(case when c.holiday_flag = '1' then 1 else 0 end) holiday_work_count
  , sum(case when p.results_division = '2' then 1 when cm.division3 = '1' then 0.5 else 0 end) holiday_count
from
  users u
inner join
  plans p
  on p.user_id = u.id
inner join
  calendar c
  on c.employee_division = p.employee_division
  and c.calendar_date = p.attendance_date
left outer join
  code_master cm
  on cm.class = %(class_work_division)s
  and cm.code = p.work_division
where
  u.department_id = %(department_id)s 
  and p.attendance_date between %(attendance_date_start)s and %(attendance_date_end)s
  and not exists(select * from results r where r.user_id = p.user_id and r.attendance_date = p.attendance_date)
group by
  u.department_id
"""

    dt_base_date = common_module.convert_date(base_date)
    param = {
        "department_id": department_id,
        "attendance_date_start": common_module.get_first_day(dt_base_date),
        "attendance_date_end": common_module.get_last_day(dt_base_date),
        "class_work_division": code_master.CLASS_WORK_DIVISION
    }

    return db_conn.select_dict(sql, param)


# 見込部門残業超過判断
def prospect_department_overtime(db_conn, department_id, base_date):

    sql = """
        select 
        u.id 
        , sum(p.over_time) as over_time 
        from users u
        inner join
        results r
        on r.user_id = u.id
        inner join
        plans p
        on u.id = p.user.id
  
        where p.attendance_date between %(attendance_date_start)s
        and %(attendance_date_end)s
        and not exists(select * from results r 
        where r.user_id = p.user_id and r.attendance_date = p.attendance_date)
        group by u.id;
        """
    dt_base_date = common_module.convert_date(base_date)
    param = {
        "department_id": department_id,
        "attendance_date_start": common_module.get_first_day(dt_base_date),
        "attendance_date_end": common_module.get_last_day(dt_base_date),
    }
    send_content = {}
    results = db_conn.select_dict(sql, param)

    # common_module.print_stdout(over_time)
    p_warning_count = 0
    p_excess_count = 0
    for plan_rec in results:
        if (plan_rec["sum_over_time"] > datetime.timedelta(hours=35)) \
                and (plan_rec["sum_over_time"] < datetime.timedelta(hours=40)):
            p_warning_count += 1

        elif plan_rec["sum_over_time"] >= datetime.timedelta(hours=40):
            p_excess_count += 1

    send_content["p_warning_count"] = p_warning_count
    send_content["p_excess_count"] = p_excess_count
    return send_content
