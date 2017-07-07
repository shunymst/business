import copy
import json
import os

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

    status, result = results.check_result(g_db_conn, request_json)

    work_time, remarks = None
    if result:
        work_time = "{}～{}".format(str(result["start_time"]), str(result["end_time"]))
        remarks = result["remarks"]

    send_content = {
        "status": status,
        "work_time": work_time,
        "remarks": remarks,
        "message": "OK"
    }

    return create_result_json(send_content)


# 勤務時間、休憩時間計算
@app.route("/attendance/result/calc_time", methods=["GET", "POST"])
def attendance_result_calc_time():

    request_json = get_request_param(request)

    # 作業時間・休憩時間取得
    work_time_minute, total_rest_time_minute = time_master.get_rest_time(g_db_conn, request_json)
    str_work_time = common_module.format_hour_minute(work_time_minute)
    str_rest_time = common_module.format_hour_minute(total_rest_time_minute)

    # 遅刻判定取得
    work_time = time_master.get_work_time(g_db_conn, request_json)
    delay_flag, early_flag = time_master.get_delay_and_early_flag(request_json, work_time)

    send_content = {
        "work_time": str_work_time,
        "rest_time": str_rest_time,
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


if __name__ == "__main__":

    # INIファイル読込
    g_ini_def = common_module.read_ini("conf/environment.ini")["DEFAULT"]

    g_db_conn = db_connection.DBConn(g_ini_def["DB_CONNECTION_STR"])

    app.run(host="0.0.0.0", port=51080)
