import time

from rich.console import Console
from rich.table import Table
from app.database.logger import OpportunityLogger
from app.blockchain.client import BlockchainClient
from app.config.chains import CHAINS
from app.config.dexes import DEXES
from app.discovery.pair_grouping import PairGrouping
from app.scanner.auto_opportunity_scanner import AutoOpportunityScanner
from app.scanner.continuous_scanner import ContinuousBatchScanner
from app.simulation.engine import SimulationEngine

simulator = SimulationEngine(dex_fee_percent=0.30)
console = Console()
logger = OpportunityLogger()

def build_quote_from_item(item: dict, base_token, quote_token):
    from app.models.price import PriceQuote
    from app.pricing.engine import PricingEngine

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

    return PriceQuote(
        dex=item["dex"],
        chain=item["chain"],
        pair=f"{base_token.symbol}/{quote_token.symbol}",
        base_symbol=base_token.symbol,
        quote_symbol=quote_token.symbol,
        price=float(price_data["price"]),
        inverse_price=float(price_data["inverse_price"]),
        liquidity_base=float(price_data["base_reserve"]),
        liquidity_quote=float(price_data["quote_reserve"]),
        base_reserve=float(price_data["base_reserve"]),
        quote_reserve=float(price_data["quote_reserve"]),
        pair_address=item["pair_address"],
    )


def main():
    console.rule("[bold cyan]Continuous Batch Scanner")

    chain_key = "polygon"
    chain = CHAINS[chain_key]

    client = BlockchainClient(chain["rpc_url"])

    if not client.is_connected():
        console.print("[bold red]Failed to connect to blockchain RPC[/bold red]")
        return

    batch_scanner = ContinuousBatchScanner(
        web3=client.web3,
        chain_name=chain["name"],
        dex_configs=DEXES[chain_key],
        batch_size=100,
    )

    opportunity_scanner = AutoOpportunityScanner()
    simulator = SimulationEngine(dex_fee_percent=0.30)

    trade_sizes = [1, 5, 10, 25, 50, 100, 250, 500, 1000]

    while True:
        console.rule("[bold yellow]New Batch")

        filtered_pairs = batch_scanner.scan_next_batch()
        grouped_pairs = PairGrouping.group_pairs(filtered_pairs)
        opportunities = opportunity_scanner.scan_grouped_pairs(grouped_pairs)

        console.print(f"[cyan]Filtered pairs:[/cyan] {len(filtered_pairs)}")
        console.print(f"[cyan]Grouped pairs:[/cyan] {len(grouped_pairs)}")
        console.print(f"[cyan]Opportunities:[/cyan] {len(opportunities)}")
        console.print(f"[cyan]Positions:[/cyan] {batch_scanner.positions}")

        table = Table(title="Continuous Scanner Opportunities")

        table.add_column("Pair", style="cyan")
        table.add_column("Buy From")
        table.add_column("Sell To")
        table.add_column("Raw Spread %", justify="right")
        table.add_column("Best Size", justify="right")
        table.add_column("Profit", justify="right")
        table.add_column("Profit %", justify="right")
        table.add_column("Decision", justify="center")

        for opportunity in opportunities[:20]:
            base_token = opportunity.base_token
            quote_token = opportunity.quote_token

            buy_quote = build_quote_from_item(
                opportunity.buy_item,
                base_token=base_token,
                quote_token=quote_token,
            )

            sell_quote = build_quote_from_item(
                opportunity.sell_item,
                base_token=base_token,
                quote_token=quote_token,
            )

            best_trade = simulator.find_best_trade_size(
                trade_sizes_quote=trade_sizes,
                buy_quote=buy_quote,
                sell_quote=sell_quote,
            )
            logger.log(
                 opportunity=opportunity,
                 best_trade=best_trade,
                decision="TRADE" if best_trade and best_trade["gross_profit"] > 0 else "DO NOT TRADE",
            )
            if best_trade and best_trade["gross_profit"] > 0:
                decision = "[bold green]TRADE[/bold green]"
                style = "green"
            else:
                decision = "[bold red]DO NOT TRADE[/bold red]"
                style = "red"

            table.add_row(
                opportunity.buy_dex,
                opportunity.sell_dex,
                f"{opportunity.spread_percent:.6f}%",
                f"{best_trade['trade_size_quote']:.2f} {buy_quote.quote_symbol}",
                f"[{style}]{best_trade['gross_profit']:.8f} {buy_quote.quote_symbol}[/{style}]",
                f"[{style}]{best_trade['gross_profit_percent']:.6f}%[/{style}]",
                decision,
            )

        console.print(table)

        time.sleep(5)


if __name__ == "__main__":
    main()