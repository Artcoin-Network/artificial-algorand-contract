CR: float = 5.00


class Exchange:  # the exchange, with prop `users`
    global_ATF: int
    global_aUSD: int
    users: list[User]  # type: ignore

    def __init__(self) -> None:
        pass


class User:
    ex: Exchange
    pk: str
    ATF: int
    aUSD: int
    local_ATF: int
    local_aUSD: int

    def __init__(self, ex, pk) -> None:
        self.ex = ex
        self.pk = pk
        self.ATF = 0
        self.aUSD = 0
        self.local_ATF = 0
        self.local_aUSD = 0

    def stake(self, ATF: int) -> None:
        self.ATF -= ATF
        self.local_ATF += ATF
        self.ex.global_ATF += ATF

    def unstake(self, ATF: int) -> None:
        fee = ATF * 0.001
        self.ex.users[0].ATF += fee  # assumed foundation account
        ATF = int(ATF - fee)
        self.ATF += ATF
        self.local_ATF -= ATF
        self.ex.global_ATF -= ATF

    def forge(self, aUSD: int) -> None:
        self.aUSD += aUSD
        self.local_aUSD += aUSD
        self.ex.global_aUSD += aUSD

    def melt(self, aUSD: int) -> None:
        self.aUSD -= aUSD
        self.local_aUSD -= aUSD
        self.ex.global_aUSD -= aUSD

    def mint(self, ATF: int) -> None:
        self.stake(ATF)
        aUSD = int(self.local_ATF / CR)
        self.forge(aUSD)

    def burn(self, ATF: int) -> None:
        self.unstake(ATF)
        aUSD = int(self.local_ATF / CR)
        self.melt(aUSD)
