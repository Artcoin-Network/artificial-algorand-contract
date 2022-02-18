# code like TST1 is to relate the test file `algob-tester.ts`.
# TODO: rekey and close remainder
# Add directory to path so that algobpy can be imported
import sys

sys.path.insert(0, ".")

from algobpy.parse import parse_params
from pyteal import *  # type: ignore wildcard import


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
    Success = Seq(
        App.globalPut(Bytes("succeeded"), App.globalGet(Bytes("succeeded")) + Int(1)),
        Return(Int(1)),
    )
    sub1 = Seq(
        App.globalPut(
            Bytes("var1"), App.globalGet(Bytes("var1")) * Int(2)
        ),  # has to use MUL
        App.globalPut(Bytes("console"), Bytes("group1")),
        # App.globalPut(Bytes("var1"), Mul(App.globalGet(Bytes("var1")), Int(2))),
        If(
            Int(1),
            Success,
            Return(Int(0)),
        ),
    )
    group1pass = Seq(
        App.globalPut(Bytes("console"), Bytes("group1")),
        Return(Int(1)),
    )
    on_creation = Seq(
        App.globalPut(Bytes("called"), Int(0)),
        App.globalPut(Bytes("succeeded"), Int(0)),
        App.globalPut(Bytes("console"), Bytes("empty")),
        App.globalPut(Bytes("var1"), Int(1)),
        App.globalPut(Bytes("var2"), Int(2)),
        App.globalPut(Bytes("var3"), Int(3)),
        Return(Int(1)),
    )
    on_opt_in = Return(Int(1))
    on_close_out = Return(Int(1))
    on_update_app = Return(Int(1))
    on_delete_app = Return(Int(1))
    on_call = Seq(
        App.globalPut(Bytes("called"), App.globalGet(Bytes("called")) + Int(1)),
        Cond(
            [
                And(
                    Global.group_size() == Int(1),
                    Txn.application_args[0] == Bytes("callsub1"),
                ),
                sub1,
            ],
            [
                Global.group_size() == Int(1),  # TST1, TST2
                group1pass,
            ],
            [Int(1), Return(Int(0))],
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
    compiled = compileTeal(algob_tester(), Mode.Application)

    """write to file"""
    # with open("algob-tester.teal", "w") as f:
    #     f.write(compiled)

    print(compiled)
    # print(compileTeal(algob_tester(params["RECEIVER_ADDRESS"]), Mode.Signature))
