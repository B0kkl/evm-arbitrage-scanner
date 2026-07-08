from dataclasses import dataclass


@dataclass
class ArbitrageOpportunity:
    pair: str
    chain: str

    buy_dex: str
    sell_dex: str

    buy_price: float
    sell_price: float

    spread: float
    spread_percent: float

    total_cost_percent: float
    net_percent: float

    profitable: bool