from app.config.dexes import DEXES
from app.dex.adapters.uniswap_v2 import UniswapV2Dex


class DexRegistry:
    def __init__(self, web3, chain_key: str, chain_name: str):
        self.web3 = web3
        self.chain_key = chain_key
        self.chain_name = chain_name
        self.dexes = self._load_dexes()

    def _load_dexes(self):
        dex_configs = DEXES.get(self.chain_key, [])
        dexes = []

        for dex_config in dex_configs:
            if not dex_config.get("enabled", True):
                continue

            dex_type = dex_config["type"]

            if dex_type == "uniswap_v2":
                dex = UniswapV2Dex(
                    web3=self.web3,
                    name=dex_config["name"],
                    chain=self.chain_name,
                    factory_address=dex_config["factory_address"],
                )
                dexes.append(dex)
            else:
                raise ValueError(f"Unsupported DEX type: {dex_type}")

        return dexes

    def get_prices(self, base_token: dict, quote_token: dict):
        quotes = []

        for dex in self.dexes:
            try:
                quote = dex.get_price(
                    base_token=base_token,
                    quote_token=quote_token,
                )
                quotes.append(quote)
            except Exception as error:
                print(f"[WARNING] {dex.name} failed: {error}")

        return quotes