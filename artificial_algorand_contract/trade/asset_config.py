# assets config to use only in this folder/module
from typing import TypedDict

from artificial_algorand_contract.classes.algorand import TealCmdList

""" NON-AAA CONFIG """
aUSD_ID = 0


class AssetConfig(TypedDict):
    """
    Asset configuration, used by the contract_generator.py and ASADeploy.
    """

    name: str
    url: str
    AAA_id: int | None
    total: int  # use same number as real life.
    unit: str
    price: float  # price of some micro unit. in contract using `price * e[decimal]`
    decimals: int
    # collateralizable: bool
    # starting with contract_: only used in contract part, not in ASA part.
    contract_cmd_list: TealCmdList
    contract_local_ints_scheme: list | dict  # only care about len
    contract_local_bytes_scheme: list | dict  # only care about len
    contract_global_ints_scheme: list | dict  # only care about len
    contract_global_bytes_scheme: list | dict  # only care about len


default_cmd_list: TealCmdList = [
    ["buy"],  # aUSD -> artificial Assets
    ["sell"],  # artificial Assets -> aUSD
]
default_local_ints_scheme = {
    "AAA_balance": "how many AAA user has",
    "margin_trading": "if user is allowed, 1/0",
    "margin_rate": "how to save diffrent margin rate on every trade?"
    # TODO:discuss: :up:
    # TODO:discuss: "limit" function (e.g. will buy when price is lower than limit) on chain?
}
default_local_bytes_scheme = ["last_msg"]
default_global_ints_scheme = []
default_global_bytes_scheme = ["price_info"]  # origin of price, implementation of ZKP.
# TODO:discuss: do we need 3 contracts for 1 AAA? price_info, ZKP and trade
# TODO:discuss: 1 account can have 10 smart contract.

aBTC_config: AssetConfig = {
    "name": "Bitcoin",
    "url": "https://bitcoin.org",
    "AAA_id": None,
    "total": 100000000,
    "unit": "BTC",
    "price": 100_000_000,
    "decimals": 8,
    # "collateralizable": False,
    "contract_cmd_list": default_cmd_list,
    "contract_local_ints_scheme": default_local_ints_scheme,
    "contract_local_bytes_scheme": default_local_bytes_scheme,
    "contract_global_ints_scheme": default_global_ints_scheme,
    "contract_global_bytes_scheme": default_global_bytes_scheme,
}
