#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util.routing_util import get_request_param, create_result_json
from flask import request
import json
import os
import copy
from routing import app


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
