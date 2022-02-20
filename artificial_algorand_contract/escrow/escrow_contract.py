""" PyTeal to escrow asset and get stable coin aUSD. """
# TODO: make sure that ASSET and STABLE have the same decimals, otherwise this can happen: 1e-8 ART <-> 1e-4 aUSD
# TODO: Fail message when user doesn't have enough minted ART. (in burn>mint case)
# TODO:feat: dry run, check how many can user burn.
# TODO:ref: make a sub-program for making transfer.
# use: two txn in gtxn should have same sender.

from pyteal import (
    Add,
    And,
    App,
    Bytes,
    Cond,
    Div,
    Ed25519Verify,
    Global,
    Gtxn,
    If,
    InnerTxnBuilder,
    Int,
    Minus,
    Mode,
    Mul,
    OnComplete,
    Or,
    Return,
    ScratchVar,
    Seq,
    ShiftRight,
    TealType,
    TxnField,
    compileTeal,
)

from ..classes.algorand import TealCmdList, TealPackage, TealParam
from ..resources import (
    ASSET_NAME,
    STABLE_NAME,  # ASSET_ID,; STABLE_ID,
    SUM_ASSET,
    SUM_STABLE,
)

""" SETTING """
# this is for algob testing. to use on testnet, use imports
ASSET_ID = 9
STABLE_ID = 10
ART_PRICE = 10

CRDD = 32  # CRDB is the number of byte digits in the CRD
CRD = Int(
    1 << CRDD
)  # collateralisation ratio denominator, reciprocal of precision of CR.

""" Smart contract typing """
cmd_list: TealCmdList = [
    ["mint"],  # send $ART$ to mint
    ["burn"],  # burn $ART$ from escrow
]
local_ints_scheme = [ASSET_NAME, "aUSD"]  # to check if user can burn / need escrow more
local_bytes_scheme = [
    "last_msg"
]  # not needed at burn: no more data for more data, maybe more "blocks"?
global_ints_scheme = {
    SUM_ASSET: f"sum of {ASSET_NAME} collateral, with unit of decimal.",
    SUM_STABLE: f"sum of {STABLE_NAME} issued, with unit of decimal.",
    "CRN": "collateralisation ratio = numerator / 2^CRDD, \
        in range [0,2^CRDD] with precision of 2^-CRDD (too fine precision).",
    # collateralisation ratio numerator
    # TODO:discuss: precision 2^-16 should be enough, we don't need that much.
    # TODO:+: Decimal is clearer. 2^-16 ~== 0.0015%. the floating range is much larger.
}
global_bytes_scheme = ["price_info"]  # origin of price, implementation of ZKP.


""" Dynamic Param from typing data """
teal_param: TealParam = {
    "local_ints": len(local_ints_scheme),
    "local_bytes": len(local_bytes_scheme),
    "global_ints": len(global_ints_scheme),
    "global_bytes": len(global_bytes_scheme),
}


def approval_program():
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
        scratch_issuing.store(
            ShiftRight(
                Div(
                    Gtxn[1].asset_amount() * Int(ART_PRICE), App.globalGet(Bytes("CRN"))
                ),
                Int(CRDD),
            )
        ),
        # Issue aUSD to user with an InnerTxn
        InnerTxnBuilder.Begin(),  # TODO: not sure if this is correct
        InnerTxnBuilder.SetFields(
            {
                # TODO:bug: :down: this line has some problem
                # TxnField.note: Bytes(f"issuance of aUSD for TXN_ID: {Gtxn[1].tx_id()}"),
                TxnField.xfer_asset: Int(STABLE_ID),
                TxnField.asset_amount: scratch_issuing.load(),
                TxnField.sender: Global.creator_address(),
                TxnField.asset_receiver: Gtxn[1].sender(),
                TxnField.asset_close_to: Global.creator_address(),
            }
        ),
        InnerTxnBuilder.Submit(),  # Run TXN, Issue aUSD to user
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
        # TODO:feat: check if user has enough escrowed $ART$
        [
            # TODO:fix: check asset == $ART$, not any random asset
            scratch_returning.store(
                ShiftRight(
                    Mul((Gtxn[1].asset_amount()), App.globalGet(Bytes("CRN")))
                    / Int(ART_PRICE),
                    Int(CRDD),
                )
            ),
            # Issue aUSD to user
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    # TODO:bug: :down: this line has some problem
                    TxnField.note: Bytes(
                        f"issuance of aUSD on TXN_ID: {Gtxn[1].tx_id()}"
                    ),
                    TxnField.xfer_asset: Int(ASSET_ID),
                    TxnField.asset_amount: scratch_returning.load(),
                    TxnField.asset_receiver: Gtxn[1].sender(),
                    TxnField.sender: Global.creator_address(),
                    TxnField.asset_close_to: Global.creator_address(),
                }
            ),
            InnerTxnBuilder.Submit(),  # Issue aUSD to user
            App.localPut(
                Gtxn[1].sender(),
                Bytes(ASSET_NAME),
                Minus(
                    App.localGet(Gtxn[1].sender(), Bytes(ASSET_NAME)),
                    Gtxn[1].asset_amount(),
                ),
            ),
            App.localPut(
                Gtxn[1].sender(),
                Bytes(STABLE_NAME),
                Minus(
                    App.localGet(Gtxn[1].sender(), Bytes(STABLE_NAME)),
                    scratch_returning.load(),
                ),
            ),
            App.globalPut(
                Bytes(SUM_ASSET),
                Minus(
                    App.globalGet(Bytes(SUM_ASSET)),
                    (Gtxn[1].asset_amount()),
                ),
            ),
            App.globalPut(
                Bytes(SUM_STABLE),
                Minus(
                    App.globalGet(Bytes(SUM_STABLE)),
                    scratch_returning.load(),
                ),
            ),
            SucceedSeq,
        ]
    )
    on_creation = Seq(
        App.globalPut(Bytes(SUM_ASSET), Int(0)),
        App.globalPut(Bytes(SUM_STABLE), Int(0)),
        App.globalPut(
            Bytes("CRN"), Int(5 << CRDD)
        ),  # == 5* 2**CRDD, assuming 1$ART$=1aUSD, minting 5$ART$ to get 1aUSD.
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
                Global.group_size() == Int(2),
                Gtxn[0].application_args[0] == Bytes("mint"),
                Or(
                    Gtxn[1].receiver() == Global.creator_address(),
                    Gtxn[1].receiver() == Global.zero_address(),
                    # TODO:ask: why changed to 0addr automatically?
                ),
                Gtxn[0].sender() == Gtxn[1].sender(),
            ),
            Seq(
                on_mint,
            ),
        ],
        [
            And(
                Global.group_size() == Int(2),
                Gtxn[0].application_args[0] == Bytes("burn"),
                App.localGet(Gtxn[1].sender(), Bytes(STABLE_NAME))
                >= Gtxn[1].asset_amount(),
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
        # checked picture https://github.com/algorand/docs/blob/92d2bb3929d2301e1d3acfd164b0621593fcac5b/docs/imgs/sccalltypes.png
    )
    # Mode.Application specifies that this is a smart contract
    return compileTeal(program, Mode.Application, version=5)


def clear_program():
    program = Return(Int(1))
    # Mode.Application specifies that this is a smart contract
    return compileTeal(program, Mode.Application, version=5)


# print out the results
# print(approval_program())
# print(clear_program())

escrow_package = TealPackage(
    "escrow", approval_program(), clear_program(), teal_param, cmd_list
)
