from web3 import Web3
from app.dex.interfaces import DexAdapter
from app.dex.abis import FACTORY_ABI, PAIR_ABI
from app.models.price import PriceQuote
from app.pricing.engine import PricingEngine


ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


class UniswapV2Dex(DexAdapter):
    def __init__(self, web3: Web3, name: str, chain: str, factory_address: str):
        self.web3 = web3
        self.name = name
        self.chain = chain
        self.factory_address = Web3.to_checksum_address(factory_address)

        self.factory = self.web3.eth.contract(
            address=self.factory_address,
            abi=FACTORY_ABI,
        )

    def get_pair_address(self, token_a: str, token_b: str) -> str:
        token_a = Web3.to_checksum_address(token_a)
        token_b = Web3.to_checksum_address(token_b)

        return self.factory.functions.getPair(token_a, token_b).call()

    def get_pair_reserves(self, pair_address: str) -> dict:
        if pair_address == ZERO_ADDRESS:
            raise ValueError(f"{self.name}: Pair does not exist.")

        pair = self.web3.eth.contract(
            address=Web3.to_checksum_address(pair_address),
            abi=PAIR_ABI,
        )

        token0 = pair.functions.token0().call()
        token1 = pair.functions.token1().call()
        reserve0, reserve1, timestamp = pair.functions.getReserves().call()

        return {
            "pair_address": pair_address,
            "token0": token0,
            "token1": token1,
            "reserve0": reserve0,
            "reserve1": reserve1,
            "timestamp": timestamp,
        }

    def get_price(self, base_token: dict, quote_token: dict) -> PriceQuote:
        pair_address = self.get_pair_address(
            base_token["address"],
            quote_token["address"],
        )

        reserves = self.get_pair_reserves(pair_address)

        price_data = PricingEngine.calculate_price(
            reserves=reserves,
            base_token=base_token,
            quote_token=quote_token,
        )

        pair_name = f"{base_token['symbol']}/{quote_token['symbol']}"

        return PriceQuote(
            dex=self.name,
            chain=self.chain,
            pair=pair_name,
            base_symbol=base_token["symbol"],
            quote_symbol=quote_token["symbol"],
            price=float(price_data["price"]),
            inverse_price=float(price_data["inverse_price"]),
            liquidity_base=float(price_data["base_reserve"]),
            liquidity_quote=float(price_data["quote_reserve"]),
            base_reserve=float(price_data["base_reserve"]),
            quote_reserve=float(price_data["quote_reserve"]),
            pair_address=pair_address,
        )