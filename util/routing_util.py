#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from flask import jsonify
from util.common_module import print_stdout


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
