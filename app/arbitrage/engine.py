from app.arbitrage.costs import CostEngine
from app.arbitrage.models import ArbitrageOpportunity
from app.models.price import PriceQuote


class OpportunityEngine:
    def __init__(
        self,
        min_net_percent: float = 0.1,
        cost_engine: CostEngine | None = None,
    ):
        self.min_net_percent = min_net_percent
        self.cost_engine = cost_engine or CostEngine()

    def find_best_opportunity(
        self,
        quotes: list[PriceQuote],
    ) -> ArbitrageOpportunity | None:
        if len(quotes) < 2:
            return None

        buy_quote = min(quotes, key=lambda quote: quote.price)
        sell_quote = max(quotes, key=lambda quote: quote.price)

        spread = sell_quote.price - buy_quote.price
        spread_percent = (spread / buy_quote.price) * 100

        costs = self.cost_engine.estimate_total_cost()
        net_percent = spread_percent - costs.total_cost_percent

        profitable = net_percent >= self.min_net_percent

        return ArbitrageOpportunity(
            pair=buy_quote.pair,
            chain=buy_quote.chain,
            buy_dex=buy_quote.dex,
            sell_dex=sell_quote.dex,
            buy_price=buy_quote.price,
            sell_price=sell_quote.price,
            spread=spread,
            spread_percent=spread_percent,
            total_cost_percent=costs.total_cost_percent,
            net_percent=net_percent,
            profitable=profitable,
        )