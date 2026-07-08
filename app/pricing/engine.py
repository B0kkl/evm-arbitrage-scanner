from decimal import Decimal, getcontext

getcontext().prec = 50


class PricingEngine:
    @staticmethod
    def normalize_reserve(raw_reserve: int, decimals: int) -> Decimal:
        return Decimal(raw_reserve) / (Decimal(10) ** decimals)

    @staticmethod
    def calculate_price(
        reserves: dict,
        base_token: dict,
        quote_token: dict,
    ) -> dict:
        token0 = reserves["token0"].lower()
        token1 = reserves["token1"].lower()

        base_address = base_token["address"].lower()
        quote_address = quote_token["address"].lower()

        reserve0_raw = reserves["reserve0"]
        reserve1_raw = reserves["reserve1"]

        if token0 == base_address and token1 == quote_address:
            base_reserve = PricingEngine.normalize_reserve(
                reserve0_raw, base_token["decimals"]
            )
            quote_reserve = PricingEngine.normalize_reserve(
                reserve1_raw, quote_token["decimals"]
            )

        elif token1 == base_address and token0 == quote_address:
            base_reserve = PricingEngine.normalize_reserve(
                reserve1_raw, base_token["decimals"]
            )
            quote_reserve = PricingEngine.normalize_reserve(
                reserve0_raw, quote_token["decimals"]
            )

        else:
            raise ValueError("Tokens do not match this pool.")

        price = quote_reserve / base_reserve
        inverse_price = base_reserve / quote_reserve

        return {
            "base_symbol": base_token["symbol"],
            "quote_symbol": quote_token["symbol"],
            "base_reserve": base_reserve,
            "quote_reserve": quote_reserve,
            "price": price,
            "inverse_price": inverse_price,
        }