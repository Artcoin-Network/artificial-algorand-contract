"""Basic Counter Application"""

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
    compileTeal,
)

from ..classes.algorand import TealCmdList, TealPackage, TealParam

"""Basic Counter Application"""


def approval_program():
    handle_creation = Seq([App.globalPut(Bytes("Count"), Int(0)), Return(Int(1))])

    handle_opt_in = Return(Int(1))
    handle_closeout = Return(Int(1))
    handle_updateapp = Return(Global.creator_address() == Txn.sender())
    handle_deleteapp = Return(Global.creator_address() == Txn.sender())
    scratchCount = ScratchVar(TealType.uint64)

    add = Seq(
        [
            scratchCount.store(App.globalGet(Bytes("Count"))),
            App.globalPut(Bytes("Count"), scratchCount.load() + Int(1)),
            Return(Int(1)),
        ]
    )

    deduct = Seq(
        [
            scratchCount.store(App.globalGet(Bytes("Count"))),
            If(
                scratchCount.load() > Int(0),
                App.globalPut(Bytes("Count"), scratchCount.load() - Int(1)),
            ),
            Return(Int(1)),
        ]
    )

    handle_no_op = Cond(
        [
            Txn.application_args.length() == Int(0),
            Return(Int(1)),
        ],
        [
            And(Global.group_size() == Int(1), Txn.application_args[0] == Bytes("Add")),
            add,
        ],
        [
            And(
                Global.group_size() == Int(1),
                Txn.application_args[0] == Bytes("Deduct"),
            ),
            deduct,
        ],
    )

    program = Cond(
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.on_completion() == OnComplete.OptIn, handle_opt_in],
        [Txn.on_completion() == OnComplete.CloseOut, handle_closeout],
        [Txn.on_completion() == OnComplete.UpdateApplication, handle_updateapp],
        [Txn.on_completion() == OnComplete.DeleteApplication, handle_deleteapp],
        [Txn.on_completion() == OnComplete.NoOp, handle_no_op],
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


teal_param: TealParam = {
    "local_ints": 0,
    "local_bytes": 0,
    "global_ints": 1,
    "global_bytes": 0,
}

cmd_list: TealCmdList = [
    ["Add"],
    ["Deduct"],
]
counter_package = TealPackage(
    "counter", approval_program(), clear_program(), teal_param, cmd_list
)
