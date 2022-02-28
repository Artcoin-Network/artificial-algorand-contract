# code like TST1 is to relate the test file `algob-tester.ts`.
# Add directory to path so that algobpy can be imported
from math import ceil
import sys

sys.path.insert(0, ".")

from algobpy.parse import parse_params
from pyteal import *  # type: ignore wildcard import

STATIC_PRICE = 3456789


def price_verifier():
    """
    This supports algob-tester, to get external global state
    """
    SuccessSeq = Seq(
        # Log(Bytes("success")),
        Return(Int(1)),
    )
    on_creation = Seq(
        App.globalPut(Bytes("last_price"), Int(STATIC_PRICE)),
        App.globalPut(Bytes("last_UTC0"), Bytes("1234567890-1234")),
        SuccessSeq,
    )
    on_opt_in = SuccessSeq
    on_close_out = SuccessSeq
    on_update_app = SuccessSeq
    on_delete_app = SuccessSeq
    on_call = If(
        Int(1),
        Seq(
            App.globalPut(Bytes("last_price"), Gtxn[0].application_args[0]),
            App.globalPut(Bytes("last_UTC0"), Gtxn[0].application_args[1]),
            SuccessSeq,
        ),
        Return(Int(0)),
    )

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.OptIn, on_opt_in],
        [Txn.on_completion() == OnComplete.CloseOut, on_close_out],
        [Txn.on_completion() == OnComplete.UpdateApplication, on_update_app],
        [Txn.on_completion() == OnComplete.DeleteApplication, on_delete_app],
        [Txn.on_completion() == OnComplete.NoOp, on_call],
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
    compiled = compileTeal(price_verifier(), Mode.Application, version=6)

    """write to file"""
    with open("price_verifier.teal", "w") as f:
        f.write(compiled)

    print(compiled)
