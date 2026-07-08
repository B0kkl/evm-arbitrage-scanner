from app.blockchain.token_metadata import TokenMetadataReader
from app.discovery.liquidity_filter import LiquidityFilter
from app.discovery.pair_discovery import PairDiscovery
from app.discovery.token_filter import TokenAllowlistFilter


class ContinuousBatchScanner:
    def __init__(
        self,
        web3,
        chain_name: str,
        dex_configs: list[dict],
        batch_size: int = 100,
    ):
        self.web3 = web3
        self.chain_name = chain_name
        self.dex_configs = dex_configs
        self.batch_size = batch_size

        self.positions = {
            dex["name"]: 0
            for dex in dex_configs
            if dex.get("enabled", True)
        }

        self.metadata_reader = TokenMetadataReader(web3)

        self.liquidity_filter = LiquidityFilter(
            min_reserve0=1_000_000,
            min_reserve1=1_000_000,
        )

        self.token_filter = TokenAllowlistFilter(
            allowed_symbols={
                "USDC",
                "USDT",
                "USDT0",
                "DAI",
                "WETH",
                "WPOL",
                "WMATIC",
                "QUICK",
                "UNI",
            }
        )

    def scan_next_batch(self) -> list[dict]:
        filtered_pairs_with_metadata = []

        for dex_config in self.dex_configs:
            if not dex_config.get("enabled", True):
                continue

            if dex_config["type"] != "uniswap_v2":
                continue

            dex_name = dex_config["name"]
            start_index = self.positions.get(dex_name, 0)

            discovery = PairDiscovery(
                web3=self.web3,
                dex_name=dex_name,
                chain_name=self.chain_name,
                factory_address=dex_config["factory_address"],
            )

            total_pairs = discovery.get_total_pairs()

            discovered_pairs = discovery.discover_pairs(
                start_index=start_index,
                limit=self.batch_size,
                skip_empty=True,
            )

            liquid_pairs = self.liquidity_filter.filter_pairs(discovered_pairs)

            for pair in liquid_pairs:
                token0 = self.metadata_reader.get_token_metadata(pair.token0)
                token1 = self.metadata_reader.get_token_metadata(pair.token1)

                if not self.token_filter.is_allowed_pair(token0, token1):
                    continue

                filtered_pairs_with_metadata.append(
                    {
                        "dex": pair.dex,
                        "chain": pair.chain,
                        "pair_address": pair.pair_address,
                        "token0": token0,
                        "token1": token1,
                        "reserve0": pair.reserve0,
                        "reserve1": pair.reserve1,
                    }
                )

            next_index = start_index + self.batch_size

            if next_index >= total_pairs:
                next_index = 0

            self.positions[dex_name] = next_index

        return filtered_pairs_with_metadata