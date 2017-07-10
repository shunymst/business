#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import copy
from util.common_module import print_stdout


# 遅刻・早退判定
def get_delay_and_early_flag(request_json, work_time):

    # 作業開始・終了時間 日付変換
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


def get_minute_work_rest_time(str_start_time, str_end_time, rest_time_list, outside_work_time_list,
                              interruption_time_list):

    # TODO: 形式変わる
    dt_start_time = datetime.datetime.strptime(str_start_time.split(" ")[1], "%H:%M:%S")
    dt_end_time = datetime.datetime.strptime(str_end_time.split(" ")[1], "%H:%M:%S")

    # 日またぎ業務の場合
    if dt_start_time > dt_end_time:
        dt_end_time += datetime.timedelta(days=1)

    print_stdout(str(str_start_time))
    print_stdout(str(str_end_time))

    work_time_list = [create_time_json(dt_start_time, dt_end_time)]
    # 休憩時間計算
    total_rest_time_minute = calc_work_time_and_interruption_time(dt_start_time, work_time_list, rest_time_list)

    # 業務外作業時間計算(休憩時間とかぶる場合は休憩時間が優先される)
    total_outside_work_time_minute = calc_work_time_and_interruption_time(dt_start_time, work_time_list, outside_work_time_list)  # noqa

    # 中断時間計算(休憩時間とかぶる場合は休憩時間が優先される)
    total_interruption_time_minute = calc_work_time_and_interruption_time(dt_start_time, work_time_list, interruption_time_list)  # noqa

    diff_time = dt_end_time - dt_start_time
    work_time_minute = \
        int(diff_time.total_seconds() / 60) - total_rest_time_minute - total_outside_work_time_minute - total_interruption_time_minute  # noqa

    return work_time_minute, total_rest_time_minute, total_outside_work_time_minute, total_interruption_time_minute


def calc_work_time_and_interruption_time(dt_start_time, work_time_list, interruption_time_list):
    interruption_time_minute = 0
    for interruption_time in interruption_time_list:
        interruption_start_time = datetime.datetime.strptime(str(interruption_time["start_time"]), "%H:%M:%S")
        interruption_end_time = datetime.datetime.strptime(str(interruption_time["end_time"]), "%H:%M:%S")

        # 日またぎ休憩時間の場合
        if interruption_start_time > interruption_end_time:
            interruption_end_time += datetime.timedelta(days=1)

        # 作業開始時間より中断時間の終了時間が過去の場合は中断時間を+1日で考える
        if interruption_end_time < dt_start_time:
            interruption_start_time += datetime.timedelta(days=1)
            interruption_end_time += datetime.timedelta(days=1)

        print_stdout(str(interruption_start_time))
        print_stdout(str(interruption_end_time))

        work_time_list_roop = copy.deepcopy(work_time_list)
        for work_time in work_time_list_roop:
            if (work_time["start_time"] <= interruption_start_time) \
                    and (interruption_end_time <= work_time["end_time"]):
                work_time_list.remove(work_time)

                if work_time["start_time"] < interruption_start_time:
                    work_time_list.append(
                        create_time_json(work_time["start_time"], interruption_start_time)
                    )
                if interruption_end_time < work_time["end_time"]:
                    work_time_list.append(
                        create_time_json(interruption_end_time, work_time["end_time"])
                    )
                interruption_time_minute += int((interruption_end_time - interruption_start_time).total_seconds() / 60)
                print("1:{}".format(work_time_list))
                break
            elif (work_time["start_time"] <= interruption_start_time) \
                    and (interruption_start_time < work_time["end_time"]):
                work_time_list.remove(work_time)
                if work_time["start_time"] < interruption_start_time:
                    work_time_list.append(
                        create_time_json(work_time["start_time"], interruption_start_time)
                    )
                interruption_time_minute += int((work_time["end_time"] - interruption_start_time).total_seconds() / 60)
                print("2:{}".format(work_time_list))
            elif (work_time["start_time"] < interruption_end_time) and (interruption_end_time <= work_time["end_time"]):
                work_time_list.remove(work_time)
                if interruption_end_time < work_time["end_time"]:
                    work_time_list.append(
                        create_time_json(interruption_end_time, work_time["end_time"])
                    )
                interruption_time_minute += int((interruption_end_time - work_time["start_time"]).total_seconds() / 60)
                print("3:{}".format(work_time_list))
            elif (interruption_start_time <= work_time["start_time"]) \
                    and (work_time["end_time"] <= interruption_end_time):
                work_time_list.remove(work_time)
                interruption_time_minute += int((work_time["end_time"] - work_time["start_time"]).total_seconds() / 60)
                print("4:{}".format(work_time_list))
            else:
                print("5:{}".format(work_time_list))

    return interruption_time_minute


# 時分フォーマット
def format_hour_minute(minute):
    return "{0:02d}".format(int(minute / 60)) + ":" + "{0:02d}".format(int(minute % 60))


# 時間Dict作成
def create_time_json(start_time, end_time):
    return {"start_time": start_time, "end_time": end_time}


# 中断時間リストDict変換処理
def convert_time_list(str_timelist):
    dict_time_list = []
    if str_timelist:
        list_time = str_timelist.split(";")
        for time_part in list_time:
            if time_part:
                dict_time_list.append(
                    {
                        "start_time": time_part[0: time_part.index("～")].split(" ")[1],
                        "end_time": time_part[time_part.index("～") + 1: time_part.index("(")].split(" ")[1],
                        "reason": time_part[time_part.index("(") + 1: len(time_part) - 1]
                    }
                )

    return dict_time_list
