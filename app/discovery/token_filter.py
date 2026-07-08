from app.blockchain.token_metadata import TokenMetadata
from app.discovery.pair_discovery import DiscoveredPair


class TokenAllowlistFilter:
    def __init__(self, allowed_symbols: set[str]):
        self.allowed_symbols = {symbol.upper() for symbol in allowed_symbols}

    def is_allowed_pair(
        self,
        token0: TokenMetadata,
        token1: TokenMetadata,
    ) -> bool:
        return (
            token0.symbol.upper() in self.allowed_symbols
            and token1.symbol.upper() in self.allowed_symbols
        )