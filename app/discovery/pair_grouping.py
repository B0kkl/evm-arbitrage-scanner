class PairGrouping:
    @staticmethod
    def canonical_pair_key(token0_symbol: str, token1_symbol: str) -> str:
        symbols = sorted([token0_symbol.upper(), token1_symbol.upper()])
        return f"{symbols[0]}/{symbols[1]}"

    @staticmethod
    def group_pairs(pairs_with_metadata: list[dict]) -> dict:
        grouped = {}

        for item in pairs_with_metadata:
            key = PairGrouping.canonical_pair_key(
                item["token0"].symbol,
                item["token1"].symbol,
            )

            if key not in grouped:
                grouped[key] = []

            grouped[key].append(item)

        return {
            pair_key: dex_pairs
            for pair_key, dex_pairs in grouped.items()
            if len(dex_pairs) >= 2
        }