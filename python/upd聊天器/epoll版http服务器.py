import socket
import re
import select


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

    # 创建一个epoll对象
    epl = select.epoll()

    # 将监听套接字对应的fd注册到epoll中
    epl.register(server_socket.fileno(), select.EPOLLIN)

    fd_event_dict = dict()
    while True:
        fd_event_list = epl.poll()  # 会默认堵塞，直到操作系统监测到数据到来，通过通知事件的方式告诉程序，才会解堵塞
        # epl.poll() 的返回值是一个列表，列表中存放着元组(套接字对应的描述符，对应的事件)。[(fd, event),(),....]
        for fd, event in fd_event_list:
            # 等待客户端连接
            if fd == server_socket.fileno():
                new_socket, client_addr = server_socket.accept()
                epl.register(new_socket.fileno(), select.EPOLLIN)
                fd_event_dict[new_socket.fileno()] = new_socket
            elif event == select.EPOLLIN:
                # 判断是否有客户端发送数据过来
                recv_date = fd_event_dict[fd].recv(1024).decode("utf-8")
                if recv_date:
                    service_client(fd_event_dict[fd], recv_date)
                else:
                    fd_event_dict[fd].close()
                    epl.unregister(fd)
                    del fd_event_dict[fd]

        # 关闭监听套接字
        server_socket.close()


if __name__ == '__main__':
    main()