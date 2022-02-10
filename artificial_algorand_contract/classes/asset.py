""" TODO: add an Asset Class (optionally initiate with asset_id)"""
from typing import TypedDict

from algosdk.future.transaction import AssetConfigTxn
from algosdk.v2client.algod import AlgodClient

from ..helper.transaction_helper import get_default_params, wait_for_confirmation
from .algo_config import algo_config
from .algorand import AlgoAcc

client = algo_config.client
mainAcc: AlgoAcc = algo_config.accounts.main


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
    # ptx = client.pending_transaction_info(txid) There's no info about asset ID.
    # print(ptx)
    # asset_id = ptx["asset-index"]

    wait_for_confirmation(client, txid)  # wait until asset is created
    txinfo = client.pending_transaction_info(txid)
    asset_id = txinfo["asset-index"]

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


test_asset_config: AssetConfig = {
    # TODO: this should load from env file
    "sender": mainAcc.addr,
    # there's no params (sp)
    "total": 1234_000000,
    "default_frozen": False,
    "unit_name": "test",
    "asset_name": "test",
    "manager": mainAcc.addr,
    "reserve": mainAcc.addr,
    "freeze": mainAcc.addr,
    "clawback": mainAcc.addr,
    "url": "https://artcoin.network/",
    "decimals": 5,  # For 1>>16 unit in contract. More decimals causes inaccuracy.
}


def create_test_asset():
    return create_asset(
        client,
        test_asset_config,
    )


def create_run_once():
    ASSET_ID = create_ART()
    STABLE_ID = create_aUSD()
    print(f"created asset {ASSET_ID}, stable {STABLE_ID}")
    print("create_run_once done")
    return {
        "ASSET_ID": ASSET_ID,
        "STABLE_ID": STABLE_ID,
    }
