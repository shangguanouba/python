import socket

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

udp_socket.sendto(b"你好呀", ("192.168.192.201", 8080))

udp_socket.close()




if __name__ == '__main__':
    main()

