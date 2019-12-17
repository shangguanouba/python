# coding=utf-8
import time


def index():
    with open("./templates/index.html") as f:
        return f.read()


def center():
    with open("../templates/center.html") as f:
        return f.read()


def application(env, start_response):
    start_response("200 OK", [("Conten-Type", "text/html;charset=utf-8")])
    file_name = env["PATH_INFO"]
    if file_name == "/index.py":
        return index()
    elif file_name == "/login.py":
        return login()
    else:
        return "hello world!!!!!!!!!!我爱你中国！！！"