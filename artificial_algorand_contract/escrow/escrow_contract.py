""" PyTeal to escrow asset and get stable coin aUSD. """

from ..resources import (
    ASSET_NAME,
    ASSET_ID,
    STABLE_NAME,
    STABLE_ID,
    SUM_ASSET,
    SUM_STABLE,
)
from ..classes.algorand import TealCmdList, TealPackage, TealParam


from pyteal import (
    And,
    App,
    Bytes,
    Cond,
    Global,
    If,
    Int,
    Mode,
    OnComplete,
    Return,
    ScratchVar,
    Seq,
    TealType,
    Txn,
    TxnField,
    compileTeal,
    Ed25519Verify,
    InnerTxnBuilder,
)

local_ints_scheme = [ASSET_NAME, "aUSD"]  # to check if user can burn / need escrow more
local_bytes_scheme = ["history"]  # TODO: for more data, maybe more "blocks"?
global_ints_scheme = {
    SUM_ASSET: f"sum of {ASSET_NAME} collateral, with unit of decimal.",
    SUM_STABLE: f"sum of {STABLE_NAME} issued, with unit of decimal.",
    "CRN": "collateralisation ratio = numerator / 2^32,"
    + "in range [0,2^32] with precision of 2^-32",
    # collateralisation ratio numerator
}
global_bytes_scheme = ["price_info"]  # origin of price, implementation of ZKP.

teal_param: TealParam = {
    "local_ints": len(local_ints_scheme),
    "local_bytes": len(local_bytes_scheme),
    "global_ints": len(global_ints_scheme),
    "global_bytes": len(global_bytes_scheme),
}

cmd_list: TealCmdList = [
    ["escrow"],  # send $ART$ to escrow
    ["redeem"],  # redeem $ART$ from escrow
]


def approval_program():
    handle_creation = Seq(
        [
            App.globalPut(Bytes(SUM_ASSET), Int(0)),  # unit: 1>>16 $ART$
            App.globalPut(Bytes(SUM_STABLE), Int(0)),  # unit: 1>>16 aUSD
            App.globalPut(
                Bytes("CRN"), Int(5 << 32)
            ),  # == 5* 2**32, assume 1$ART$=1aUSD
            Return(Int(1)),
        ]
    )  # global_ints_scheme

    handle_opt_in = Return(Int(1))  # always allow user to opt in

    handle_close_out = Return(
        Int(1)
    )  # TODO: check user's escrow. Only 0 escrow user can close out.

    handle_update_app = Return(
        And(
            Global.creator_address() == Txn.sender(),
            Ed25519Verify(
                data=Txn.application_args[0],
                sig=Txn.application_args[1],
                key=Txn.application_args[2],
            ),  # TODO: discuss: security, should use a password? high cost is ok.
        )
    )

    handle_deleteapp = handle_update_app  # Same security level as update_app

    scratch_sum_asset = ScratchVar(TealType.uint64)  # used in both escrow and redeem
    scratch_sum_stable = ScratchVar(TealType.uint64)  # used in both escrow and redeem
    scratch_CRN = ScratchVar(TealType.uint64)  # used in both escrow and redeem
    scratch_issuing = ScratchVar(TealType.uint64)  # aUSD, only used in escrow
    scratch_returning = ScratchVar(TealType.uint64)  # $ART$, only used in redeem
    escrow = Seq(
        # User escrow $ART$ to get aUSD
        [
            scratch_sum_asset.store(App.globalGet(Bytes(SUM_ASSET))),  # TODO:why store?
            scratch_sum_stable.store(App.globalGet(Bytes(SUM_STABLE))),
            scratch_CRN.store(App.globalGet(Bytes("CRN"))),
            scratch_issuing.store(
                (Txn.asset_amount() << 16) / (scratch_CRN.load() << 32)
            ),
            # Issue aUSD to user
            InnerTxnBuilder.Begin(),  # TODO: not sure if this is correct
            InnerTxnBuilder.SetFields(
                {
                    TxnField.note: Bytes(f"issuance of aUSD on TXN_ID: {Txn.tx_id()}"),
                    TxnField.xfer_asset: Int(STABLE_ID),  # TODO: not sure
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
                App.localGet(Txn.sender(), Bytes(ASSET_NAME)) + Txn.asset_amount(),
            ),
            App.localPut(
                Txn.sender(),
                Bytes(STABLE_NAME),
                App.localGet(Txn.sender(), Bytes(STABLE_NAME)) + scratch_issuing.load(),
            ),
            App.globalPut(
                Bytes(SUM_ASSET),
                scratch_sum_asset.load() + (Txn.asset_amount() << 16),
            ),
            App.globalPut(
                Bytes(SUM_STABLE), scratch_sum_stable.load() + scratch_issuing.load()
            ),
            Return(Int(1)),
        ]
    )

    redeem = Seq(
        # user redeem $ART$ from aUSD, assuming user has enough escrowed $ART$
        [
            scratch_sum_asset.store(App.globalGet(Bytes(SUM_ASSET))),  # TODO:why store?
            scratch_sum_stable.store(App.globalGet(Bytes(SUM_STABLE))),
            scratch_CRN.store(App.globalGet(Bytes("CRN"))),
            scratch_returning.store(
                (Txn.asset_amount() << 16) * (scratch_CRN.load() << 32)
            ),
            # Issue aUSD to user
            InnerTxnBuilder.Begin(),  # TODO: not sure if this is correct
            InnerTxnBuilder.SetFields(
                {
                    TxnField.note: Bytes(f"issuance of aUSD on TXN_ID: {Txn.tx_id()}"),
                    TxnField.xfer_asset: Int(ASSET_ID),  # TODO: not sure
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
                App.localGet(Txn.sender(), Bytes(ASSET_NAME)) + Txn.asset_amount(),
            ),
            App.localPut(
                Txn.sender(),
                Bytes(STABLE_NAME),
                App.localGet(Txn.sender(), Bytes(STABLE_NAME))
                + scratch_returning.load(),
            ),
            App.globalPut(
                Bytes(SUM_ASSET),
                scratch_sum_asset.load() + (Txn.asset_amount() << 16),
            ),
            App.globalPut(
                Bytes(SUM_STABLE), scratch_sum_stable.load() + scratch_returning.load()
            ),
            Return(Int(1)),
        ]
    )

    handle_no_op = Cond(
        [
            And(
                Global.group_size() == Int(1),
                Txn.application_args[0] == Bytes("escrow"),
            ),
            escrow,
        ],
        [
            And(
                Global.group_size() == Int(1),
                Txn.application_args[0] == Bytes("redeem"),
                App.localGet(Txn.sender(), Bytes(STABLE)) >= Txn.asset_amount(),
                # TODO: make sure correct logic
            ),
            redeem,
        ],
    )

    program = Cond(
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.on_completion() == OnComplete.OptIn, handle_opt_in],
        [Txn.on_completion() == OnComplete.CloseOut, handle_close_out],
        [Txn.on_completion() == OnComplete.UpdateApplication, handle_update_app],
        [Txn.on_completion() == OnComplete.DeleteApplication, handle_deleteapp],
        [Txn.on_completion() == OnComplete.NoOp, handle_no_op],
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
