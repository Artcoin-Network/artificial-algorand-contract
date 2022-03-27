from typing import Any


class Exchange:  # the exchange, with prop `users`
    global_aAsset: list[int]
    users: list[User]  # type: ignore
    aStocks: list[int]
    ZKP: Any

    def __init__(self) -> None:
        pass


class User:
    ex: Exchange
    pk: str
    aUSD: int
    aAsset: list[int]

    def __init__(self, ex, pk) -> None:
        self.ex = ex
        self.pk = pk
        self.aUSD = 0

    def _validate_trading_period(self, token_id: int) -> bool:
        if token_id in self.ex.aStocks:
            import datetime

            return (
                self.ex.ZKP.price_info(token_id).last_update_time
                > datetime.datetime.now().timestamp()
            )

        return True

    def _before_all(self, token_id) -> bool:
        if self._validate_trading_period(token_id):
            return True
        return False

    def buy(self, token_id: int, token_price: float, aUSD: int) -> None:
        if not self._before_all(token_id):
            return None
        self.aUSD -= aUSD
        fee = aUSD * 0.001
        aUSD = int(aUSD - fee)
        token_amount = int(aUSD / token_price)
        self.aAsset[token_id] += token_amount
        self.ex.global_aAsset[token_id] += token_amount

    def sell(self, token_id: int, token_price: float, aUSD: int) -> None:
        if not self._before_all(token_id):
            return None
        self.aUSD += aUSD
        fee = aUSD * 0.001
        aUSD = int(aUSD - fee)
        token_amount = int(aUSD / token_price)
        self.aAsset[token_id] -= token_amount
        self.ex.global_aAsset[token_id] -= token_amount
