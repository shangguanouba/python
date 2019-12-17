# coding=utf-8
import socket
import re
import multiprocessing
import time
# import dynamic.mini_frame
import sys


class WSGIServer(object):
    def __init__(self, port, app, static_path):
        # 创建套接字
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 绑定
        self.tcp_server_socket.bind(("", port))
        # 变为监听套接字
        self.tcp_server_socket.listen(128)

        self.application = app
        self.static_path = static_path

    def service_client(self, new_socket):
        """为客户端返回数据"""
        # 接收浏览器发送的请求
        request = new_socket.recv(1024).decode("utf-8")
        # 分割字符串
        request_list = request.splitlines()
        ret = re.match(r"[^/]+(/[^ ]*)", request_list[0])
        file_name = ""
        if ret:
            file_name = ret.group(1)
            if file_name == "/":
                file_name = "/index.html"

        # 如果请求的资源不是已.py结尾，那么久认为是静态资源（html/css/js/png/jpg等）
        if not file_name.endswith(".py"):
            try:
                f = open(self.static_path+file_name, "rb")
            except:
                response = "HTTP/1.1 404 not found\r\n"
                response += "\r\n"
                response += "没有找到服务"
                new_socket.send ( response.encode ( "utf-8" ) )
            else:
                html_content = f.read()
                f.close()
                response = "HTTP/1.1 200 OK\r\n"
                response += "\r\n"
                # 将response hearder 发送浏览器
                new_socket.send ( response.encode ( "utf-8" ) )
                # 将response body 发送浏览器
                new_socket.send ( html_content )
        else:
            # 如果是以.py结尾，那么就认为是动态资源的请求
            env = dict()
            env["PATH_INFO"] = file_name
            body = self.application(env, self.set_response_header)
            header = "HTTP/1.1 %s\r\n" % self.status
            for temp in self.headers:
                header += "%s:%s\r\n" % (temp[0], temp[1])
            header += "\r\n"
            response = header + body
            new_socket.send(response.encode("utf-8"))
        # 关闭套接字
        new_socket.close()

    def set_response_header(self, status, headers):
        self.status = status
        self.headers = [("server", "Apache")]
        self.headers += headers

    def run_forerver(self):
        """完成整体控制"""

        while True:
            # 等待接收client请求
            new_socket, client_addr = self.tcp_server_socket.accept()
            # 为客户端服务
            p = multiprocessing.Process(target=self.service_client, args=(new_socket,))
            p.start()

            new_socket.close()
        # 关闭套接字
        self.tcp_server_socket.close()


def main():
    """整体控制，创建web，然后调用run_forerver运行方法"""
    if len(sys.argv) == 3:
        try:
            port = int(sys.argv[1])  #7890
            frame_app_name = sys.argv[2]  # mini_frame:application
        except Exception as ret:
            print("端口错误。。。。")
            return
    else:
        return

    # mini_frame:application
    ret = re.match(r"([^:]+):(.*)", frame_app_name)
    if ret:
        frame_name = ret.group(1)  # mini_frame
        app_name = ret.group(2)  # application
    else:
        return

    with open("./web_server.conf") as f:
        conf_info = eval(f.read())

    # 此时conf_info是一个字典里面的数据为：
    # {
    #     "static_path":"./static",
    #     "dynamic_path":"./dynamic"
    # }

    sys.path.append(conf_info['dynamic_path'])

    frame = __import__(frame_name)  # 返回值标记这个导入的模块
    app = getattr(frame, app_name)  # 此时app指向 dynamic/mini_frame模块中的application函数

    wsgis = WSGIServer()
    wsgis.run_forerver()


if __name__ == '__main__':
    main()