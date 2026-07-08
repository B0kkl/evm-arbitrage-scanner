from web3 import Web3


class BlockchainClient:
    def __init__(self, rpc_url: str):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))

    def is_connected(self) -> bool:
        return self.web3.is_connected()

    def latest_block_number(self) -> int:
        return self.web3.eth.block_number

    def chain_id(self) -> int:
        return self.web3.eth.chain_id