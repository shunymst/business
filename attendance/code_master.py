#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import db_connection


def get_work_division(db_conn, request_json):
    sql = "select id, email, name, employee_division, (select code_name from code_master where class='0001' and code=users.employee_division) as employee_division_name from users where mid = (%s) and enabled = true"
    param = [request_json["employee_division"]]
    user_info = db_conn.select_dict(sql, param)

    return user_info


if __name__ == "__main__":
    pass