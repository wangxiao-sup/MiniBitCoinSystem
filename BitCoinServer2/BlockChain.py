from Block import *
 
 
class BlockChain:
    """
        区块链结构体
            blocks:        包含的区块列表
    """
 
    def __init__(self):
        self.blocks = []
        self.height = 0
 
    def add_block(self, block):
        """
            添加区块
        """
        self.blocks.append(block)
 
    def print_list(self):
        print(f"区块链包含个数为：{len(self.blocks)}")
        for block in self.blocks:
            height = 0
            print(f"区块链高度为：{height}")
            print(f"父区块为：{block.prev_hash}")
            print(f"区块内容为：{block.transactions}")
            print(f"区块哈希值为：{block.hash}")
            height += 1
            print()
 
# user生成创世区块（新建区块链），并添加到区块链中
def generate_genesis_block():
    blockchain = BlockChain()
    genesis_block = Block(transactions=[], prev_hash="",height=0)
    #w = ProofOfWork(new_block)
    #genesis_block = w.mine()
    genesis_block.hash = 'AABBCCDD'
    blockchain.add_block(genesis_block)
    # 返回创世区块
    return blockchain

def verify_new_block(blockchain,new_block):
    #验证previous_hash
    if blockchain.blocks[-1].hash != new_block.prev_hash:
        print("(Server2) Previous hash not valid")
        return False
    #验证nonce
    pow = ProofOfWork(new_block)
    if pow.validate == False:
        print("(Server2) Nonce not valid")
        return False
    #验证transactions
    pass
    return True
 
# 矿工将验证成功的交易列表打包出块
def generate_block(transactions, blockchain):
    new_block = Block(transactions=transactions,
                      prev_hash=blockchain.blocks[len(blockchain.blocks) - 1].hash,
                      height=blockchain.height + 1)
    print("(Server2)生成新的区块...")
    # 挖矿
    w = ProofOfWork(new_block)
    block = w.mine()
    print('(Server2)新区块生成成功')
    return block