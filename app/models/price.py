from dataclasses import dataclass


@dataclass
class PriceQuote:
    dex: str
    chain: str
    pair: str

    base_symbol: str
    quote_symbol: str

    price: float
    inverse_price: float

    liquidity_base: float
    liquidity_quote: float

    base_reserve: float
    quote_reserve: float

    pair_address: str