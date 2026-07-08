from dataclasses import dataclass

from app.pricing.engine import PricingEngine


@dataclass
class AutoOpportunity:
    pair: str
    base_symbol: str
    quote_symbol: str

    buy_dex: str
    sell_dex: str

    buy_price: float
    sell_price: float
    spread_percent: float

    buy_item: dict
    sell_item: dict
    base_token: object
    quote_token: object


class AutoOpportunityScanner:
    def _find_token_by_symbol(self, item: dict, symbol: str):
        token0 = item["token0"]
        token1 = item["token1"]

        if token0.symbol.upper() == symbol.upper():
            return token0

        if token1.symbol.upper() == symbol.upper():
            return token1

        raise ValueError(f"Token symbol {symbol} not found in pair.")

    def scan_grouped_pairs(self, grouped_pairs: dict) -> list[AutoOpportunity]:
        opportunities = []

        for pair_key, dex_pairs in grouped_pairs.items():
            base_symbol, quote_symbol = pair_key.split("/")

            quotes = []

            for item in dex_pairs:
                base_token = self._find_token_by_symbol(item, base_symbol)
                quote_token = self._find_token_by_symbol(item, quote_symbol)

                reserves = {
                    "token0": item["token0"].address,
                    "token1": item["token1"].address,
                    "reserve0": item["reserve0"],
                    "reserve1": item["reserve1"],
                }

                price_data = PricingEngine.calculate_price(
                    reserves=reserves,
                    base_token={
                        "symbol": base_token.symbol,
                        "address": base_token.address,
                        "decimals": base_token.decimals,
                    },
                    quote_token={
                        "symbol": quote_token.symbol,
                        "address": quote_token.address,
                        "decimals": quote_token.decimals,
                    },
                )

                quotes.append(
                    {
                        "dex": item["dex"],
                        "price": float(price_data["price"]),
                        "item": item,
                        "base_token": base_token,
                        "quote_token": quote_token,
                    }
                )

            if len(quotes) < 2:
                continue

            buy = min(quotes, key=lambda x: x["price"])
            sell = max(quotes, key=lambda x: x["price"])

            spread_percent = ((sell["price"] - buy["price"]) / buy["price"]) * 100

            opportunities.append(
                AutoOpportunity(
                    pair=pair_key,
                    base_symbol=base_symbol,
                    quote_symbol=quote_symbol,
                    buy_dex=buy["dex"],
                    sell_dex=sell["dex"],
                    buy_price=buy["price"],
                    sell_price=sell["price"],
                    spread_percent=spread_percent,
                    buy_item=buy["item"],
                    sell_item=sell["item"],
                    base_token=buy["base_token"],
                    quote_token=buy["quote_token"],
                )
            )

        return sorted(
            opportunities,
            key=lambda opportunity: opportunity.spread_percent,
            reverse=True,
        )