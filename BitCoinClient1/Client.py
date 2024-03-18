from account import *
import random
import threading
import socket
import time

def send_message(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        i = 0
        try:
            s.connect((ip, port))
            s.sendall(message.encode('gbk'))
            i += 1
        except:
            if i >= 3:
                print(f"Can't connect to {ip}")
        s.close()


if __name__ == '__main__':
    ip1 = "172.17.0.2"
    ip2 = "172.17.0.3"
    port = 8000

    while(1):
        time.sleep(5)
        #从csv加载账户信息
        accounts = load_account()
        id_list = list(accounts.keys())
        #随机生成一个交易
        id_out,id_in = random.sample(id_list,2)
        # id_out = random.choice(id_list) #支出账户id
        # id_in = random.choice(id_list) #收入账户id
        value_out = random.randint(0,accounts[id_out].balance) #支出金额，已限制不大于余额
        #生成交易信息
        field_timestamp = time.time()
        field_from = accounts[id_out].public_address
        field_to = accounts[id_in].public_address
        field_value = value_out
        field_sig = accounts[id_out].generate_signature(field_to,field_value)
        transaction = f"{field_timestamp},{field_from},{field_to},{field_value},{field_sig}"
        #广播交易信息到server1和server2节点
        print(f'{id_out} send {value_out} to {id_in}')
        thread1 = threading.Thread(target=send_message, args=(ip1, port, transaction))
        thread2 = threading.Thread(target=send_message, args=(ip2, port, transaction))
        try_num1 = 0
        try_num2 = 0
        try:
            thread1.start()
        except:
            try_num1 += 1
            if try_num1 >= 3:
                print("Can't connect to Server1")
        try:
            thread2.start()
        except:
            try_num2 += 1
            if try_num2 >= 3:
                print("Can't connect to Server2")
        thread1.join()
        thread2.join()

