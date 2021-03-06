# assets config to use only in this folder/module
from typing import TypedDict

from artificial_algorand_contract.classes.algorand import TealCmdList

""" NON-AAA CONFIG """
aUSD_ID = 10


class AssetConfig(TypedDict):
    """
    Asset configuration, used by the contract_generator.py and ASADeploy.
    """

    ASSET_name: str
    AAA_name: str
    url: str
    AAA_unit_name: str
    decimals: int
    AAA_id: int
    total: int  # use same number as real life.
    price: float  # price of 1 unit(like 1BTC=38k) of asset in USD
    # price_b16 = integer, with a fixed unit of 2^-16USD. This should be OK with our supported asset.
    # decided to use price_b16 on meeting 0226 for lower cost.
    # collateralizable: bool

    # starting with contract_: only used in contract part, not in ASA part.
    contract_cmd_list: TealCmdList
    contract_local_ints_scheme: list | dict  # only care about len
    contract_local_bytes_scheme: list | dict  # only care about len
    contract_global_ints_scheme: list | dict  # only care about len
    contract_global_bytes_scheme: list | dict  # only care about len

    # starting with ASA_: only used in ASA part, not in contract part.
    # ASA_defaultFrozen: bool
    # ASA_manager: str
    # ASA_reserve: str
    # ASA_freeze: str
    # ASA_clawback: str
    # ASA_metadataHash: "12345678901234567890123456789012"
    # ASA_note: "note"
    # ASA_noteb64: "noteb64"


default_cmd_list: TealCmdList = [
    ["buy"],  # aUSD -> artificial Assets
    ["sell"],  # artificial Assets -> aUSD
]
default_local_ints_scheme = {
    "AAA_balance": "how many AAA user has",
    "margin_trading": "if user is allowed, 1/0",
    "margin_rate": "how to save diffrent margin rate on every trade?"
    # TODO:SKIP: :up:
    # TODO:SKIP: "limit" function (e.g. will buy when price is lower than limit) on chain?
}
default_local_bytes_scheme = ["last_msg"]
default_global_ints_scheme = []
default_global_bytes_scheme = ["price_info"]  # origin of price, implementation of ZKP.

aBTC_config: AssetConfig = {
    "ASSET_name": "Bitcoin",
    "AAA_name": "aBTC",
    "url": "https://bitcoin.org",
    "AAA_id": 9,
    "total": 100000000,
    "AAA_unit_name": "aBTC",
    "price": 38_613.14,
    "decimals": 8,
    # "collateralizable": False,
    "contract_cmd_list": default_cmd_list,
    "contract_local_ints_scheme": default_local_ints_scheme,
    "contract_local_bytes_scheme": default_local_bytes_scheme,
    "contract_global_ints_scheme": default_global_ints_scheme,
    "contract_global_bytes_scheme": default_global_bytes_scheme,
}

"""
$ART$:
  total: 1e+12
  decimals: 6
  defaultFrozen: false
  unitName: "ART"
  url: "url"
  metadataHash: "12345678901234567890123456789012"
  note: "note"
  noteb64: "noteb64"
  # manager: "WWYNX3TKQYVEREVSW6QQP3SXSFOCE3SKUSEIVJ7YAGUPEACNI5UGI4DZCE"
  # reserve: "WWYNX3TKQYVEREVSW6QQP3SXSFOCE3SKUSEIVJ7YAGUPEACNI5UGI4DZCE"
  # freeze: "WWYNX3TKQYVEREVSW6QQP3SXSFOCE3SKUSEIVJ7YAGUPEACNI5UGI4DZCE"
  # clawback: "WWYNX3TKQYVEREVSW6QQP3SXSFOCE3SKUSEIVJ7YAGUPEACNI5UGI4DZCE"

aUSD:
  total: 1e+18
  decimals: 6
  defaultFrozen: false
  unitName: "aUSD"
  url: "url"
  # User may get "signature validation failed" from node if shorter hash is used.
  metadataHash: "12345678901234567890123456789013"
  note: "note"
  noteb64: "noteb64"
  # manager: "WWYNX3TKQYVEREVSW6QQP3SXSFOCE3SKUSEIVJ7YAGUPEACNI5UGI4DZCE"
  # reserve: "WWYNX3TKQYVEREVSW6QQP3SXSFOCE3SKUSEIVJ7YAGUPEACNI5UGI4DZCE"
  # freeze: "WWYNX3TKQYVEREVSW6QQP3SXSFOCE3SKUSEIVJ7YAGUPEACNI5UGI4DZCE"
  # clawback: "WWYNX3TKQYVEREVSW6QQP3SXSFOCE3SKUSEIVJ7YAGUPEACNI5UGI4DZCE"
  
"""
