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
    Mul,
    OnComplete,
    Return,
    ScratchVar,
    Seq,
    ShiftLeft,
    TealType,
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
    AAA_ID = asset_config["AAA_id"] or 0  # raise exc?
    STABLE_ID = aUSD_ID
    ASSET_PRICE = asset_config["price"]
    PRICE_B16 = Int(int(asset_config["price"] * 2**16))
    SucceedSeq = Seq(Return(Int(1)))

    def FailWithMsg(msg: str):  # TODO:ref: use byte_msg
        # TODO:feat: add timestamp to last_msg
        # didn't change local_bytes_scheme, nor updated teal_param
        return Seq(
            If(
                Bytes(msg) == Bytes(""),
                App.localPut(
                    Gtxn[0].sender(), Bytes("last_msg"), Bytes("[ERR]:EMPTY_ERR_MSG")
                ),
                App.localPut(Gtxn[0].sender(), Bytes("last_msg"), Bytes("[ERR]" + msg)),
            ),
            Return(Int(0)),
        )

    scratch_issuing = ScratchVar(TealType.uint64)  # aUSD, only used once in mint
    scratch_returning = ScratchVar(TealType.uint64)  # $ART$, only used once in burn

    """ User mint $ART$ to get aUSD """
    on_mint = Seq(
        Assert(
            And(
                Global.group_size() == Int(3),
                Gtxn[1].asset_receiver() == Global.creator_address(),
                Gtxn[0].sender() == Gtxn[1].sender(),  # called and paid by same user
                Gtxn[1].sender() == Gtxn[2].asset_receiver(),  #  and mint to same user
                Gtxn[1].xfer_asset() == Int(AAA_ID),
                Gtxn[2].xfer_asset() == Int(STABLE_ID),
            ),
        ),
        scratch_issuing.store(
            Div(
                ShiftLeft(
                    Gtxn[1].asset_amount() * PRICE_B16,
                    Int(CRDD),
                ),
                App.globalGet(Bytes("CRN")),
            )
        ),
        Assert(
            scratch_issuing.load()
            == Gtxn[2].asset_amount(),  # TODO:discuss: price affected by network delay?
        ),
        App.localPut(
            Gtxn[1].sender(),
            Bytes(ASSET_NAME),
            Add(
                App.localGet(Gtxn[1].sender(), Bytes(ASSET_NAME)),
                Gtxn[1].asset_amount(),
            ),
        ),
        App.localPut(
            Gtxn[1].sender(),
            Bytes(STABLE_NAME),
            Add(
                App.localGet(Gtxn[1].sender(), Bytes(STABLE_NAME)),
                scratch_issuing.load(),
            ),
        ),
        App.globalPut(
            Bytes(SUM_ASSET),
            Add(App.globalGet(Bytes(SUM_ASSET)), (Gtxn[1].asset_amount())),
        ),
        App.globalPut(
            Bytes(SUM_STABLE),
            Add(App.globalGet(Bytes(SUM_STABLE)), scratch_issuing.load()),
        ),
        SucceedSeq,
    )

    on_burn = Seq(
        # user burn aUSD to get $ART$ back,
        # TODO:feat: checked user has enough escrowed $ART$ in [on_call]
        Assert(
            And(
                Global.group_size() == Int(3),
                Gtxn[1].asset_receiver() == Global.creator_address(),
                Gtxn[0].sender() == Gtxn[1].sender(),  # called and paid by same user
                Gtxn[1].sender() == Gtxn[2].asset_receiver(),  #  and mint to same user
                Gtxn[1].xfer_asset() == Int(STABLE_ID),
                Gtxn[2].xfer_asset() == Int(AAA_ID),
            ),
        ),
        scratch_returning.store(
            Mul((Gtxn[1].asset_amount()), App.globalGet(Bytes("CRN")))
            / ShiftLeft(Int(ASSET_PRICE), Int(CRDD))
        ),
        Assert(
            scratch_returning.load()  # TODO:ref: not needed, can use Gtxn[2].asset_amount()
            == Gtxn[2].asset_amount(),  # TODO:discuss: price affected by network delay?
        ),
        App.localPut(
            Gtxn[1].sender(),
            Bytes(ASSET_NAME),
            Minus(
                App.localGet(Gtxn[1].sender(), Bytes(ASSET_NAME)),
                Gtxn[2].asset_amount(),
            ),
        ),
        App.localPut(
            Gtxn[1].sender(),
            Bytes(STABLE_NAME),
            Minus(
                App.localGet(Gtxn[1].sender(), Bytes(STABLE_NAME)),
                Gtxn[1].asset_amount(),
            ),
        ),
        App.globalPut(
            Bytes(SUM_ASSET),
            Minus(
                App.globalGet(Bytes(SUM_ASSET)),
                Gtxn[2].asset_amount(),
            ),
        ),
        App.globalPut(
            Bytes(SUM_STABLE),
            Minus(
                App.globalGet(Bytes(SUM_STABLE)),
                Gtxn[1].asset_amount(),
            ),
        ),
        SucceedSeq,
    )
    on_creation = Seq(
        App.globalPut(Bytes(SUM_ASSET), Int(0)),
        App.globalPut(Bytes(SUM_STABLE), Int(0)),
        App.globalPut(Bytes("CRN"), Int(DEFAULT_CR << CRDD)),
        # == DEFAULT_CR*(2**CRDD), value of $ART$ minted / value of aUSD issued == DEFAULT_CR.
        SucceedSeq,
    )  # global_ints_scheme

    on_opt_in = Seq(
        App.localPut(Gtxn[0].sender(), Bytes(ASSET_NAME), Int(0)),
        App.localPut(Gtxn[0].sender(), Bytes(STABLE_NAME), Int(0)),
        App.localPut(Gtxn[0].sender(), Bytes("last_msg"), Bytes("OptIn OK.")),
        SucceedSeq,
    )  # always allow user to opt in

    on_close_out = FailWithMsg("Only allow 0 $ART$ user, or lose $ART$.")

    on_update_app = Return(
        And(
            Global.creator_address() == Gtxn[0].sender(),  # TODO: manager
            Ed25519Verify(
                data=Gtxn[0].application_args[0],
                sig=Gtxn[0].application_args[1],
                key=Gtxn[0].application_args[2],
            ),  # security, should use a password, high cost is ok.
        )
    )

    on_deleteapp = on_update_app  # Same security level as update_app

    on_call = Cond(
        [
            And(
                Gtxn[0].application_args[0] == Bytes("mint"),
            ),
            on_mint,
        ],
        [
            And(
                Gtxn[0].application_args[0] == Bytes("burn"),
                App.localGet(Gtxn[1].asset_sender(), Bytes(STABLE_NAME))
                >= Gtxn[1].asset_amount(),
                # TODO:discuss: move to on_burn? needed? (TEAL has integer underflow)
                # correct logic depend on ACID (atomicity, consistency, isolation, durability).
                # cannot be used to cheat (will not parallel) for ACID.
            ),
            on_burn,
        ],
        [
            Int(1),
            FailWithMsg("wrong args"),
        ],
    )

    program = Cond(
        [Gtxn[0].application_id() == Int(0), on_creation],
        [Gtxn[0].on_completion() == OnComplete.NoOp, on_call],
        [Gtxn[0].on_completion() == OnComplete.CloseOut, on_close_out],
        [Gtxn[0].on_completion() == OnComplete.UpdateApplication, on_update_app],
        [Gtxn[0].on_completion() == OnComplete.DeleteApplication, on_deleteapp],
        [Gtxn[0].on_completion() == OnComplete.OptIn, on_opt_in],
    )

    return compileTeal(program, Mode.Application, version=TEAL_VERSION)


def clear_program():
    program = Return(Int(1))
    # Mode.Application specifies that this is a smart contract
    return compileTeal(program, Mode.Application, version=TEAL_VERSION)
