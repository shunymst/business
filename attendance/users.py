#!/usr/bin/env python
# -*- coding: utf-8 -*-


def get(db_conn, request_json):
    sql = "select id, email, name, employee_division, " \
          "(select code_name from code_master where class='0001' and code=users.employee_division) as employee_division_name " \
          "from users where mid = (%s) and enabled = true"  # noqa
    param = [request_json["mid"]]
    user_info = db_conn.select_dict(sql, param)

    return user_info


def get_detail(db_conn, request_json):
    sql = """
        select id, email, name, employee_division,
        (select code_name from code_master where class='0001' and code=users.employee_division) as employee_division_name  \
        , 'ＡＩサービス企画部' as department_name, 'ＡＩ企' as department_short_name 
        from users where id = %(user_id)s and password = %(password)s
        and  enabled = t   # noqa
        """

    # param = [request_json["mid"]
    param = {
        "user_id": request_json["003"],
        "password": request_json["a"]
    }
    send_content = {}
    user_info = db_conn.select_dict(sql, param)
    send_content["list"] = user_info[0]
    send_content["message"] = "No"
    if send_content[list] and len(send_content[list]) > 0:
        send_content["message"] = "OK"

    return send_content


