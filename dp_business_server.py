import copy
import json
import os
import datetime
import re

from flask import Flask, request, jsonify

from attendance import code_master
from attendance import results
from attendance import time_master
from attendance import users
from util import common_module
from util import db_connection
from util import send_mail
from util.common_module import print_stdout

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)  # セッション情報を暗号化するためのキーを設定
app.config["JSON_AS_ASCII"] = False  # 日本語文字化け対策


@app.route("/file", methods=["GET", "POST"])
def file():
    request_json = get_request_param(request)
    file_name = request_json["file"].strip()

    if not os.path.exists("./file/" + file_name):
        raise Exception("ファイルが存在しません")

    with open("./file/" + file_name, encoding="UTF-8") as file_json:
        send_content = json.load(file_json)

    return create_result_json(send_content)


@app.route("/getKoho", methods=["GET", "POST"])
def get_koho():
    request_json = get_request_param(request)
    kibobi_list = request_json["kibobi_list"]

    if "2017/07/08 13:00:00" in kibobi_list:
        send_content = {"fix_date": "7月8日 13:00"}
    else:
        with open("./file/koho_date.json", encoding="UTF-8") as file_json:
            send_content = json.load(file_json)

    return create_result_json(send_content)


@app.route("/add", methods=["GET", "POST"])
def add():
    request_json = get_request_param(request)
    file_name = request_json["file"].strip()

    copy_json = copy.deepcopy(request_json)
    del copy_json["file"]

    with open("./file/" + file_name, "w", encoding="UTF-8") as file_json:
        json.dump(copy_json, file_json, indent=4, separators=(',', ': '), ensure_ascii=False)

    send_content = {"message": "OK"}

    return create_result_json(send_content)


@app.route("/update", methods=["GET", "POST"])
def update():
    request_json = get_request_param(request)
    file_name = request_json["file"].strip()

    if not os.path.exists("./file/" + file_name):
        raise Exception("ファイルが存在しません")

    with open("./file/" + file_name, encoding="UTF-8") as file_json:
        base_json = json.load(file_json)

    copy_json = copy.deepcopy(request_json)
    del copy_json["file"]

    for key in copy_json:
        base_json[key] = copy_json[key]

    # 書き込みで開くとloadできない
    with open("./file/" + file_name, "w", encoding="UTF-8") as file_json:
        json.dump(base_json, file_json, indent=4, separators=(',', ': '), ensure_ascii=False)

    send_content = {"message": "OK"}

    return create_result_json(send_content)


@app.route("/page_add", methods=["GET", "POST"])
def page_add():
    request_json = get_request_param(request)
    file_name = request_json["file"].strip()

    data_list = request_json["data_list"]

    with open("./file/" + file_name, "w", encoding="UTF-8") as file_json:
        json.dump(data_list, file_json, indent=4, separators=(',', ': '), ensure_ascii=False)

    send_content = {"message": "OK", "page_no": 1, "page_cnt": len(data_list)}

    return create_result_json(send_content)


@app.route("/page_get", methods=["GET", "POST"])
def page_get():
    request_json = get_request_param(request)
    file_name = request_json["file"].strip()

    if not os.path.exists("./file/" + file_name):
        raise Exception("ファイルが存在しません")

    with open("./file/" + file_name, encoding="UTF-8") as file_json:
        page_json = json.load(file_json)

    if not request_json["page_no"]:
        page_no = 0
    else:
        page_no = int(request_json["page_no"])

    if len(page_json["list"]) <= page_no:
        send_content = {"message": "データはありません"}
    else:
        send_content = {
            "message": "OK",
            "total_size": len(page_json["list"]),
            "page_no": page_no + 1,
            "page_data": page_json["list"][page_no]
        }

    return create_result_json(send_content)


@app.route("/update_jizen", methods=["GET", "POST"])
def update_jizen():
    request_json = get_request_param(request)
    file_name = request_json["file"].strip()

    if not os.path.exists("./file/" + file_name):
        raise Exception("ファイルが存在しません")

    with open("./file/" + file_name, encoding="UTF-8") as file_json:
        base_json = json.load(file_json)

    if request_json["edit1"] in base_json:
        base_json[request_json["edit1"]] = request_json["value"]
        # 書き込みで開くとloadできない
        with open("./file/" + file_name, "w", encoding="UTF-8") as file_json:
            json.dump(base_json, file_json, indent=4, separators=(',', ': '), ensure_ascii=False)
    if request_json["edit2"] in base_json:
        base_json[request_json["edit2"]] = request_json["value"]
        # 書き込みで開くとloadできない
        with open("./file/" + file_name, "w", encoding="UTF-8") as file_json:
            json.dump(base_json, file_json, indent=4, separators=(',', ': '), ensure_ascii=False)

    send_content = {"message": "OK"}

    return create_result_json(send_content)


@app.route("/sendMail", methods=["GET", "POST"])
def send_mail():
    request_json = get_request_param(request)

    send_mail.send_mail(
        request_json["mail_server"],
        request_json["mail_server_port"],
        request_json["login_user"],
        request_json["login_pass"],
        request_json["from_address"],
        request_json["to_address"],
        request_json["subject"],
        request_json["text"],
        is_ssl=request_json["is_ssl"]
    )

    send_content = {"message": "OK"}

    return create_result_json(send_content)


@app.route("/dummy", methods=["GET", "POST"])
def dummy():

    send_content = {}

    return create_result_json(send_content)


@app.route("/list", methods=["GET", "POST"])
def list_append():

    request_json = get_request_param(request)

    if request_json["list"]:
        send_content = {
            "list": request_json["list"] + ", " + request_json["value"]
        }
    else:
        send_content = {
            "list": request_json["value"]
        }

    return create_result_json(send_content)


# 勤怠管理用 Start
# ユーザー情報取得
@app.route("/attendance/user/get", methods=["GET", "POST"])
def attendance_users_get():

    request_json = get_request_param(request)

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

    return create_result_json(send_content)


# 実績登録情報確認
@app.route("/attendance/result/check_result", methods=["GET", "POST"])
def attendance_result_check_result():

    request_json = get_request_param(request)

    send_content = results.check_result(g_db_conn, request_json)

    return create_result_json(send_content)

# 勤務時間、休憩時間、中断時間計算
@app.route("/attendance/result/calc_time", methods=["GET", "POST"])
def attendance_result_calc_time():

    request_json = get_request_param(request)

    # 作業時間・休憩時間取得
    rest_time_list = time_master.get_rest_time(g_db_conn, request_json)

    # 業務外作業時間・休憩時間取得
    outside_work_time_list = convert_time_list(request_json["outside_work_time_list"])
    interruption_time_list = convert_time_list(request_json["interruption_time_list"])

    # 作業時間・休憩時間・中断時間計算
    work_time_minute, total_rest_time_minute, total_outside_work_time_minute, total_interruption_time_minute = \
        get_minute_work_rest_time(
            request_json["start_time"],
            request_json["end_time"],
            rest_time_list,
            outside_work_time_list,
            interruption_time_list
        )

    str_work_time = common_module.format_hour_minute(work_time_minute)
    str_rest_time = common_module.format_hour_minute(total_rest_time_minute)
    str_outside_work_time = common_module.format_hour_minute(total_rest_time_minute)
    str_interruption_time = common_module.format_hour_minute(total_rest_time_minute)

    # 遅刻判定取得
    work_time = time_master.get_work_time(g_db_conn, request_json)
    delay_flag, early_flag = get_delay_and_early_flag(request_json, work_time)

    send_content = {
        "work_time": str_work_time,
        "rest_time": str_rest_time,
        "outside_work_time": str_outside_work_time,
        "interruption_time": str_interruption_time,
        "delay_flag": delay_flag,
        "early_flag": early_flag,
        "message": "OK"
    }

    return create_result_json(send_content)


# 勤怠実績登録(勤務)
@app.route("/attendance/result/insert/work", methods=["GET", "POST"])
def attendance_result_insert_work():

    request_json = get_request_param(request)
    results.delete(g_db_conn, request_json)
    message = results.insert_work(g_db_conn, request_json)
    send_content = {
        "message": message
    }

    return create_result_json(send_content)


# 勤怠実績登録(休暇)
@app.route("/attendance/result/insert/holiday", methods=["GET", "POST"])
def attendance_result_insert_holiday():

    request_json = get_request_param(request)
    results.delete(g_db_conn, request_json)
    message = results.insert_holiday(g_db_conn, request_json)
    send_content = {
        "message": message
    }

    return create_result_json(send_content)


# 勤務区分リスト取得
@app.route("/attendance/code/work_division", methods=["GET", "POST"])
def attendance_code_work_division():

    request_json = get_request_param(request)
    code_list = code_master.get_work_division(g_db_conn, request_json)
    send_content = {
        "code_list": code_list,
        "message": "OK"
    }

    return create_result_json(send_content)


# 休暇区分リスト取得
@app.route("/attendance/code/holiday_division", methods=["GET", "POST"])
def attendance_code_holiday_division():

    request_json = get_request_param(request)
    code_list = code_master.get_holiday_division(g_db_conn, request_json)
    send_content = {
        "code_list": code_list,
        "message": "OK"
    }

    return create_result_json(send_content)


# 休暇事由リスト取得
@app.route("/attendance/code/holiday_reason", methods=["GET", "POST"])
def attendance_code_holiday_reason():

    request_json = get_request_param(request)
    code_list = code_master.get_holiday_reason(g_db_conn, request_json)
    send_content = {
        "code_list": code_list,
        "message": "OK"
    }

    return create_result_json(send_content)


# 勤怠実績取消
@app.route("/attendance/result/delete", methods=["GET", "POST"])
def attendance_result_delete():

    request_json = get_request_param(request)
    message = results.delete(g_db_conn, request_json)
    send_content = {
        "message": message
    }

    return create_result_json(send_content)


# 文字列結合
@app.route("/attendance/concat", methods=["GET", "POST"])
def attendance_concat():

    request_json = get_request_param(request)

    if request_json["list"]:
        send_content = {
            "list": request_json["list"] + ", " + request_json["value"]
        }
    else:
        send_content = {
            "list": request_json["value"]
        }

    return create_result_json(send_content)
# 勤怠管理用 End


def get_request_param(req):
    if req.method == "GET":
        result = req.args
    else:
        result = req.json

    print_stdout("---------------START---------------")
    print_stdout("Input:{}".format(
        json.dumps(result, indent=4, separators=(",", ": "), ensure_ascii=False)
    ))
    return result


def create_result_json(send_content):
    print_stdout("Output:{}".format(
        json.dumps(send_content, indent=4, separators=(",", ": "), ensure_ascii=False)
    ))
    return jsonify(send_content)


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
        int(diff_time.total_seconds() / 60) - total_outside_work_time_minute - total_interruption_time_minute

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


def create_time_json(start_time, end_time):
    return {"start_time": start_time, "end_time": end_time}


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
                        "remarks": time_part[time_part.index("(") + 1: len(time_part) - 1]
                    }
                )

    return dict_time_list


if __name__ == "__main__":

    # INIファイル読込
    g_ini_def = common_module.read_ini("conf/environment.ini")["DEFAULT"]

    g_db_conn = db_connection.DBConn(g_ini_def["DB_CONNECTION_STR"])

    app.run(host="0.0.0.0", port=51080)
