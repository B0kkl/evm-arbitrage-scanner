from dataclasses import dataclass

from web3 import Web3

from app.dex.abis import ERC20_ABI


@dataclass
class TokenMetadata:
    address: str
    symbol: str
    name: str
    decimals: int


class TokenMetadataReader:
    def __init__(self, web3: Web3):
        self.web3 = web3
        self.cache: dict[str, TokenMetadata] = {}

    def get_token_metadata(self, token_address: str) -> TokenMetadata:
        checksum_address = Web3.to_checksum_address(token_address)
        cache_key = checksum_address.lower()

        if cache_key in self.cache:
            return self.cache[cache_key]

        token = self.web3.eth.contract(
            address=checksum_address,
            abi=ERC20_ABI,
        )

        try:
            symbol = token.functions.symbol().call()
        except Exception:
            symbol = "UNKNOWN"

        try:
            name = token.functions.name().call()
        except Exception:
            name = "Unknown Token"

        try:
            decimals = token.functions.decimals().call()
        except Exception:
            decimals = 18

        metadata = TokenMetadata(
            address=checksum_address,
            symbol=symbol,
            name=name,
            decimals=decimals,
        )

        self.cache[cache_key] = metadata
        return metadata