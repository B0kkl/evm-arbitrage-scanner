class SimulationEngine:
    def __init__(self, dex_fee_percent: float = 0.30):
        self.dex_fee = dex_fee_percent / 100

    def simulate_uniswap_v2_swap(
        self,
        amount_in: float,
        reserve_in: float,
        reserve_out: float,
    ) -> float:
        amount_in_after_fee = amount_in * (1 - self.dex_fee)

        return (
            amount_in_after_fee * reserve_out
        ) / (
            reserve_in + amount_in_after_fee
        )

    def simulate_arbitrage(
        self,
        trade_size_quote: float,
        buy_quote,
        sell_quote,
    ) -> dict:
        # Buy base token using quote token on the buy DEX.
        # reserve_in  = quote reserve
        # reserve_out = base reserve
        base_received = self.simulate_uniswap_v2_swap(
            amount_in=trade_size_quote,
            reserve_in=buy_quote.quote_reserve,
            reserve_out=buy_quote.base_reserve,
        )

        # Sell base token back into quote token on the sell DEX.
        # reserve_in  = base reserve
        # reserve_out = quote reserve
        quote_received = self.simulate_uniswap_v2_swap(
            amount_in=base_received,
            reserve_in=sell_quote.base_reserve,
            reserve_out=sell_quote.quote_reserve,
        )

        gross_profit = quote_received - trade_size_quote
        gross_profit_percent = (gross_profit / trade_size_quote) * 100

        return {
            "trade_size_quote": trade_size_quote,
            "base_received": base_received,
            "quote_received": quote_received,
            "gross_profit": gross_profit,
            "gross_profit_percent": gross_profit_percent,
        }

    def simulate_many_trade_sizes(
        self,
        trade_sizes_quote: list[float],
        buy_quote,
        sell_quote,
    ) -> list[dict]:
        results = []

        for trade_size in trade_sizes_quote:
            result = self.simulate_arbitrage(
                trade_size_quote=trade_size,
                buy_quote=buy_quote,
                sell_quote=sell_quote,
            )
            results.append(result)

        return results

    def find_best_trade_size(
        self,
        trade_sizes_quote: list[float],
        buy_quote,
        sell_quote,
    ) -> dict | None:
        results = self.simulate_many_trade_sizes(
            trade_sizes_quote=trade_sizes_quote,
            buy_quote=buy_quote,
            sell_quote=sell_quote,
        )

        if not results:
            return None

        return max(results, key=lambda item: item["gross_profit"])