from abc import ABC, abstractmethod

from app.models.price import PriceQuote


class DexAdapter(ABC):
    @abstractmethod
    def get_price(self, base_token: dict, quote_token: dict) -> PriceQuote:
        pass