#!/usr/bin/env python
# -*- coding: utf-8 -*-
from attendance import code_master


def get_work_time(db_conn, request_json):

    # 勤務区分コード変換
    work_division = code_master.change_code_by_name(
        db_conn, code_master.CLASS_WORK_DIVISION,
        request_json["work_division"],
        request_json["employee_division"]
    )

    sql = "select start_time, end_time from time_master where id = (select division2 from code_master where code = (%s)) and time_division = '1' "  # noqa
    param = [work_division]
    results = db_conn.select_dict(sql, param)

    if results and len(results) > 0:
        return results[0]
    return None


def get_rest_time(db_conn, request_json):

    # 勤務区分コード変換
    work_division = code_master.change_code_by_name(
        db_conn, code_master.CLASS_WORK_DIVISION,
        request_json["work_division"],
        request_json["employee_division"]
    )

    sql = "select start_time, end_time from time_master where id = (select division2 from code_master where code = (%s)) and time_division = '2' "  # noqa
    param = [work_division]
    results = db_conn.select_dict(sql, param)

    return results


if __name__ == "__main__":
    pass
