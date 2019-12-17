import socket


def main():
    # 1.创建套接字
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 2.获取服务器ip和port
    server_ip = input("请输入服务器ip：")
    server_port = int(input("请输入服务器port："))
    # 3.连接服务器
    tcp_socket.connect((server_ip, server_port))
    # 4.获取下载文件名
    download_filename = input("请输入需要下载的文件名：")
    # 5.将文件名发送服务器
    tcp_socket.send(download_filename.encode("utf-8"))
    # 6.接收文件中的数据
    recv_date = tcp_socket.recv(1024)  # 1024=1k  1024*1024=1M
    # 7.保存收到到数据到一个文件夹
    if recv_date:
        with open("[新]"+download_filename, "wb") as f:
            f.write(recv_date)
    # 8.关闭套接字
    tcp_socket.close()


if __name__ == '__main__':
    main()
