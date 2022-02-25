from artificial_algorand_contract.trade.asset_config import AssetConfig


def gen_trade_contract(asset_config: AssetConfig) -> str:
    """
    Generate the trade contract TEAL code by AssetConfig

    Args:
        asset_config (AssetConfig): config of asset, can be found in asset_config.py

    Returns:
        str: TEAL code of the trade contract
    """

    return "FALSE"
