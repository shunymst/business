#!/usr/bin/env python
# -*- coding: utf-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
from email.header import Header

SMTP_TIMEOUT = 5


def sample():
    send_mail(
        "smtp.gmail.com",
        587,
        "miyamoto.test.test@gmail.com",
        "dpdpdptest",
        "dmy@tis.co.jp",
        "miyamoto.atsushi@tis.co.jp",
        "テスト件名",
        "テスト本文"
    )

    send_mail(
        "smtp.gmail.com",
        465,
        "miyamoto.test.test@gmail.com",
        "dpdpdptest",
        "dmy@tis.co.jp",
        "miyamoto.atsushi@tis.co.jp",
        "テスト件名SSL",
        "テスト本文SSL",
        is_ssl=True
    )


def send_mail(mail_server, mail_server_port, login_user, login_pass,
              from_address, to_address, subject, text, charset="iso-2022-jp", is_ssl=False):

    send_account = from_address

    message = create_message(
        send_account,
        to_address,
        subject,
        text,
        charset=charset
    )
    if is_ssl:
        smtp = get_smtp_ssl(mail_server, mail_server_port, login_user, login_pass)
    else:
        smtp = get_smtp(mail_server, mail_server_port, login_user, login_pass)

    smtp.send_message(message)
    smtp.quit()


def create_message(from_address, to_address, subject, text, charset="iso-2022-jp"):
    message = MIMEText(
        text.encode(charset),
        "plain",
        charset,
    )
    message["Subject"] = Header(subject, charset)
    message["From"] = from_address
    message["To"] = to_address
    message["Date"] = formatdate(localtime=True)
    return message


def get_smtp(mail_server, mail_server_port, login_user, login_pass):
    smtp = smtplib.SMTP(mail_server, mail_server_port, timeout=SMTP_TIMEOUT)
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(login_user, login_pass)
    return smtp


def get_smtp_ssl(mail_server, mail_server_port, login_user, login_pass):
    smtp = smtplib.SMTP_SSL(mail_server, mail_server_port, timeout=SMTP_TIMEOUT)
    smtp.login(login_user, login_pass)
    return smtp


if __name__ == "__main__":
    sample()
