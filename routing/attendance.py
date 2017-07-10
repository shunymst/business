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

    # 作業時間・休憩時間取得
    rest_time_list = time_master.get_rest_time(g_db_conn, request_json)

    # 業務外作業時間・中断時間設定
    outside_work_time_list = attendans_util.convert_time_list(request_json["outside_work_time_list"])
    interruption_time_list = attendans_util.convert_time_list(request_json["interruption_time_list"])

    # 作業時間・休憩時間・中断時間計算
    work_time_minute, total_rest_time_minute, total_outside_work_time_minute, total_interruption_time_minute = \
        attendans_util.get_minute_work_rest_time(
            request_json["start_time"],
            request_json["end_time"],
            rest_time_list,
            outside_work_time_list,
            interruption_time_list
        )

    str_work_time = attendans_util.format_hour_minute(work_time_minute)
    str_rest_time = attendans_util.format_hour_minute(total_rest_time_minute)
    str_outside_work_time = attendans_util.format_hour_minute(total_outside_work_time_minute)
    str_interruption_time = attendans_util.format_hour_minute(total_interruption_time_minute)

    # 遅刻判定取得
    work_time = time_master.get_work_time(g_db_conn, request_json)
    delay_flag, early_flag = attendans_util.get_delay_and_early_flag(request_json, work_time)

    send_content = {
        "work_time": str_work_time,
        "rest_time": str_rest_time,
        "outside_work_time": str_outside_work_time,
        "interruption_time": str_interruption_time,
        "delay_flag": delay_flag,
        "early_flag": early_flag,
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


# 勤怠実績取消
@app.route("/attendance/result/delete", methods=["GET", "POST"])
def attendance_result_delete():

    request_json = routing_util.get_request_param(request)
    message = results.delete(g_db_conn, request_json)
    send_content = {
        "message": message
    }

    return routing_util.create_result_json(send_content)


# 文字列結合
@app.route("/attendance/concat", methods=["GET", "POST"])
def attendance_concat():

    request_json = routing_util.get_request_param(request)

    if request_json["list"]:
        send_content = {
            "list": request_json["list"] + ", " + request_json["value"]
        }
    else:
        send_content = {
            "list": request_json["value"]
        }

    return routing_util.create_result_json(send_content)
