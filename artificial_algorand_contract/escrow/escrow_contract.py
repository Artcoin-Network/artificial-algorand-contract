""" PyTeal to escrow asset and get stable coin aUSD. """
# TODO: make sure that ASSET and STABLE have the same decimals, otherwise this can happen: 1e-8 ART <-> 1e-4 aUSD
# TODO: Fail message when user doesn't have enough minted ART. (in burn>mint case)
from pyteal import (
    Add,
    And,
    App,
    Bytes,
    Cond,
    Div,
    Ed25519Verify,
    Global,
    If,
    InnerTxnBuilder,
    Int,
    Minus,
    Mode,
    Mul,
    OnComplete,
    Return,
    ScratchVar,
    Seq,
    ShiftRight,
    TealType,
    Txn,
    TxnField,
    compileTeal,
)

from ..classes.algorand import TealCmdList, TealPackage, TealParam
from ..resources import (
    ASSET_NAME,
    STABLE_NAME,
    SUM_ASSET,
    SUM_STABLE,
    # ASSET_ID,
    # STABLE_ID,
)

""" SETTING """
# this is for algob testing. to use on testnet, use imports
ASSET_ID = 9
STABLE_ID = 10

CRDD = 32  # CRDB is the number of byte digits in the CRD
CRD = Int(
    1 << CRDD
)  # collateralisation ratio denominator, reciprocal of precision of CR.

""" Smart contract typing """
cmd_list: TealCmdList = [
    ["escrow"],  # send $ART$ to escrow
    ["redeem"],  # redeem $ART$ from escrow
]
local_ints_scheme = [ASSET_NAME, "aUSD"]  # to check if user can burn / need escrow more
local_bytes_scheme = [
    "history"
]  # not needed at redeem: no more data for more data, maybe more "blocks"?
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
    FailSeq = Seq(Return(Int(0)))

    on_creation = Seq(
        App.globalPut(Bytes(SUM_ASSET), Int(0)),
        App.globalPut(Bytes(SUM_STABLE), Int(0)),
        App.globalPut(
            Bytes("CRN"), Int(5 << CRDD)
        ),  # == 5* 2**CRDD, assuming 1$ART$=1aUSD, minting 5$ART$ to get 1aUSD.
        SucceedSeq,
    )  # global_ints_scheme

    on_opt_in = SucceedSeq  # always allow user to opt in

    on_close_out = Return(
        Int(0)  # not allow anyone to close out escrow for now, for todo
    )  # TODO: check user's escrow. Only user with 0 escrow can close out (not losing $ART$).

    on_update_app = Return(
        And(
            Global.creator_address() == Txn.sender(),  # TODO: manager
            Ed25519Verify(
                data=Txn.application_args[0],
                sig=Txn.application_args[1],
                key=Txn.application_args[2],
            ),  # security, should use a password, high cost is ok.
        )
    )

    on_deleteapp = on_update_app  # Same security level as update_app

    scratch_issuing = ScratchVar(TealType.uint64)  # aUSD, only used once in escrow
    scratch_returning = ScratchVar(TealType.uint64)  # $ART$, only used once in redeem

    """ User escrow $ART$ to get aUSD """
    on_escrow = Seq(
        scratch_issuing.store(
            ShiftRight(Div(Txn.asset_amount(), App.globalGet(Bytes("CRN"))), Int(CRDD))
        ),  # Remember that all needs Int()!
        # Issue aUSD to user
        InnerTxnBuilder.Begin(),  # TODO: not sure if this is correct
        InnerTxnBuilder.SetFields(
            {
                # TODO:bug: :down: this line has some problem
                # TxnField.note: Bytes(f"issuance of aUSD on TXN_ID: {Txn.tx_id()}"),
                TxnField.xfer_asset: Int(STABLE_ID),
                TxnField.asset_amount: scratch_issuing.load(),
                TxnField.sender: Global.creator_address(),
                TxnField.asset_receiver: Txn.sender(),
                TxnField.asset_close_to: Global.creator_address(),
            }
        ),
        InnerTxnBuilder.Submit(),  # Issue aUSD to user
        App.localPut(
            Txn.sender(),
            Bytes(ASSET_NAME),
            Add(App.localGet(Txn.sender(), Bytes(ASSET_NAME)), Txn.asset_amount()),
        ),
        App.localPut(
            Txn.sender(),
            Bytes(STABLE_NAME),
            Add(
                App.localGet(Txn.sender(), Bytes(STABLE_NAME)),
                scratch_issuing.load(),
            ),
        ),
        App.globalPut(
            Bytes(SUM_ASSET),
            Add(App.globalGet(Bytes(SUM_ASSET)), (Txn.asset_amount())),
        ),
        App.globalPut(
            Bytes(SUM_STABLE),
            Add(App.globalGet(Bytes(SUM_STABLE)), scratch_issuing.load()),
        ),
        SucceedSeq,
    )

    on_redeem = Seq(
        # user redeem $ART$ from aUSD, assuming user has enough escrowed $ART$
        [
            # TODO:fix: check asset == $ART$, not any random asset
            scratch_returning.store(
                ShiftRight(
                    Mul((Txn.asset_amount()), App.globalGet(Bytes("CRN"))), Int(CRDD)
                )
            ),
            # Issue aUSD to user
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    # TODO:bug: :down: this line has some problem
                    TxnField.note: Bytes(f"issuance of aUSD on TXN_ID: {Txn.tx_id()}"),
                    TxnField.xfer_asset: Int(ASSET_ID),
                    TxnField.asset_amount: scratch_returning.load(),
                    TxnField.asset_receiver: Txn.sender(),
                    TxnField.sender: Global.creator_address(),
                    TxnField.asset_close_to: Global.creator_address(),
                }
            ),
            InnerTxnBuilder.Submit(),  # Issue aUSD to user
            App.localPut(
                Txn.sender(),
                Bytes(ASSET_NAME),
                Minus(
                    App.localGet(Txn.sender(), Bytes(ASSET_NAME)),
                    Txn.asset_amount(),
                ),
            ),
            App.localPut(
                Txn.sender(),
                Bytes(STABLE_NAME),
                Minus(
                    App.localGet(Txn.sender(), Bytes(STABLE_NAME)),
                    scratch_returning.load(),
                ),
            ),
            App.globalPut(
                Bytes(SUM_ASSET),
                Minus(
                    App.globalGet(Bytes(SUM_ASSET)),
                    (Txn.asset_amount()),
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

    on_call = Cond(
        [
            And(
                Global.group_size() == Int(1),
                Txn.application_args[0] == Bytes("escrow"),
            ),
            on_escrow,
        ],
        [
            And(
                Global.group_size() == Int(1),
                Txn.application_args[0] == Bytes("redeem"),
                App.localGet(Txn.sender(), Bytes(STABLE_NAME)) >= Txn.asset_amount(),
                # correct logic depend on ACID (atomicity, consistency, isolation, durability).
                # cannot be used to cheat (will not parallel) for ACID.
            ),
            on_redeem,
        ],
        [
            Int(1),
            Return(Int(0)),  # Fail if no correct args.
        ],
    )

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.OptIn, on_opt_in],
        [Txn.on_completion() == OnComplete.CloseOut, on_close_out],
        [Txn.on_completion() == OnComplete.UpdateApplication, on_update_app],
        [Txn.on_completion() == OnComplete.DeleteApplication, on_deleteapp],
        [Txn.on_completion() == OnComplete.NoOp, on_call],
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
