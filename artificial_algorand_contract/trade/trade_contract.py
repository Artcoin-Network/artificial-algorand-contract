from pyteal import Int, Mode, Return, compileTeal

from artificial_algorand_contract.trade.asset_config import AssetConfig, aUSD_ID
from ..classes.algorand import TealCmdList, TealPackage, TealParam

TEAL_VERSION = 5


def gen_teal_param(asset_config: AssetConfig) -> TealParam:
    """
    Generate the teal param by AssetConfig
    Args:
        asset_config (AssetConfig): config of asset, can be found in asset_config.py
    Returns:
        TealParam: teal param
    """
    # for typing and readability

    """ Smart contract typing """
    cmd_list: TealCmdList = asset_config["contract_cmd_list"]
    local_ints_scheme = asset_config["contract_local_ints_scheme"]
    local_bytes_scheme = asset_config["contract_local_bytes_scheme"]
    global_ints_scheme = asset_config["contract_global_ints_scheme"]
    global_bytes_scheme = asset_config["contract_global_bytes_scheme"]

    """ Dynamic Param from typing data """
    teal_param: TealParam = {
        "local_ints": len(local_ints_scheme),
        "local_bytes": len(local_bytes_scheme),
        "global_ints": len(global_ints_scheme),
        "global_bytes": len(global_bytes_scheme),
    }
    return teal_param


def approval_program(asset_config: AssetConfig) -> str:
    """
    Generate the approval contract TEAL code by AssetConfig
    Args:
        asset_config (AssetConfig): config of asset, can be found in asset_config.py
    Returns:
        str: TEAL code of the approval contract
    """
    # for typing and readability
    AAA_ID = asset_config["AAA_id"]
    STABLE_ID = aUSD_ID
    ASSET_PRICE = asset_config["price"]
    DEFAULT_CR = 5  # 500%
    program = Return(Int(0))
    return compileTeal(program, Mode.Application, version=TEAL_VERSION)


def clear_program():
    program = Return(Int(1))
    # Mode.Application specifies that this is a smart contract
    return compileTeal(program, Mode.Application, version=TEAL_VERSION)
