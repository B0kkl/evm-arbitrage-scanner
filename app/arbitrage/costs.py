from dataclasses import dataclass


@dataclass
class CostEstimate:
    dex_fee_percent: float
    gas_cost_percent: float
    slippage_percent: float
    total_cost_percent: float


class CostEngine:
    def __init__(
        self,
        dex_fee_percent: float = 0.60,  # two swaps: 0.30% + 0.30%
        gas_cost_percent: float = 0.02,
        slippage_percent: float = 0.05,
    ):
        self.dex_fee_percent = dex_fee_percent
        self.gas_cost_percent = gas_cost_percent
        self.slippage_percent = slippage_percent

    def estimate_total_cost(self) -> CostEstimate:
        total = (
            self.dex_fee_percent
            + self.gas_cost_percent
            + self.slippage_percent
        )

        return CostEstimate(
            dex_fee_percent=self.dex_fee_percent,
            gas_cost_percent=self.gas_cost_percent,
            slippage_percent=self.slippage_percent,
            total_cost_percent=total,
        )