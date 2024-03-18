from threading import Thread
from collections import deque
from account import *
from Block import *
from BlockChain import *
from socket import *
import json
import time
import random

#接收消息线程
class listenThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.socket = socket(AF_INET,SOCK_STREAM)
        self.socket.bind(('',8000))
    def run(self):
        self.socket.listen(2)
        print('(server2) Listen Thread Start')
        while(1):
            socket, Addr = self.socket.accept()
            msg = socket.recv(1024)
            #若消息来自server
            if Addr[0] == '172.17.0.2': 
                print(f"(Server2) Block Infromation")
                add_block_thread = addNewBlock(msg,'Server1')
                add_block_thread.start()
                socket.close()
            #若消息来自client
            else:
                print(f"(Client1) Transacation Information")
                check_transcation_thread = addNewTransacation(msg)
                check_transcation_thread.start()
                socket.close()
        self.socket.close()

#新增交易线程
class addNewTransacation(Thread):
    def __init__(self,msg):
        Thread.__init__(self)
        self.transcation = msg.decode('gbk')

    def run(self):
        global pub_addr_dict
        global global_blockchain
        global global_transcations
        global accounts
        field_time,field_from,field_to,field_value,field_sig = self.transcation.split(',')
        id_out,id_in = pub_addr_dict[field_from],pub_addr_dict[field_to]
        if accounts[id_out].verify_signature(field_to,field_value,field_sig) == True: 
            print(f'Transcation info:{id_out} send {field_value} to {id_in}')
            if checkBalance([field_time,field_from,field_to,field_value,field_sig]) == False:
                print('Balance not enough !')
            else:
                accounts[id_out].withdraw(float(field_value))
                accounts[id_in].deposit(float(field_value))
                global_transcations.append([field_time,field_from,field_to,field_value,field_sig,False])
                #print(f'Transcation info:{id_out} send {field_value} to {id_in}')
            print('Print Transacations:')
            printTransacations(global_transcations)
        #if len(global_transcations) >= 2:
        if len(global_transcations) >= 2 and global_transcations[0][5] == global_transcations[1][5] == False:
            #生成新的区块
            global_transcations[0][5] = global_transcations[1][5] = True
            new_block = generate_block(list((global_transcations[0],global_transcations[1])),global_blockchain)
            if new_block == None:
                #global_transcations[0][5] = global_transcations[1][5] = False
                return
            #广播新区块
            sendBlock(new_block)
            #加入自身的blockchain
            new_block_json = new_block.toJson()
            add_block_thread = addNewBlock(json.dumps(new_block_json).encode('utf-8'),'Server2')
            add_block_thread.start() 

#处理新收到block线程
class addNewBlock(Thread):
    def __init__(self,msg,owner):
        Thread.__init__(self)
        self.new_block_json = json.loads(msg.decode('utf-8'))
        self.new_block = Block(transactions=self.new_block_json['transactions'],
                               prev_hash=self.new_block_json['prev_hash'],
                               height=self.new_block_json['height'],)
        self.new_block.hash = self.new_block_json['hash']
        self.new_block.nonce = self.new_block_json['nonce']
        self.new_block.owner = owner

    def run(self):
        global pub_addr_dict
        global global_blockchain
        global global_transcations
        if verify_new_block(global_blockchain,self.new_block) == True:
            global_blockchain.add_block(self.new_block)
            print('(Server2)新区块添加成功')
            clearTransacations(self.new_block.transactions)
        else:
            print("Block is not valid")
        printBlockChain(global_blockchain)



# 矿工将验证成功的交易列表打包出块
def generate_block(transactions, blockchain):
    new_block = Block(transactions=transactions,
                      prev_hash=blockchain.blocks[len(blockchain.blocks) - 1].hash,
                      height=blockchain.height + 1)
    print("(Server2)生成新的区块...")
    print('(Server2)正在生成交易信息为')
    printTransacations(transactions)
    # 挖矿
    # w = ProofOfWork(new_block)
    # block = w.mine()
    difficulty = 5
    i = 0
    prefix = '0' * difficulty
    height_raw = len(blockchain.blocks)
    while True:
        if len(blockchain.blocks) != height_raw:
            break
        block_info = hashlib.sha256()
        block_info.update(str(new_block.prev_hash).encode('utf-8'))
        # 更新区块中的交易数据
        block_info.update(str(new_block.transactions).encode('utf-8'))
        block_info.update(str(new_block.timestamp).encode('utf-8'))
        block_info.update(str(i).encode("utf-8"))
        digest = block_info.hexdigest()
        if digest.startswith(prefix):
            new_block.nonce = i
            new_block.hash = digest
            break
        i += 1
    if new_block.hash == None:
        print('(Server2)挖矿速度过慢，新区块生成失败')
        return None
    else:
        print('(Server2)新区块生成成功')
        return new_block

#广播block
def sendBlock(block):
    ip = '172.17.0.2'
    port = 8000
    address = (ip,port)
    socket_ = socket(AF_INET,SOCK_STREAM)
    socket_.connect(address)
    block_json = block.toJson()
    socket_.send(json.dumps(block_json).encode('utf-8'))
    socket_.close()

#检验某条交易是否合法
def checkBalance(transaction):
    global accounts
    global pub_addr_dict
    field_time,field_from,field_to,field_value,field_sig = transaction
    id_out,id_in = pub_addr_dict[field_from],pub_addr_dict[field_to]
    if check_action(accounts,id_out,float(field_value)) == True:
        return True
    else:
        return False

#清除交易队列中已经打包的交易
def clearTransacations(transactions):
    global global_transcations
    for transaction in transactions:
        for i in range(len(global_transcations)):
            if transaction[4] == global_transcations[i][4]:
                global_transcations.remove(global_transcations[i])
                break
    print('清除后的Transacations:')
    printTransacations(global_transcations)

#账户信息转为公钥地址字典
def accountToaddr(accounts):
    pubAddrDict = {}
    for key in accounts.keys():
        pubAddrDict[accounts[key].public_address] = accounts[key].id
    return pubAddrDict

#打印交易队列
def printTransacations(transactions):
    global pub_addr_dict
    for transaction in transactions:
        id_out = pub_addr_dict[transaction[1]]
        id_in = pub_addr_dict[transaction[2]]
        val = transaction[3]
        print(f"{id_out} -> {id_in} ({val})")

#打印区块链
def printBlockChain(blockchain):
    for block in blockchain.blocks:
        print(f"{block.hash[5:8]}({block.owner}) ->",end = ' ')
    print('')

if __name__ == '__main__':
    accounts = load_account() #加载账户
    pub_addr_dict = accountToaddr(accounts) #将账户信息转化为地址字典
    global_blockchain = generate_genesis_block() #生成创世区块
    global_transcations = deque() #交易队列
    listen_thread = listenThread()
    listen_thread.start()


            
        
