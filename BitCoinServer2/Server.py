from threading import Thread
from collections import deque
import time
from socket import *
import random

class sendThread(Thread):
    def __init__(self,address,func):
        Thread.__init__(self)
        self.func = func
        ip,port = address
        self.socket = socket(AF_INET,SOCK_STREAM)
        self.socket.connect(address)
    def run(self):
        val,bin_list = self.func
        send_msg = f'number:{val},bin_list:{bin_list}'
        self.socket.send(send_msg.encode("gbk"))
        self.socket.close()

class listenThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.socket = socket(AF_INET,SOCK_STREAM)
        self.socket.bind(('',8000))
    def run(self):
        self.socket.listen(2)
        socket, Addr = self.socket.accept()
        from_msg = socket.recv(1024)
        #若消息来自server
        if Addr[0] == '172.17.0.2': 
            print(f"---Server2 get message from Server1:{from_msg.decode('gbk')}")
            self.listen_count += 1
            socket.close()
        #若消息来自client
        else:
            print(f"+++Server2 get message from Client1:{from_msg.decode('gbk')}")
            socket.close()
        self.socket.close()

if __name__ == '__main__':
    while(1):
        listen_thread = listenThread()
        listen_thread.start()
        listen_thread.join()