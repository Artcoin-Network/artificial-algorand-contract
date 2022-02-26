from pyteal import (
    Add,
    And,
    App,
    Assert,
    Bytes,
    Cond,
    Div,
    Ed25519Verify,
    Global,
    Gtxn,
    If,
    Int,
    Minus,
    Mode,
    OnComplete,
    Return,
    Seq,
    compileTeal,
)

from ..classes.algorand import TealCmdList, TealPackage, TealParam
from .asset_config import AssetConfig, aUSD_ID

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
    Generate the approval contract TEAL code by AssetConfig.
    Args:
        asset_config (AssetConfig): config of asset, can be found in asset_config.py
    Returns:
        str: TEAL code of the approval contract
    """
    # All asset in this contract are counted in units of its own "decimal".
    # for typing and readability
    AAA_ID = asset_config["AAA_id"]  # raise exception?
    if AAA_ID == 0:
        input("AAA_ID shouldn't be 0")
    AAA_NAME = asset_config["AAA_name"]
    SUM_ASSET = f"+{AAA_NAME}"
    STABLE_ID = aUSD_ID
    PRICE_B16 = Int(int(asset_config["price"] * 2**16))
    AAA_ATOM_IN_ONE = Int(10 ** asset_config["decimals"])
    SucceedSeq = Seq(Return(Int(1)))
    AppCall = Gtxn[0]
    Receiving = Gtxn[1]
    Sending = Gtxn[2]

    def FailWithMsg(msg: str):  # TODO:ref: use byte_msg
        # TODO:feat: add timestamp to last_msg
        # didn't change local_bytes_scheme, nor updated teal_param
        return Seq(
            If(
                Bytes(msg) == Bytes(""),
                App.localPut(
                    AppCall.sender(), Bytes("last_msg"), Bytes("[ERR]:EMPTY_ERR_MSG")
                ),
                App.localPut(AppCall.sender(), Bytes("last_msg"), Bytes("[ERR]" + msg)),
            ),
            Return(Int(0)),
        )

    """ User mint $ART$ to get aUSD """
    on_buy = Seq(
        Assert(
            And(
                Global.group_size() == Int(3),
                Receiving.asset_receiver() == Global.creator_address(),
                AppCall.sender() == Receiving.sender(),
                Receiving.sender() == Sending.asset_receiver(),
                Receiving.xfer_asset() == Int(STABLE_ID),
                Sending.xfer_asset() == Int(AAA_ID),
            ),
        ),
        Assert(
            (Receiving.asset_amount() << Int(16)) * AAA_ATOM_IN_ONE / PRICE_B16
            == Sending.asset_amount(),
            # TODO:discuss: price affected by network delay?
        ),
        App.localPut(
            Receiving.sender(),
            Bytes(AAA_NAME),
            Add(
                App.localGet(Receiving.sender(), Bytes(AAA_NAME)),
                Receiving.asset_amount(),
            ),
        ),
        App.globalPut(
            Bytes(SUM_ASSET),
            Add(App.globalGet(Bytes(SUM_ASSET)), (Receiving.asset_amount())),
        ),
        SucceedSeq,
    )

    on_sell = Seq(
        # user burn aUSD to get $ART$ back,
        # TODO:feat: checked user has enough staked $ART$ in [on_call]
        Assert(
            And(
                Global.group_size() == Int(3),
                Receiving.asset_receiver() == Global.creator_address(),
                AppCall.sender() == Receiving.sender(),  # called and paid by same user
                Receiving.sender() == Sending.asset_receiver(),
                Receiving.xfer_asset() == Int(STABLE_ID),
                Sending.xfer_asset() == Int(AAA_ID),
            ),
        ),
        Assert(
            (Receiving.asset_amount() << Int(16)) / PRICE_B16
            == Sending.asset_amount(),  # TODO:discuss: price affected by network delay?
        ),
        App.localPut(
            Receiving.sender(),
            Bytes(AAA_NAME),
            Minus(
                App.localGet(Receiving.sender(), Bytes(AAA_NAME)),
                Sending.asset_amount(),
            ),
        ),
        App.globalPut(
            Bytes(SUM_ASSET),
            Minus(
                App.globalGet(Bytes(SUM_ASSET)),
                Sending.asset_amount(),
            ),
        ),
        SucceedSeq,
    )
    on_creation = Seq(
        App.globalPut(Bytes(SUM_ASSET), Int(0)),
        # == DEFAULT_CR*(2**CRDD), value of $ART$ minted / value of aUSD issued == DEFAULT_CR.
        SucceedSeq,
    )  # global_ints_scheme

    on_opt_in = Seq(
        App.localPut(AppCall.sender(), Bytes("AAA_balance"), Int(0)),
        App.localPut(AppCall.sender(), Bytes("margin_trading"), Int(0)),
        App.localPut(AppCall.sender(), Bytes("last_msg"), Bytes("OptIn OK.")),
        SucceedSeq,
    )  # always allow user to opt in

    on_close_out = FailWithMsg("Only allow 0 $ART$ user, or lose $ART$.")

    on_update_app = Return(
        And(
            Global.creator_address() == AppCall.sender(),  # TODO: manager
            Ed25519Verify(
                data=AppCall.application_args[0],
                sig=AppCall.application_args[1],
                key=AppCall.application_args[2],
            ),  # security, should use a password, high cost is ok.
        )
    )

    on_deleteapp = on_update_app  # Same security level as update_app

    on_call = Cond(
        [
            And(
                AppCall.application_args[0] == Bytes("buy"),
            ),
            on_buy,
        ],
        [
            And(
                AppCall.application_args[0] == Bytes("burn"),
                App.localGet(Receiving.asset_sender(), Bytes(AAA_NAME))
                >= Receiving.asset_amount(),
                # TODO:discuss: user should can sell more than bought? diff from stake.
                # correct logic depend on ACID (atomicity, consistency, isolation, durability).
                # cannot be used to cheat (will not parallel) for ACID.
            ),
            on_sell,
        ],
        [
            Int(1),
            FailWithMsg("wrong args"),
        ],
    )

    program = Cond(
        [AppCall.application_id() == Int(0), on_creation],
        [AppCall.on_completion() == OnComplete.NoOp, on_call],
        [AppCall.on_completion() == OnComplete.CloseOut, on_close_out],
        [AppCall.on_completion() == OnComplete.UpdateApplication, on_update_app],
        [AppCall.on_completion() == OnComplete.DeleteApplication, on_deleteapp],
        [AppCall.on_completion() == OnComplete.OptIn, on_opt_in],
    )

    return compileTeal(program, Mode.Application, version=TEAL_VERSION)


def clear_program():
    program = Return(Int(1))
    # Mode.Application specifies that this is a smart contract
    return compileTeal(program, Mode.Application, version=TEAL_VERSION)
