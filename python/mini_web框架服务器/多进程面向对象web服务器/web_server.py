import socket
import re
import multiprocessing


class WSGIServer(object):
    def __init__(self):
        # 创建套接字
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 绑定
        self.tcp_server_socket.bind(("", 7890))
        # 变为监听套接字
        self.tcp_server_socket.listen(128)

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


        # 返回http格式数据给浏览器 header body
        try:
            f = open("./html"+file_name, "rb")
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

        # 关闭套接字
        new_socket.close()

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
    wsgis = WSGIServer()
    wsgis.run_forerver()


if __name__ == '__main__':
    main()