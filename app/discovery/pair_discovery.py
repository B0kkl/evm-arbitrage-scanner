from dataclasses import dataclass

from web3 import Web3

from app.dex.abis import FACTORY_ABI, PAIR_ABI


@dataclass
class DiscoveredPair:
    dex: str
    chain: str
    pair_address: str
    token0: str
    token1: str
    reserve0: int
    reserve1: int


class PairDiscovery:
    def __init__(self, web3: Web3, dex_name: str, chain_name: str, factory_address: str):
        self.web3 = web3
        self.dex_name = dex_name
        self.chain_name = chain_name
        self.factory_address = Web3.to_checksum_address(factory_address)

        self.factory = self.web3.eth.contract(
            address=self.factory_address,
            abi=FACTORY_ABI,
        )

    def get_total_pairs(self) -> int:
        return self.factory.functions.allPairsLength().call()

    def get_pair_address_by_index(self, index: int) -> str:
        return self.factory.functions.allPairs(index).call()

    def get_pair_details(self, pair_address: str) -> DiscoveredPair:
        pair = self.web3.eth.contract(
            address=Web3.to_checksum_address(pair_address),
            abi=PAIR_ABI,
        )

        token0 = pair.functions.token0().call()
        token1 = pair.functions.token1().call()
        reserve0, reserve1, _ = pair.functions.getReserves().call()

        return DiscoveredPair(
            dex=self.dex_name,
            chain=self.chain_name,
            pair_address=pair_address,
            token0=token0,
            token1=token1,
            reserve0=reserve0,
            reserve1=reserve1,
        )

    def discover_pairs(
        self,
        start_index: int = 0,
        limit: int = 50,
        skip_empty: bool = True,
    ) -> list[DiscoveredPair]:
        total_pairs = self.get_total_pairs()
        end_index = min(start_index + limit, total_pairs)

        discovered_pairs = []

        for index in range(start_index, end_index):
            try:
                pair_address = self.get_pair_address_by_index(index)
                pair_details = self.get_pair_details(pair_address)

                if skip_empty and (
                    pair_details.reserve0 == 0 or pair_details.reserve1 == 0
                ):
                    continue

                discovered_pairs.append(pair_details)

            except Exception as error:
                print(f"[WARNING] Failed to read pair index {index}: {error}")

        return discovered_pairs