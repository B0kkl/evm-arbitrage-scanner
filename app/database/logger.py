import csv
from datetime import datetime, timezone
from pathlib import Path


class OpportunityLogger:
    def __init__(self, file_path: str = "data/opportunities.csv"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.file_path.exists():
            with self.file_path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "timestamp",
                    "pair",
                    "buy_dex",
                    "sell_dex",
                    "raw_spread_percent",
                    "best_trade_size",
                    "profit",
                    "profit_percent",
                    "decision",
                ])

    def log(self, opportunity, best_trade: dict, decision: str):
        with self.file_path.open("a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now(timezone.utc).isoformat(),
                opportunity.pair,
                opportunity.buy_dex,
                opportunity.sell_dex,
                opportunity.spread_percent,
                best_trade["trade_size_quote"],
                best_trade["gross_profit"],
                best_trade["gross_profit_percent"],
                decision.replace("[bold green]", "")
                        .replace("[bold red]", "")
                        .replace("[/bold green]", "")
                        .replace("[/bold red]", ""),
            ])