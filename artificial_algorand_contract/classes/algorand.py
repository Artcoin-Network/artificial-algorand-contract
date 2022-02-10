from typing import Literal, TypedDict, Any as Any_type, Optional
from ..helper.typed_algosdk import account, mnemonic

""" TYPING """
Mnemonics = str


class AlgoAcc:
    __mnemonics: str
    __sk: str
    addr: str

    def __init__(self, mnemonics: str | list[str] | None, address: str | None) -> None:
        """Get the secret key and address from the mnemonics

        Args:
            mnemonics? (str | list[str]): If None, generate a new account.
            address? (str): Only to assert the address is correct.
        """
        if not mnemonics:
            sk, addr = account.generate_account()
            self.__sk = sk
            self.__mnemonics = mnemonic.from_private_key(self.__sk)
            self.addr = addr
            return
        if not isinstance(mnemonics, str):  # is list
            mnemonics = " ".join(mnemonics)
        self.__mnemonics = mnemonics
        self.__sk = mnemonic.to_private_key(mnemonics)
        self.addr = account.address_from_private_key(self.__sk)
        if address:
            assert self.addr == address

    def __repr__(self) -> str:
        """
        Representation of the object
        """
        return f"<AlgoAcc w/address: {self.addr}>"

    def print_mnemonics(self) -> None:
        print(self.__mnemonics)

    def get_secret_key(self) -> str:
        return self.__sk

    def request_mnemonics(self) -> str:
        return self.__mnemonics


# TODO: Args can be number? How to encode?
TealNoOpArgs = list[Literal["string"] | str]
TealCmdList = list[TealNoOpArgs]


class TealParam(TypedDict):
    """
    A dictionary of parameters for a Teal program

    Args:
        local_ints (int): The number of local ints to allocate
        local_bytes (int): The number of local bytes to allocate
        global_ints (int): The number of global ints to allocate
        global_bytes (int): The number of global bytes to allocate
    """

    local_ints: int
    local_bytes: int
    global_ints: int
    global_bytes: int


class TealPackage:
    """
    A Teal package for to pass into the test function

    Args:
        approval (str): The approval program
        clear (str): The clear program
        param (TealParam): The parameters for the program
        app_args (None | list[TealNoOpArgs]): The arguments to pass to the program
    """

    approval: str
    clear: str
    param: TealParam
    args: list[TealNoOpArgs]

    def __init__(
        self,
        approval: str,
        clear: str,
        param: TealParam,
        app_args: Optional[TealCmdList] = None,
    ) -> None:
        self.approval = approval
        self.clear = clear
        self.param = param
        self.args = app_args or []


def algo_acc_test():
    test_addr = "Z2CNMQ6JQQUBEOOJRDHTWVHJX55ZL7CRILNNBICBFY6Q5V7OFDG2IBYVFM"
    test_mnemonics = "monster sniff airport silent try this wheat style walnut anchor pond carry air letter sign matrix permit hope sentence canyon faculty strategy spider able indoor"
    # test_mnemonics = ["monster", "sniff", "airport", "silent", "try", "this", "wheat", "style", "walnut", "anchor", "pond", "carry", "air", "letter", "sign", "matrix", "permit", "hope", "sentence", "canyon", "faculty", "strategy", "spider", "able", "indoor", ]
    test_acc = AlgoAcc(mnemonics=test_mnemonics, address=test_addr)
    print(test_acc)
