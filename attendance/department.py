#!/usr/bin/env python
# -*- coding: utf-8 -*-


def get(db_conn, department_id):
    sql = "select id, name, short_name from department where id = %(id)s"
    param = {"id": department_id}
    info = db_conn.select_dict(sql, param)

    return info


def get_name(db_conn, department_id):
    info = get(db_conn, department_id)

    if info and len(info) > 0:
        return info[0]["name"]

    return None


def get_short_name(db_conn, department_id):
    info = get(db_conn, department_id)

    if info and len(info) > 0:
        return info[0]["short_name"]

    return None
