import csv
import ecdsa
import hashlib

def generateKeyPair():
    # 生成私钥
    private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    private_key_hex = private_key.to_string().hex()

    # 生成公钥
    public_key = private_key.get_verifying_key()
    public_key_hex = public_key.to_string().hex()

    return private_key_hex, public_key_hex

def generatePublicKeyAddress(public_key_hex):
    # 创建 SHA-256 对象
    sha256 = hashlib.sha256()

    # 更新哈希对象的输入数据
    sha256.update(public_key_hex.encode('utf-8'))
    hash1 = sha256.digest()

    # 对上一步的结果进行RIPEMD160哈希
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(hash1)
    hash2 = ripemd160.digest()

    # 将结果转换为十六进制字符串
    public_key_address = hash2.hex()

    return public_key_address


class Account:
    def __init__(self,id,balance,public_key,private_key,public_address):
        self.id = id
        self.balance = balance
        self.public_key = public_key
        self.private_key = private_key
        self.public_address = public_address

    #收入
    def deposit(self, amount):
        self.balance += amount

    #支出
    def withdraw(self, amount):
        self.balance -= amount

    #对<FROM,TO,VALUE>生成签名
    def generate_signature(self,to_address,value):
        from_address = self.public_address
        transaction_data = f"{from_address},{to_address},{value}"
        private_key = ecdsa.SigningKey.from_string(bytes.fromhex(self.private_key), curve=ecdsa.SECP256k1)
        signature = private_key.sign(transaction_data.encode()).hex()
        return signature

    #验证签名
    def verify_signature(self,to_address,value,signature):
        from_address = self.public_address
        transaction_data = f"{from_address},{to_address},{value}"
        public_key = ecdsa.VerifyingKey.from_string(bytes.fromhex(self.public_key), curve=ecdsa.SECP256k1)
        return public_key.verify(bytes.fromhex(signature), transaction_data.encode())

#从csv加载账户信息，返回字典accounts
def load_account():
    accounts = {}
    with open('./accounts.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == 'id':
                continue
            account = Account(row[0], float(row[1]),row[2],row[3],row[4])
            accounts[row[0]] = account
    return accounts

#检查账户操作是否合法：只查验支出操作
def check_action(accounts,id,amount):
    if accounts[id].balance >= amount:
        return True
    else:
        return False

#修改账户信息，但只在字典accounts中修改
def modify_accounts(accounts,id,amount,action):
    if action == 'deposit':
        accounts[id].deposit(amount)
    elif action == 'withdraw':
        accounts[id].withdraw(amount)
    return accounts

#保存账户信息到csv
def save_accounts(accounts):
    with open('./accounts.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['id','balance'])
        for id, account in accounts.items():
            writer.writerow([account.id, account.balance])



