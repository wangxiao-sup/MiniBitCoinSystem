import hashlib
import json
from datetime import datetime
 
 
class Block:
    """
        区块结构
            prev_hash:      父区块哈希值
            transactions:   交易信息
            timestamp:      区块创建时间
            hash:           区块哈希值
            Nonce:          随机数
    """
 
    def __init__(self, transactions, prev_hash, height):
        self.height = height
        self.prev_hash = prev_hash
        # 交易列表
        self.transactions = transactions
        # 获取当前时间
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 
        # 设置Nonce和哈希的初始值为None
        self.nonce = None
        self.hash = None
        self.owner = None
 
    # 类的 __repr__() 方法定义了实例化对象的输出信息
    def __repr__(self):
        return f"区块内容:{self.transactions}\n区块哈希值:{self.hash}"

    def toJson(self):
        return {
            "height": self.height,
            "prev_hash": self.prev_hash,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "hash": self.hash,
            "nonce": self.nonce
        }
    
 
 
class ProofOfWork:
    """
        工作量证明
            block:          区块
            difficulty:     难度值
    """
 
    def __init__(self, block, difficult=5):
        self.block = block
 
        # 定义工作量难度，默认为5，表示有效的哈希值以5个“0”开头
        self.difficulty = difficult
 
    def mine(self):
        """
            挖矿函数
        """
        i = 0
        prefix = '0' * self.difficulty

        while True:
            block_info = hashlib.sha256()
            block_info.update(str(self.block.prev_hash).encode('utf-8'))
            # 更新区块中的交易数据
            block_info.update(str(self.block.transactions).encode('utf-8'))
            block_info.update(str(self.block.timestamp).encode('utf-8'))
            block_info.update(str(i).encode("utf-8"))
            digest = block_info.hexdigest()
            if digest.startswith(prefix):
                self.block.nonce = i
                self.block.hash = digest
                return self.block
            i += 1
 
    def validate(self):
        """
            验证有效性
        """
        block_info = hashlib.sha256()
        block_info.update(str(self.block.prev_hash).encode('utf-8'))
        block_info.update(json.dumps(self.block.transactions).encode('utf-8'))
        block_info.update(str(self.block.timestamp).encode('utf-8'))
        block_info.update(str(self.block.nonce).encode('utf-8'))
        digest = block_info.hexdigest()
        prefix = '0' * self.difficulty
        return digest.startswith(prefix)