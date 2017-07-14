#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import copy
from util import common_module
from attendance import code_master
from attendance import interruption
from attendance import confirm


# 勤怠実績・見込照会(部門別)
def results_department(db_conn, request_json):
    sql = """
select
 d.id
 , d.short_name
 , to_char(to_date(%(attendance_date)s, 'YYYY/MM/DD'), 'MM月') as month
 , count(distinct coalesce(r.id, p.id)) as user_count
 , sum(r.work_time) as r_work_time
 , sum(r.over_time) as r_over_time
 , sum(r.holiday_work_count) as r_holiday_work_count
 , sum(case when r.over_time >= interval '30 hours' and r.over_time < interval '40 hours' then 1 else 0 end) as r_warning_cnt
 , sum(case when r.over_time >= interval '40 hours' then 1 else 0 end) as r_excess_cnt
 , sum(coalesce(r.work_time, interval '0') + coalesce(p.work_time, interval '0')) as p_work_time
 , sum(coalesce(r.over_time, interval '0') + coalesce(p.over_time, interval '0')) as p_over_time
 , coalesce(sum(r.holiday_work_count), 0) + coalesce(sum(p.holiday_work_count), 0) as p_holiday_work_count
 , sum(case when coalesce(r.over_time, interval '0') + coalesce(p.over_time, interval '0') >= interval '30 hours' and coalesce(r.over_time, interval '0') + coalesce(p.over_time, interval '0') < interval '40 hours' then 1 else 0 end) as p_warning_cnt
 , sum(case when coalesce(r.over_time, interval '0') + coalesce(p.over_time, interval '0') >= interval '40 hours' then 1 else 0 end) as p_excess_cnt
from
 department d
left outer join (
 select
  u.id, sum(r.work_time) as work_time, sum(r.over_time) as over_time, sum(case when c.holiday_flag = '1' then 1 else 0 end) holiday_work_count
 from
  users u
 inner join
  results r
 on
  r.user_id = u.id
 inner join
  calendar c
 on
  c.employee_division = r.employee_division
  and c.calendar_date = r.attendance_date
 where 
  u.department_id = %(department_id)s
  and r.attendance_date between date_trunc('month', to_date(%(attendance_date)s, 'YYYY/MM/DD')) and date_trunc('month', to_date(%(attendance_date)s, 'YYYY/MM/DD')) + '1 month' + '-1 Day'
 group by
   u.id
) r
on 1 = 1
left outer join (
 select
  u.id, sum(p.work_time) as work_time, sum(p.over_time) as over_time, sum(case when c.holiday_flag = '1' then 1 else 0 end) holiday_work_count
 from
  users u
 inner join
  plans p
 on
  p.user_id = u.id
 inner join
  calendar c
 on
  c.employee_division = p.employee_division
  and c.calendar_date = p.attendance_date
 where 
  u.department_id = %(department_id)s
  and p.attendance_date between date_trunc('month', to_date(%(attendance_date)s, 'YYYY/MM/DD')) and date_trunc('month', to_date(%(attendance_date)s, 'YYYY/MM/DD')) + '1 month' + '-1 Day'
  and not exists(select * from results r where r.user_id = p.user_id and r.attendance_date = p.attendance_date)
 group by
   u.id
) p
on
 r.id = p.id
where
 d.id = %(department_id)s
group by
 d.id
 , d.name
 , d.short_name
 """

    param = {
        "department_id": request_json["department_id"],
        "attendance_date": request_json["attendance_date"]
    }
    results = db_conn.select_dict(sql, param)

    send_content = {}

    if results and len(results):
        send_content["results"] = confirm.convert_date_to_string(results[0])
        send_content["message"] = "OK"
    else:
        send_content["message"] = "NG"

    return send_content


# 勤怠実績・見込照会(個人別)
def results_person(db_conn, request_json):
    sql = """
select
 u.id
 , u.name
 , d.id
 , d.short_name
 , to_char(to_date(%(attendance_date)s, 'YYYY/MM/DD'), 'MM月') as month
 , r.work_time as r_work_time
 , r.over_time as r_over_time
 , r.holiday_work_count as r_holiday_work_count
 , case when r.over_time >= interval '30 hours' and r.over_time < interval '40 hours' then 1 else 0 end as r_warning_cnt
 , case when r.over_time >= interval '40 hours' then 1 else 0 end as r_excess_cnt
 , coalesce(r.work_time, interval '0') + coalesce(p.work_time, interval '0') as p_work_time
 , coalesce(r.over_time, interval '0') + coalesce(p.over_time, interval '0') as p_over_time
 , coalesce(r.holiday_work_count, 0) + coalesce(p.holiday_work_count, 0) as p_holiday_work_count
 , case when coalesce(r.over_time, interval '0') + coalesce(p.over_time, interval '0') >= interval '30 hours' and coalesce(r.over_time, interval '0') + coalesce(p.over_time, interval '0') < interval '40 hours' then 1 else 0 end as p_warning_cnt
 , case when coalesce(r.over_time, interval '0') + coalesce(p.over_time, interval '0') >= interval '40 hours' then 1 else 0 end as p_excess_cnt
from
 users u
inner join
 department d
on
 u.department_id = d.id
left outer join (
 select
  u.id, sum(r.work_time) as work_time, sum(r.over_time) as over_time, sum(case when c.holiday_flag = '1' then 1 else 0 end) holiday_work_count
 from
  users u
 inner join
  results r
 on
  r.user_id = u.id
 inner join
  calendar c
 on
  c.employee_division = r.employee_division
  and c.calendar_date = r.attendance_date
 where 
  u.id = %(user_id)s
  and r.attendance_date between date_trunc('month', to_date(%(attendance_date)s, 'YYYY/MM/DD')) and date_trunc('month', to_date(%(attendance_date)s, 'YYYY/MM/DD')) + '1 month' + '-1 Day'
 group by
   u.id
) r
on 1 = 1
left outer join (
 select
  u.id, sum(p.work_time) as work_time, sum(p.over_time) as over_time, sum(case when c.holiday_flag = '1' then 1 else 0 end) holiday_work_count
 from
  users u
 inner join
  plans p
 on
  p.user_id = u.id
 inner join
  calendar c
 on
  c.employee_division = p.employee_division
  and c.calendar_date = p.attendance_date
 where 
  u.id = %(user_id)s
  and p.attendance_date between date_trunc('month', to_date(%(attendance_date)s, 'YYYY/MM/DD')) and date_trunc('month', to_date(%(attendance_date)s, 'YYYY/MM/DD')) + '1 month' + '-1 Day'
  and not exists(select * from results r where r.user_id = p.user_id and r.attendance_date = p.attendance_date)
 group by
   u.id
) p
on
 r.id = p.id
where 
 u.id = %(user_id)s
 """

    param = {
        "department_id": request_json["department_id"],
        "attendance_date": request_json["attendance_date"]
    }
    results = db_conn.select_dict(sql, param)

    send_content = {}

    if results and len(results):
        send_content["results"] = confirm.convert_date_to_string(results[0])
        send_content["message"] = "OK"
    else:
        send_content["message"] = "NG"

    return send_content


# 勤怠実績・見込照会(個人別)
def holiday_person(db_conn, request_json):
    sql = """
select
 d.id
 , d.short_name
 , to_char(to_date(%(attendance_date)s, 'YYYY/MM/DD'), 'MM月') as month
 , count(distinct coalesce(r.id, p.id)) as user_count
 , sum(r.work_time) as r_work_time
 , sum(r.over_time) as r_over_time
 , sum(r.holiday_work_count) as r_holiday_work_count
 , sum(case when r.over_time >= interval '30 hours' and r.over_time < interval '40 hours' then 1 else 0 end) as r_warning_cnt
 , sum(case when r.over_time >= interval '40 hours' then 1 else 0 end) as r_excess_cnt
 , sum(coalesce(r.work_time, interval '0') + coalesce(p.work_time, interval '0')) as p_work_time
 , sum(coalesce(r.over_time, interval '0') + coalesce(p.over_time, interval '0')) as p_over_time
 , coalesce(sum(r.holiday_work_count), 0) + coalesce(sum(p.holiday_work_count), 0) as p_holiday_work_count
 , sum(case when coalesce(r.over_time, interval '0') + coalesce(p.over_time, interval '0') >= interval '30 hours' and coalesce(r.over_time, interval '0') + coalesce(p.over_time, interval '0') < interval '40 hours' then 1 else 0 end) as p_warning_cnt
 , sum(case when coalesce(r.over_time, interval '0') + coalesce(p.over_time, interval '0') >= interval '40 hours' then 1 else 0 end) as p_excess_cnt
from
 department d
left outer join (
 select
  u.id, sum(r.work_time) as work_time, sum(r.over_time) as over_time, sum(case when c.holiday_flag = '1' then 1 else 0 end) holiday_work_count
 from
  users u
 inner join
  results r
 on
  r.user_id = u.id
 inner join
  calendar c
 on
  c.employee_division = r.employee_division
  and c.calendar_date = r.attendance_date
 where 
  u.department_id = %(department_id)s
  and r.attendance_date between date_trunc('month', to_date(%(attendance_date)s, 'YYYY/MM/DD')) and date_trunc('month', to_date(%(attendance_date)s, 'YYYY/MM/DD')) + '1 month' + '-1 Day'
 group by
   u.id
) r
on 1 = 1
left outer join (
 select
  u.id, sum(p.work_time) as work_time, sum(p.over_time) as over_time, sum(case when c.holiday_flag = '1' then 1 else 0 end) holiday_work_count
 from
  users u
 inner join
  plans p
 on
  p.user_id = u.id
 inner join
  calendar c
 on
  c.employee_division = p.employee_division
  and c.calendar_date = p.attendance_date
 where 
  u.department_id = %(department_id)s
  and p.attendance_date between date_trunc('month', to_date(%(attendance_date)s, 'YYYY/MM/DD')) and date_trunc('month', to_date(%(attendance_date)s, 'YYYY/MM/DD')) + '1 month' + '-1 Day'
  and exists(select * from results r where r.user_id = p.user_id and r.attendance_date = p.attendance_date)
 group by
   u.id
) p
on r.id = p.id
where
 d.id = %(department_id)s
group by
 d.id
 , d.name
 , d.short_name
 """

    param = {
        "department_id": request_json["department_id"],
        "attendance_date": request_json["attendance_date"]
    }
    results = db_conn.select_dict(sql, param)

    send_content = {}

    if results and len(results):
        send_content["results"] = confirm.convert_date_to_string(results[0])
        send_content["message"] = "OK"
    else:
        send_content["message"] = "NG"

    return send_content
