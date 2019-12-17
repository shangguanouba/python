import socket
import re


def service_client(new_socket, request):
    # request = new_socket.recv(1024).decode("utf-8")
    request_list = request.splitlines()
    file_name = ""
    ret = re.match(r"[^/]+(/[^ ]*)", request_list[0])
    if ret:
        file_name = ret.group(1)
        if file_name == "/":
            file_name = "/index.html"

    try:
        f = open("./html" + file_name, "rb")
    except:
        response = "HTTP/1.1 404 FOUND\r\n"
        response += "\r\n"
        new_socket.send(response.encode("utf-8"))
    else:
        html_content = f.read()
        f.close()

        response_body = html_content
        response_header = "HTTP/1.1 200 OK\r\n"
        response_header += "Content_Length:%d" % len(html_content)  # 长连接
        response_header += "\r\n"
        response = response_header.encode("utf-8") + response_body

        new_socket.send(response)


def main():
    # 创建套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # 绑定
    server_socket.bind(("", 7890))

    # 变为监听套接字
    server_socket.listen(128)
    server_socket.setblocking(False)  # 将套接字变为费堵塞

    client_socket_list = list()
    while True:
        # 等待客户端连接
        try:
            new_socket, client_addr = server_socket.accept()
        except Exception as ret:
            pass
        else:
            new_socket.setblocking(False)
            client_socket_list.append(new_socket)
        # 遍历列表为客户端提供服务
        for client_socket in client_socket_list:
            try:
                recv_date = client_socket.recv(1024).decode("utf-8")
            except Exception as ret:
                pass
            else:
                if recv_date:
                    service_client(client_socket, recv_date)
                else:
                    client_socket.close()
                    client_socket_list.remove(client_socket)

    # 关闭监听套接字
    server_socket.close()


if __name__ == '__main__':
    main()