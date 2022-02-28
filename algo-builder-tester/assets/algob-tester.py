# code like TST1 is to relate the test file `algob-tester.ts`.
# TODO: rekey and close remainder
# Add directory to path so that algobpy can be imported
import sys

sys.path.insert(0, ".")

from algobpy.parse import parse_params
from pyteal import *  # type: ignore wildcard import

NAMES3 = "btcethxrpadasoldotustltcunitrxfttbchxlmftmetc"
NAMES4 = "usdtusdclunaavaxbusddogeshibatomnearalgomana"


def algob_tester(RECEIVER_ADDRESS=None):
    """
    This tester do cheap tests in algob
    """
    ## INIT ##
    if RECEIVER_ADDRESS is None:
        RECEIVER_ADDRESS = Global.creator_address()
    else:
        RECEIVER_ADDRESS = Addr(RECEIVER_ADDRESS)
    """ code bank
    commons_checks = And(
            Txn.rekey_to() == Global.zero_address(),
            Txn.close_remainder_to() == Global.zero_address(),
        ) """
    ## INIT DONE ##
    SuccessSeq = Seq(
        App.globalPut(Bytes("runstate"), Bytes("succeeded")),
        Return(Int(1)),
    )
    FailSeq = Seq(
        App.globalPut(Bytes("runstate"), Bytes("failed")),
        App.globalPut(Bytes("runstate"), Bytes("failed")),
        Return(Int(0)),
    )
    reset = Seq(  # Seq accepts a list of statements or multiple args. Seq(*cmd_list) and Seq(cmd_list) have same effect.
        [
            App.globalPut(Bytes("console"), Bytes("empty")),
            SuccessSeq,
        ]
    )
    tst5 = Cond(
        [
            Txn.application_args[1] == Bytes("txn"),
            Seq(App.globalPut(Bytes("console"), Bytes("txn>txn")), SuccessSeq),
        ],
        [
            Txn.application_args[1] == Bytes("gtxn"),
            Seq(
                App.globalPut(Bytes("console"), Bytes("gtxn>txn")),
                SuccessSeq,
            ),
        ],
        [
            Gtxn[0].application_args[1] == Bytes("txn"),
            Seq(
                App.globalPut(Bytes("console"), Bytes("txn>gtxn")),
                SuccessSeq,
            ),
        ],
        [
            Gtxn[0].application_args[1] == Bytes("gtxn"),
            Seq(
                App.globalPut(Bytes("console"), Bytes("gtxn>gtxn")),
                SuccessSeq,
            ),
        ],
        [Int(1), FailSeq],
    )  # cannot write Seq(Cond,Return(Int(1))): "All cond body should have same return type"
    tst7 = Seq(App.globalPut(Bytes("console"), Gtxn[0].application_args[1]), SuccessSeq)
    coin_search_list = ScratchVar(TealType.bytes)
    coin_name_len = ScratchVar(TealType.uint64)
    coin_list_len = ScratchVar(TealType.uint64)
    str_start = ScratchVar(TealType.uint64)
    tst8 = Seq(
        coin_name_len.store(Len(Gtxn[0].application_args[1])),
        Cond(
            [
                coin_name_len.load() == Int(3),
                coin_search_list.store(App.globalGet(Bytes("names3"))),
            ],
            [
                coin_name_len.load() == Int(4),
                coin_search_list.store(App.globalGet(Bytes("names4"))),
            ],
        ),
        coin_list_len.store(Len(coin_search_list.load())),
        str_start.store(Int(0)),
        While(str_start.load() < coin_list_len.load()).Do(
            If(
                Gtxn[0].application_args[1]
                == Extract(
                    App.globalGet(Bytes("names3")),
                    str_start.load(),
                    coin_name_len.load(),
                ),
                Seq(
                    App.globalPut(Bytes("console"), Gtxn[0].application_args[1]),
                    SuccessSeq,
                ),
                str_start.store(Add(str_start.load(), coin_name_len.load())),
            )
        ),
        App.globalPut(Bytes("console"), Bytes("coin_name not found")),
        SuccessSeq,
    )
    sub1 = Seq(
        App.globalPut(
            Bytes("var1"), App.globalGet(Bytes("var1")) * Int(2)
        ),  # has to use MUL
        App.globalPut(Bytes("console"), Bytes("sub1run")),
        # App.globalPut(Bytes("var1"), Mul(App.globalGet(Bytes("var1")), Int(2))),
        If(
            Int(1),
            SuccessSeq,
            FailSeq,
        ),
    )
    group1pass = Seq(
        App.globalPut(Bytes("console"), Bytes("group1")),
        SuccessSeq,
    )
    group2pass = Seq(
        App.globalPut(Bytes("console"), Bytes("group2")),
        SuccessSeq,
    )
    on_creation = Seq(
        App.globalPut(Bytes("called"), Int(0)),
        App.globalPut(Bytes("runstate"), Bytes("created")),
        App.globalPut(Bytes("console"), Bytes("empty")),
        App.globalPut(Bytes("var1"), Int(1)),
        App.globalPut(Bytes("var2"), Int(2)),
        App.globalPut(Bytes("var3"), Int(3)),
        App.globalPut(Bytes("names3"), Bytes(NAMES3)),
        App.globalPut(Bytes("names4"), Bytes(NAMES4)),
        SuccessSeq,
    )
    on_opt_in = SuccessSeq
    on_close_out = SuccessSeq
    on_update_app = SuccessSeq
    on_delete_app = SuccessSeq
    on_call = Seq(
        App.globalPut(Bytes("called"), App.globalGet(Bytes("called")) + Int(1)),
        Cond(
            [Gtxn[0].application_args[0] == Bytes("reset"), reset],  # resetApp
            [Gtxn[0].application_args[0] == Bytes("TST8"), tst8],  # TST5  # TST5
            [Gtxn[0].application_args[0] == Bytes("TST7"), tst7],  # TST5  # TST5
            [Gtxn[0].application_args[0] == Bytes("TST5"), tst5],  # TST5  # TST5
            [
                And(
                    Global.group_size() == Int(1),
                    Txn.application_args[0] == Bytes("callsub1"),
                ),
                sub1,
            ],
            [Global.group_size() == Int(1), group1pass],  # TST1, TST2
            [Global.group_size() == Int(2), group2pass],  # TST4
            # :up: len(list) cause compile error
            [Int(1), FailSeq],  # TST3
        ),
    )

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.OptIn, on_opt_in],
        [Txn.on_completion() == OnComplete.CloseOut, on_close_out],
        [Txn.on_completion() == OnComplete.UpdateApplication, on_update_app],
        [Txn.on_completion() == OnComplete.DeleteApplication, on_delete_app],
        [Txn.on_completion() == OnComplete.NoOp, on_call],
        # checked picture https://github.com/algorand/docs/blob/92d2bb3929d2301e1d3acfd164b0621593fcac5b/docs/imgs/sccalltypes.png
    )

    return program


if __name__ == "__main__":
    # this is the default value (globalZeroAddress) of RECEIVER_ADDRESS. If template parameter
    # via scripts is not passed then this value will be used.
    params = {
        "RECEIVER_ADDRESS": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY5HFKQ"
    }

    # Overwrite params if sys.argv[1] is passed
    if len(sys.argv) > 1:
        _params = parse_params(sys.argv[1], params)
        if _params:
            param = _params
    compiled = compileTeal(algob_tester(), Mode.Application, version=5)

    """write to file"""
    with open("algob-tester.teal", "w") as f:
        f.write(compiled)

    print(compiled)
    # print(compileTeal(algob_tester(params["RECEIVER_ADDRESS"]), Mode.Signature))
