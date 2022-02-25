# assets config to use only in this folder/module
from typing import TypedDict


class AssetConfig(TypedDict):
    """
    Asset configuration, used by the contract_generator.py and ASADeploy.
    """

    name: str
    url: str
    ASA_id: int | None
    unit: str
    price: int
    decimals: int
    # collateralizable: bool


aBTC: AssetConfig = {
    "name": "Bitcoin",
    "url": "https://bitcoin.org",
    "ASA_id": None,
    "unit": "BTC",
    "price": 100_000_000,
    "decimals": 8,
    # "collateralizable": False,
}
