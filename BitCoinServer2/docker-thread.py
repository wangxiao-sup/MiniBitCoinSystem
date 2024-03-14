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
        self.socket.connect((ip,port))
    def run(self):
        val,bin_list = self.func
        send_msg = f'number:{val},bin_list:{bin_list}'
        self.socket.send(send_msg.encode("gbk"))
        self.socket.close()

def getBinary(val):
    val_raw = val
    binary_list = deque()
    while val > 0:
        binary_list.appendleft(val % 2)
        val = int(val / 2)
    print("...Server2 produce number:",val_raw," and calculate its binary number is:",binary_list,"At ",time.ctime())
    return val_raw,binary_list

class listenThread(Thread):
    def __init__(self,address):
        Thread.__init__(self)
        self.socket = socket(AF_INET,SOCK_STREAM)
        self.listen_count = 0
        self.socket.bind(('',8000))
    def run(self):
        while self.listen_count < 10:
            self.socket.listen(2)
            socket, Addr = self.socket.accept()
            from_msg = socket.recv(1024)
            if Addr[0] == '172.17.0.2':
                print(f"---Server2 get message from Server1:{from_msg.decode('gbk')}")
                self.listen_count += 1
                socket.close()
            else:
                print(f"+++Server2 get message from Client1:{from_msg.decode('gbk')}")
                socket.close()
        self.socket.close()

if __name__ == '__main__':
    time.sleep(1)
    address = ('172.17.0.2',8000)
    listen_thread = listenThread(address)
    listen_thread.start()
    T1,T2 = time.time(),time.time()
    while (T2-T1 <= 60):
        if listen_thread.is_alive() == False:
            break
        time.sleep(1)
        random_num = int(random.random()*100)
        if random_num <= 50 and random_num >= 30:
            send_thread = sendThread(address,getBinary(random_num))
            send_thread.start()
            send_thread.join()
        T2 = time.time()
    print('Server2 end and T2-T1 = '+str(T2-T1))
    
        