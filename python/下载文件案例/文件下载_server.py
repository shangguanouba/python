import socket


def sendfile_2_client(new_client_socket, client_addr):
    filename = new_client_socket.recv ( 1024 ).decode ( "utf-8" )
    print ( "客户端%s需要下载的文件是:%s" % (str ( client_addr ), filename) )
    # 打开文件读取数据
    file_content = None
    try:
        f = open(filename, "rb")
        file_content = f.read()
        f.close()
    except Exception as ret:
        print("没有要下载的文件（%s）" % filename)
    if file_content:
        new_client_socket.send ( file_content)

def main():
    # 1.创建套接字
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 2.绑定本地信息 bind
    tcp_socket.bind("", 7890)
    # 3.默认套接字变为被动接收 listen
    tcp_socket.listen(128)
    while True:
        # 4.等待客户端连接 accept
        new_client_socket, client_addr = tcp_socket.accept()
        # 5.调用发送文件函数
        sendfile_2_client(new_client_socket, client_addr)
        # 7.关闭套接字
        new_client_socket.close()
    tcp_socket.close()
if __name__ == '__main__':
    main()