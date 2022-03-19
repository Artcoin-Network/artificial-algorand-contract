class Exchange:  # the exchange, with prop `users`
    global_aAsset: list[int]
    users: list[User]  # type: ignore

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

    def buy(self, token_id: int, token_price: float, aUSD: int) -> None:
        self.aUSD -= aUSD
        fee = aUSD * 0.001
        aUSD = int(aUSD - fee)
        token_amount = int(aUSD / token_price)
        self.aAsset[token_id] += token_amount
        self.ex.global_aAsset[token_id] += token_amount

    def sell(self, token_id: int, token_price: float, aUSD: int) -> None:
        self.aUSD += aUSD
        fee = aUSD * 0.001
        aUSD = int(aUSD - fee)
        token_amount = int(aUSD / token_price)
        self.aAsset[token_id] -= token_amount
        self.ex.global_aAsset[token_id] -= token_amount
