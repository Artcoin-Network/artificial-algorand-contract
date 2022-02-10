from typing import TypedDict
from unicodedata import decimal
from ..helper.transaction_helper import wait_for_confirmation, get_default_params
from .algorand import AlgoAcc
from .algo_config import AlgoConfig
from algosdk.future.transaction import AssetConfigTxn
from algosdk.v2client.algod import AlgodClient

client = AlgoConfig.client
mainAcc: AlgoAcc = AlgoConfig.accounts.main


class AssetConfig(TypedDict):
    sender: str  # AlgoAcc.addr
    total: int
    default_frozen: bool
    unit_name: str
    asset_name: str
    manager: str  # AlgoAcc.addr
    reserve: str  # AlgoAcc.addr
    freeze: str  # AlgoAcc.addr
    clawback: str  # AlgoAcc.addr
    url: str
    decimals: int


def create_asset(
    client: AlgodClient,
    asset_config: AssetConfig,
):

    params = get_default_params(
        client,
    )

    txn = AssetConfigTxn(sp=params, **asset_config)
    signed_txn = txn.sign(mainAcc.get_secret_key())
    txid = client.send_transaction(signed_txn)
    print(txid)
    ptx = client.pending_transaction_info(txid)
    asset_id = ptx["asset-index"]

    wait_for_confirmation(client, txid)  # wait until asset is created
    account_info = client.account_info(mainAcc.addr)
    print("account_info:", account_info)  ##devprint

    return asset_id


ART_asset_config: AssetConfig = {
    # TODO: this should load from env file
    "sender": mainAcc.addr,
    # there's no params (sp)
    "total": 100000,
    "default_frozen": False,
    "unit_name": "$ART$",
    "asset_name": "$artificial$",
    "manager": mainAcc.addr,
    "reserve": mainAcc.addr,
    "freeze": mainAcc.addr,
    "clawback": mainAcc.addr,
    "url": "https://artcoin.network/",
    "decimals": 4,  # For 1>>16 unit in contract. More decimals causes inaccuracy.
}


def create_ART():
    return create_asset(
        client,
        ART_asset_config,
    )


aUSD_asset_config: AssetConfig = {
    # TODO: this should load from env file
    "sender": mainAcc.addr,
    # there's no params (sp)
    "total": 100000,
    "default_frozen": False,
    "unit_name": "aUSD",
    "asset_name": "$artificial$ USD",
    "manager": mainAcc.addr,
    "reserve": mainAcc.addr,
    "freeze": mainAcc.addr,
    "clawback": mainAcc.addr,
    "url": "https://artcoin.network/",
    "decimals": 4,  # For 1>>16 unit in contract. More decimals causes inaccuracy.
}


def create_aUSD():
    return create_asset(
        client,
        aUSD_asset_config,
    )


def create_run_once():
    create_ART()
    create_aUSD()
