# coding=utf-8
import time
import re

URL_FUNC_DICT = {
    "/index.py": index,
    "center.py": center
}


def index():
    with open("./templates/index.html") as f:
        content = f.read()
    my_stock_info = "哈哈哈，这是你的本月名额"
    content =re.sub(r"\{%content%\}", my_stock_info, content)
    return content


def center():
    with open("../templates/center.html") as f:
        content = f.read()
    my_stock_info = "这里是从mysql查询出来的数据"
    content = re.sub ( r"\{%content%\}", my_stock_info, content )
    return content


def application(env, start_response):
    start_response("200 OK", [("Conten-Type", "text/html;charset=utf-8")])
    file_name = env["PATH_INFO"]

    """if file_name == "/index.py":
        return index()
    elif file_name == "/center.py":
        return center()
    else:
        return "hello world!!!!!!!!!!我爱你中国！！！"""

    URL_FUNC_DICT[file_name]