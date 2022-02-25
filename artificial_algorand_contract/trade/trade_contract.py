from pyteal import Int, Mode, Return, compileTeal

from artificial_algorand_contract.trade.asset_config import AssetConfig

TEAL_VERSION = 5


def gen_approval_program(asset_config: AssetConfig) -> str:
    """
    Generate the approval contract TEAL code by AssetConfig
    Args:
        asset_config (AssetConfig): config of asset, can be found in asset_config.py
    Returns:
        str: TEAL code of the approval contract
    """
    return approval_program(asset_config["ASA_id"] or 0)


def approval_program(ASA_id: int) -> str:
    """
    Generate the approval contract TEAL code by AssetConfig
    Args:
        asset_config (AssetConfig): config of asset, can be found in asset_config.py
    Returns:
        str: TEAL code of the approval contract
    """
    program = Return(Int(0))
    return compileTeal(program, Mode.Application, version=TEAL_VERSION)


def clear_program():
    program = Return(Int(1))
    # Mode.Application specifies that this is a smart contract
    return compileTeal(program, Mode.Application, version=TEAL_VERSION)
