#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import routing_util
from flask import request
from routing import app, g_db_conn
from util import attendans_util
from attendance import code_master
from attendance import results
from attendance import time_master
from attendance import users
from attendance import calendar
from attendance import confirm


# ユーザー情報取得
@app.route("/attendance/user/get", methods=["GET", "POST"])
def attendance_users_get():

    request_json = routing_util.get_request_param(request)

    user_info = users.get(g_db_conn, request_json)

    if user_info and len(user_info) > 0:
        send_content = {
            "user_info": user_info[0],
            "message": "OK"
        }
    else:
        send_content = {
            "message": "Not Found"
        }

    return routing_util.create_result_json(send_content)


# アカウント認証
@app.route("/attendance/user/get_detail", methods=["GET", "POST"])
def attendance_users_get_detail():
    request_json = routing_util.get_request_param(request)

    user_info = users.get_detail(g_db_conn, request_json)

    send_content = {"list": user_info[0],
                    "message": "No"}

    if send_content["list"] and len(send_content["list"]) > 0:
        send_content["message"] = "OK"

    return routing_util.create_result_json(send_content)


# 実績登録初期化
@app.route("/attendance/result/init", methods=["GET", "POST"])
def attendance_result_init():

    # request_json = routing_util.get_request_param(request)

    send_content = {
        "remarks": "なし",
        "interruption_time": "なし",
        # "outside_work_time": "なし"
    }

    return routing_util.create_result_json(send_content)


# 実績登録情報確認
@app.route("/attendance/result/check_result", methods=["GET", "POST"])
def attendance_result_check_result():

    request_json = routing_util.get_request_param(request)

    send_content = results.check_result(g_db_conn, request_json)

    return routing_util.create_result_json(send_content)


# 勤務時間、休憩時間、中断時間計算
@app.route("/attendance/result/calc_time", methods=["GET", "POST"])
def attendance_result_calc_time():

    request_json = routing_util.get_request_param(request)

    # 勤務時間取得
    work_time = time_master.get_work_time(g_db_conn, request_json)

    # 休憩時間取得
    rest_time_list = time_master.get_rest_time(g_db_conn, request_json)

    # 祝日フラグ取得
    holiday_flag = calendar.get_holiday_flag(g_db_conn, request_json)

    # 中断時間・業務外勤務時間設定
    interruption_time_list = attendans_util.convert_time_list(request_json["interruption_time_list"])
    # outside_work_time_list = attendans_util.convert_time_list(request_json["outside_work_time_list"])

    # 作業時間・休憩時間・中断時間・残業時間計算
    work_time_minute, total_rest_time_minute, total_interruption_time_minute, total_over_time_minute = \
        attendans_util.get_minute_work_rest_time(
            request_json["start_time"],
            request_json["end_time"],
            rest_time_list,
            interruption_time_list,
            # outside_work_time_list
            work_time,
            holiday_flag
        )

    str_work_time = attendans_util.format_hour_minute(work_time_minute)
    str_rest_time = attendans_util.format_hour_minute(total_rest_time_minute)
    str_interruption_time = attendans_util.format_hour_minute(total_interruption_time_minute)
    # str_outside_work_time = attendans_util.format_hour_minute(total_outside_work_time_minute)
    str_over_time = attendans_util.format_hour_minute(total_over_time_minute)

    # 遅刻・早退判定取得
    delay_flag = "0"
    early_flag = "0"
    if holiday_flag:
        delay_flag, early_flag = attendans_util.get_delay_and_early_flag(request_json, work_time)

    send_content = {
        "work_time": str_work_time,
        "rest_time": str_rest_time,
        "interruption_time": str_interruption_time,
        # "outside_work_time": str_outside_work_time,
        "over_time": str_over_time,
        "delay_early_flag": "1" if delay_flag == "1" or early_flag == "1" else "0",
        "message": "OK"
    }

    return routing_util.create_result_json(send_content)


# 勤怠実績登録(勤務)
@app.route("/attendance/result/insert/work", methods=["GET", "POST"])
def attendance_result_insert_work():

    request_json = routing_util.get_request_param(request)

    results.delete(g_db_conn, request_json)
    message = results.insert_work(g_db_conn, request_json)
    send_content = {
        "message": message
    }

    return routing_util.create_result_json(send_content)


# 勤怠実績登録(休暇)
@app.route("/attendance/result/insert/holiday", methods=["GET", "POST"])
def attendance_result_insert_holiday():

    request_json = routing_util.get_request_param(request)

    results.delete(g_db_conn, request_json)
    message = results.insert_holiday(g_db_conn, request_json)
    send_content = {
        "message": message
    }

    return routing_util.create_result_json(send_content)


# 勤怠実績取消
@app.route("/attendance/result/delete", methods=["GET", "POST"])
def attendance_result_delete():

    request_json = routing_util.get_request_param(request)
    message = results.delete(g_db_conn, request_json)
    send_content = {
        "message": message
    }

    return routing_util.create_result_json(send_content)


# 勤務区分リスト取得
@app.route("/attendance/code/work_division", methods=["GET", "POST"])
def attendance_code_work_division():

    request_json = routing_util.get_request_param(request)
    code_list = code_master.get_work_division(g_db_conn, request_json)
    send_content = {
        "code_list": code_list,
        "message": "OK"
    }

    return routing_util.create_result_json(send_content)


# 休暇区分リスト取得
@app.route("/attendance/code/holiday_division", methods=["GET", "POST"])
def attendance_code_holiday_division():

    request_json = routing_util.get_request_param(request)
    code_list = code_master.get_holiday_division(g_db_conn, request_json)
    send_content = {
        "code_list": code_list,
        "message": "OK"
    }

    return routing_util.create_result_json(send_content)


# 休暇事由リスト取得
@app.route("/attendance/code/holiday_reason", methods=["GET", "POST"])
def attendance_code_holiday_reason():

    request_json = routing_util.get_request_param(request)
    code_list = code_master.get_holiday_reason(g_db_conn, request_json)
    send_content = {
        "code_list": code_list,
        "message": "OK"
    }

    return routing_util.create_result_json(send_content)


# 文字列結合
@app.route("/attendance/concat", methods=["GET", "POST"])
def attendance_concat():

    request_json = routing_util.get_request_param(request)

    if request_json["list"] and request_json["list"] != "なし":
        send_content = {
            "list": request_json["list"] + ", " + request_json["value"]
        }
    else:
        send_content = {
            "list": request_json["value"]
        }

    return routing_util.create_result_json(send_content)


# 勤怠実績明細
@app.route("/attendance/confilm/details", methods=["GET", "POST"])
def attendance_details():

    request_json = routing_util.get_request_param(request)
    send_content = confirm.work_confirm(g_db_conn, request_json)

    return routing_util.create_result_json(send_content)


# 勤怠実績照会
@app.route("/attendance/confilm/plans_inquiry", methods=["GET", "POST"])
def attendance_plans_inquiry():

    request_json = routing_util.get_request_param(request)
    send_content = confirm.plans_inquiry(g_db_conn, request_json)

    return routing_util.create_result_json(send_content)


# 勤怠予定照会
@app.route("/attendance/confilm/plans_work", methods=["GET", "POST"])
def attendance_plans_work():

    request_json = routing_util.get_request_param(request)
    send_content = confirm.plans_work(g_db_conn, request_json)

    return routing_util.create_result_json(send_content)


# 勤怠実績・見込照会(部門別)
@app.route("/attendance/confilm/results/department", methods=["GET", "POST"])
def attendance_confirm_results_department():

    request_json = routing_util.get_request_param(request)
    import attendance.confirm2 as confirm2
    send_content = confirm2.results_department(g_db_conn, request_json)

    return routing_util.create_result_json(send_content)


# 勤怠実績・見込照会(個人別)
@app.route("/attendance/confilm/results/person", methods=["GET", "POST"])
def attendance_confirm_results_person():

    request_json = routing_util.get_request_param(request)
    import attendance.confirm2 as confirm2
    send_content = confirm2.results_person(g_db_conn, request_json)

    return routing_util.create_result_json(send_content)


# 休暇照会(個人別)
@app.route("/attendance/confilm/holiday/person", methods=["GET", "POST"])
def attendance_confirm_holiday_person():

    request_json = routing_util.get_request_param(request)
    import attendance.confirm2 as confirm2
    send_content = confirm2.holiday_person(g_db_conn, request_json)

    return routing_util.create_result_json(send_content)


