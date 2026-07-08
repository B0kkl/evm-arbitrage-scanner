from app.discovery.pair_discovery import DiscoveredPair


class LiquidityFilter:
    def __init__(
        self,
        min_reserve0: int = 1_000_000,
        min_reserve1: int = 1_000_000,
    ):
        self.min_reserve0 = min_reserve0
        self.min_reserve1 = min_reserve1

    def is_liquid(self, pair: DiscoveredPair) -> bool:
        return (
            pair.reserve0 >= self.min_reserve0
            and pair.reserve1 >= self.min_reserve1
        )

    def filter_pairs(self, pairs: list[DiscoveredPair]) -> list[DiscoveredPair]:
        return [pair for pair in pairs if self.is_liquid(pair)]