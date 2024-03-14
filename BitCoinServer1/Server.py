from threading import Thread
from collections import deque
from account import *
from Block import *
from BlockChain import *
from socket import *
import json
import time
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

#接收消息线程
class listenThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.socket = socket(AF_INET,SOCK_STREAM)
        self.socket.bind(('',8000))
    def run(self):
        self.socket.listen(2)
        while(1):
            socket, Addr = self.socket.accept()
            from_msg = socket.recv(1024)
            sender = 0 # -1代表server，1代表client
            #若消息来自server
            if Addr[0] == '172.17.0.3': 
                print(f"(Server2) Block Infromation")
                sender = -1
                socket.close()
            #若消息来自client
            else:
                print(f"(Client1) Transacation Information")
                sender = 1
                socket.close()
        self.socket.close()

#挖矿线程
class mineThread(Thread):
    def __init__(self):
        Thread.__init__(self)

def accoToaddr(accounts):
    pubAddrDict = {}
    for key in accounts.keys():
        pubAddrDict[accounts[key].public_address] = {accounts[key].id}

if __name__ == '__main__':
    accounts = load_account()
    pub_addr_dict = accoToaddr(accounts)
    blockchain = generate_genesis_block()
    transcations = deque()
    while(1):
        listen_thread = listenThread()
        sender,msg = listen_thread.start()
        if sender == -1:
            new_block = json.loads(msg.decode('utf-8'))
            if verify_new_block(blockchain,new_block) == True:
                blockchain.add_block(new_block)
            else:
                print("Block is not valid")
        elif sender == 1:
            msg = msg.decode('gbk')
            field_time,field_from,field_to,field_value,field_sig = msg.split(',')
            id_out,id_in = pub_addr_dict[field_from],pub_addr_dict[field_to]
            if accounts[id_out].verify_signature(field_to,field_value,field_sig) == True:
                transcations[field_time] = {field_from,field_to,field_value,field_sig}
                #modify_accounts(accounts,id_out,id_in,field_value)
            if len(transcations) == 2:
                generate_block(0,transcations,blockchain)


            
        
