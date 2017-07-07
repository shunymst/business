#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from util.common_module import print_stdout


def get_work_time(db_conn, request_json):
    sql = "select start_time, end_time from time_master where employee_division = (%s) and time_division = '1' "
    param = [request_json["employee_division"]]
    results = db_conn.select_dict(sql, param)

    if results and len(results) > 0:
        return results[0]
    return None


def get_delay_and_early_flag(request_json, work_time):

    dt_start_time = datetime.datetime.strptime(request_json["start_time"].split(" ")[1], "%H:%M:%S")
    dt_end_time = datetime.datetime.strptime(request_json["end_time"].split(" ")[1], "%H:%M:%S")
    work_start_time = datetime.datetime.strptime(str(work_time["start_time"]), "%H:%M:%S")
    work_end_time = datetime.datetime.strptime(str(work_time["end_time"]), "%H:%M:%S")

    print("IN:", str(dt_start_time), str(dt_end_time), str(work_start_time), str(work_end_time))

    # 日またぎ業務の場合
    if dt_start_time > dt_end_time:
        dt_end_time += datetime.timedelta(days=1)

    # 規定勤務時間が日またぎ業務の場合
    if work_start_time > work_end_time:

        # 規定勤務時間の終了時間を+1日
        work_end_time += datetime.timedelta(days=1)

        # 開始時間が規定勤務時間の終了時間より小さい場合は+1日
        if dt_start_time < work_end_time:
            dt_start_time += datetime.timedelta(days=1)

        # 終了時間が規定勤務時間の終了時間より小さい場合は+1日
        if dt_end_time < work_end_time:
            dt_end_time += datetime.timedelta(days=1)

    delay_flag = "0"
    if (work_start_time < dt_start_time) and (dt_start_time < work_end_time):
        delay_flag = "1"
    early_flag = "0"
    if (work_start_time < dt_end_time) and (dt_end_time < work_end_time):
        early_flag = "1"

    print("OUT:", str(dt_start_time), str(dt_end_time), str(work_start_time), str(work_end_time))

    return delay_flag, early_flag


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

    # TODO: 形式変わりそう
    dt_start_time = datetime.datetime.strptime(str_start_time.split(" ")[1], "%H:%M:%S")
    dt_end_time = datetime.datetime.strptime(str_end_time.split(" ")[1], "%H:%M:%S")

    # 日またぎ業務の場合
    if dt_start_time >= dt_end_time:
        dt_end_time += datetime.timedelta(days=1)

    diff_time = dt_end_time - dt_start_time

    total_rest_time_minute = 0
    for i, rest_time in enumerate(rest_time_list):
        rest_start_time = datetime.datetime.strptime(str(rest_time["start_time"]), "%H:%M:%S")
        rest_end_time = datetime.datetime.strptime(str(rest_time["end_time"]), "%H:%M:%S")

        # 作業開始時間より休憩時間の開始時間が先の場合は+1日
        if rest_start_time < dt_start_time:
            rest_start_time += datetime.timedelta(days=1)

        # 作業開始時間より休憩時間の終了時間が先の場合は+1日
        if rest_end_time < dt_start_time:
            rest_end_time += datetime.timedelta(days=1)

        print_stdout(str(rest_start_time))
        print_stdout(str(rest_end_time))

        # if dt_start_time <= rest_start_time <= rest_end_time <= dt_end_time:
        if (dt_start_time <= rest_start_time) and (rest_end_time <= dt_end_time):
            total_rest_time_minute += int((rest_end_time - rest_start_time).total_seconds() / 60)
        # elif dt_start_time <= rest_start_time < dt_end_time:
        elif (dt_start_time <= rest_start_time) and (rest_start_time < dt_end_time):
            total_rest_time_minute += int((dt_end_time - rest_start_time).total_seconds() / 60)
        # elif dt_start_time < rest_end_time <= dt_end_time:
        elif (dt_start_time < rest_end_time) and (rest_end_time <= dt_end_time):
            total_rest_time_minute += int((rest_end_time - dt_start_time).total_seconds() / 60)

        print_stdout(str(total_rest_time_minute))

    work_time_minute = int(diff_time.total_seconds() / 60) - total_rest_time_minute

    return work_time_minute, total_rest_time_minute


if __name__ == "__main__":
    pass
