#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 共通モジュール
import configparser
import os
import datetime
import re
import json
import base64
import sys

from Crypto.Cipher import AES
from logging import getLogger, handlers, StreamHandler, DEBUG, INFO, WARN, WARNING, ERROR, FATAL, CRITICAL
from collections import OrderedDict
from functools import partial
import math


# INIファイル読込
def read_ini(filepath, encoding='utf8'):

    # %(XXX)をただの文字列として扱うようにinterpolation=Noneを設定
    config = configparser.ConfigParser(interpolation=None)

    if isinstance(filepath, list):

        for i, item in enumerate(filepath):
            # INIファイル読込
            if not os.path.exists(item):
                raise Exception("INIファイルが見つかりません : " + item)
            config.read(item, encoding=encoding)

    else:
        # INIファイル読込
        if not os.path.exists(filepath):
            raise Exception("INIファイルが見つかりません : " + filepath)
        config.read(filepath, encoding=encoding)

    # print("ini" + str(config))
    # for section in config:
    #     section
    #     print ("section:" + section)
    #     for param in config[section]:
    #         print("param:" + param.upper())

    return config


# ログ初期化
def get_logger(filepath, fh_stdo_level="DEBUG", fh_file_level="INFO",
               log_format="%(levelname)s %(module)s.%(funcName)s(%(lineno)d) %(message)s"):
    import logging  # loggingはどこからでも使用可能にしておくのは、あまりよくないらしいのでローカルでimport

    # ログファイルに年月日フォーマットが指定されている場合置換
    ptn = re.compile("{[^}]+}")
    m = ptn.search(filepath, 0)
    if m:
        fmt = filepath[m.start(): m.end()]
        str_this_ym = datetime.date.today().strftime(fmt[1: -1])
        filepath = filepath.replace(fmt, str_this_ym)

    # Logger取得
    logger = getLogger(filepath)
    logger.setLevel(DEBUG)

    if fh_stdo_level.upper() != "NONE":
        # 標準出力ハンドラ
        shandler = StreamHandler()
        shandler.setLevel(get_log_level(fh_stdo_level))
        shandler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(shandler)

    if fh_file_level.upper() != "NONE":
        # # ファイルハンドラ
        # fhandler = FileHandler(filepath, 'a', encoding="utf-8")
        # fhandler.setLevel(get_log_level(fh_file_level))
        # fhandler.setFormatter(logging.Formatter(log_format))
        # logger.addHandler(fhandler)

        # 日時ロテートファイルハンドラ
        lfhandler = handlers.TimedRotatingFileHandler(filepath, when="D", interval=1, backupCount=180, encoding="utf-8")
        lfhandler.setLevel(get_log_level(fh_file_level))
        lfhandler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(lfhandler)

    return logger


# ログレベル取得
def get_log_level(str_level):
    str_level = str_level.upper()
    if str_level == "DEBUG":
        return DEBUG
    elif str_level == "INFO":
        return INFO
    elif str_level == "WARN":
        return WARN
    elif str_level == "WARNING":
        return WARNING
    elif str_level == "ERROR":
        return ERROR
    elif str_level == "FATAL":
        return FATAL
    elif str_level == "CRITICAL":
        return CRITICAL


# json Value取得
def get_jsonvalue(json_dict, key, default_value=None):
    if json_dict is None:
        return None
    if key not in json_dict:
        return default_value
    else:
        return json_dict[key]


# json Value取得
def json_dumps(json_dict, is_format=False):

    if is_format:
        # json文字列を出力
        return json.dumps(json_dict, indent=4, separators=(',', ': '), ensure_ascii=False)
    else:
        # 整形なしで出力(encodeはしない)
        return json.dumps(json_dict, ensure_ascii=False)


# 暗号化定数
CRYPT_BLOCK_SIZE = 16
CRYPT_BASE64_ENCODE = "ASCII"
CRYPT_PAD_CHAR = " "


# AES 暗号化処理
def aes_crypt(secret_key, val, encode="UTF-8"):

    # ブロックサイズ設定
    doc_byte_len = len(val.encode(encode))
    block_cnt = int(doc_byte_len / CRYPT_BLOCK_SIZE)  # 切捨て
    if doc_byte_len % CRYPT_BLOCK_SIZE > 0:
        block_cnt += 1

    # 文字列が16桁の倍数になるように半角スペースで埋める
    pad_doc = val
    while len(pad_doc.encode(encode)) % CRYPT_BLOCK_SIZE != 0:
        pad_doc += CRYPT_PAD_CHAR

    # 暗号化
    crypt_doc = AES.new(secret_key, AES.MODE_ECB).encrypt(pad_doc)
    # print(crypt_doc)

    # 文字列に変換できるようbase64でエンコード
    base64_enc_doc = base64.b64encode(crypt_doc)
    return base64_enc_doc.decode(CRYPT_BASE64_ENCODE)


# AES 複合化処理
def aes_decrypt(secret_key, crypt_doc, encode="UTF-8"):
    # 複合化
    decrypt_doc = AES.new(secret_key, AES.MODE_ECB).decrypt(base64.b64decode(crypt_doc)).decode(encode).strip()

    return decrypt_doc


# base64でエンコードされた文字列をデコードし、OrderedDict形式で返却
def decode_base64_to_odict(str_base64, encode="UTF-8"):

    if str_base64:
        # 「-」を「+」に「_」を「/」に置き換え
        rep_str = str_base64
        rep_str = rep_str.replace("-", "+")
        rep_str = rep_str.replace("_", "/")

        # base64をDECODE
        decode_str = base64.b64decode(rep_str).decode(encode)
        # OrderedDictで返却
        return json_loads_odict(decode_str)
    
    return OrderedDict()


# Json文字列をOrderedDict形式に変換
def json_loads_odict(json_str):
    # OrderedDict形式でLoadsにする
    odict_loads = partial(json.loads, object_pairs_hook=OrderedDict)
    return odict_loads(json_str)


# ライン表示用書式変換処理
def line_format_date(s_timestamp):
    s_date = s_timestamp[0: 10]
    conv_date = datetime.datetime.strptime(s_date, "%Y-%m-%d")
    week_day = ["月", "火", "水", "木", "金", "土", "日"]
    s_time = s_timestamp[-8: -3]

    return "{}/{}({}) {}～".format(
        int(s_timestamp[5:7]),
        int(s_timestamp[8:10]),
        week_day[conv_date.weekday()],
        s_time
    )


# 文字列切り出し
def cut_string(cutstr, length, omission_char="…"):
    if len(cutstr) > length:
        if omission_char:
            return cutstr[0: length - 1] + omission_char
        else:
            return cutstr[0: length]
    else:
        return cutstr


# 指定桁で切り捨て
def custom_floor(number, digit):

    if digit > 0:
        p = math.pow(10, digit)
        return format_number(math.floor(number * p) / p)
    elif digit < 0:
        p = math.pow(10, digit * - 1)
        return format_number(math.floor(number / p) * p)
    elif digit == 0:
        return format_number(math.floor(number))


# 指定桁で切り上げ
def custom_ceil(number, digit):

    if digit > 0:
        p = math.pow(10, digit)
        return format_number(math.ceil(number * p) / p)
    elif digit < 0:
        p = math.pow(10, digit * - 1)
        return format_number(math.ceil(number / p) * p)
    elif digit == 0:
        return format_number(math.ceil(number))


# 数値フォーマット
def format_number(number):
    if number == int(number):
        return int(number)
    else:
        return number


# 時分フォーマット
def format_hour_minute(minute):
    return "{0:02d}".format(int(minute / 60)) + ":" + "{0:02d}".format(int(minute % 60))


# datetime変換
def convert_datetime(str_dt, str_format="%Y/%m/%d %H:%M:%S"):
    return datetime.datetime.strptime(str_dt, str_format)


# time変換
def convert_time(str_dt, str_format="%H:%M:%S"):
    dt = convert_datetime(str_dt, str_format)
    return datetime.time(dt.hour, dt.minute, dt.second, dt.microsecond)


# 標準出力処理(printではSupervisorログに出力されない為)
def print_stdout(text):
    sys.stdout.write(str(text))
    sys.stdout.write("\n")
    sys.stdout.flush()
