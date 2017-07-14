#!/usr/bin/env python
# -*- coding: utf-8 -*-


def get(db_conn, request_json):
    sql = "select id, email, name, employee_division, " \
          "(select code_name from code_master where class='0001' and code=users.employee_division) as employee_division_name " \
          "from users where mid = (%s) and enabled = true"  # noqa
    param = {
        request_json["mid"]
    }
    user_info = db_conn.select_dict(sql, param)

    return user_info


def get_detail(db_conn, request_json):
    sql = """
        select id, email, name, employee_division,
        (select code_name from code_master where class='0001' and code=users.employee_division) as employee_division_name  \
        , 'ＡＩサービス企画部' as department_name, 'ＡＩ企' as department_short_name 
        from users where id = %(user_id)s and password = %(password)s
        and  enabled = 't'  
        """ # noqa

    param = {
        "user_id": request_json["user_id"],
        "password": request_json["password"]
    }
    user_info = db_conn.select_dict(sql, param)

    return user_info

