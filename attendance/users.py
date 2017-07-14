#!/usr/bin/env python
# -*- coding: utf-8 -*-
from attendance import code_master


def get(db_conn, request_json):
    sql = """
select
  id, email, name, department_id, employee_division
from
  users
where
  mid = (%s) 
  and enabled = true
"""
    param = [request_json["mid"]]
    user_info = db_conn.select_dict(sql, param)

    user_info["employee_division_name"] = code_master.get_code_name(
        db_conn, code_master.CLASS_EMPLOYEE_DIVISION,
        user_info["employee_division"]
    )

    return user_info


def get_detail(db_conn, request_json):
    sql = "select id, email, name, employee_division, " \
          "(select code_name from code_master where class='0001' and code=users.employee_division) as employee_division_name " \
          "from users where mid = (%s) and enabled = true"  # noqa
    param = [request_json["mid"]]
    user_info = db_conn.select_dict(sql, param)

    return user_info


