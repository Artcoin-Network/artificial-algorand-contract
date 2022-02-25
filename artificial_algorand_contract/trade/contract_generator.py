import imp
from .asset_config import AssetConfig, aBTC_config
from .trade_contract import approval_program, clear_program, gen_teal_param
from ..classes.algorand import TealCmdList, TealPackage, TealParam


def gen_trade_contract(asset_config: AssetConfig) -> TealPackage:
    """
    Generate the trade contract TEAL TealPackage by AssetConfig

    Args:
        asset_config (AssetConfig): config of asset, can be found in asset_config.py

    Returns:
        str: TEAL code of the trade contract
    """

    return TealPackage(
        asset_config["ASSET_name"],
        approval_program(asset_config),
        clear_program(),
        gen_teal_param(asset_config),
        asset_config["contract_cmd_list"],
    )


# example
btc_package = gen_trade_contract(aBTC_config)
