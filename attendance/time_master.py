#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from util.common_module import print_stdout


def get_rest_time(db_conn, request_json):
    sql = "select start_time, end_time from time_master where employee_division = (%s) and time_division = '2' "
    param = [request_json["employee_division"]]
    results = db_conn.select_dict(sql, param)

    return get_minute_work_rest_time(
        request_json["start_time"],
        request_json["end_time"],
        results
    )


def get_minute_work_rest_time(str_start_time, str_end_time, rest_time_list):

    dt_start_time = datetime.datetime.strptime(str_start_time.split(" ")[1], "%H:%M:%S")
    dt_end_time = datetime.datetime.strptime(str_end_time.split(" ")[1], "%H:%M:%S")
    if dt_start_time >= dt_end_time:
        dt_end_time += datetime.timedelta(days=1)
    diff_time = dt_end_time - dt_start_time

    total_rest_time_minute = 0
    for i, rest_time in enumerate(rest_time_list):
        rest_start_time = datetime.datetime.strptime(str(rest_time["start_time"]), "%H:%M:%S")
        if rest_start_time < dt_start_time:
            rest_start_time += datetime.timedelta(days=1)

        rest_end_time = datetime.datetime.strptime(str(rest_time["end_time"]), "%H:%M:%S")
        if rest_end_time < dt_start_time:
            rest_end_time += datetime.timedelta(days=1)

        print_stdout(rest_time["start_time"])
        print_stdout(rest_time["end_time"])
        print_stdout(rest_start_time)
        print_stdout(rest_end_time)

        if dt_start_time <= rest_start_time and rest_end_time <= dt_end_time:
            total_rest_time_minute += int((rest_end_time - rest_start_time).total_seconds() / 60)
        elif dt_start_time <= rest_start_time and rest_end_time > dt_end_time:
            total_rest_time_minute += int((rest_end_time - dt_end_time).total_seconds() / 60)
        elif dt_start_time > rest_start_time and rest_end_time <= dt_end_time:
            total_rest_time_minute += int((dt_start_time - rest_start_time).total_seconds() / 60)

        print_stdout(total_rest_time_minute)

    work_time_minute = int(diff_time.total_seconds() / 60) - total_rest_time_minute

    return work_time_minute, total_rest_time_minute


if __name__ == "__main__":
    pass
