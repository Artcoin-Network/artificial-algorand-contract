from ..typed_algosdk import account, mnemonic

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


def algo_acc_test():
    test_addr = "Z2CNMQ6JQQUBEOOJRDHTWVHJX55ZL7CRILNNBICBFY6Q5V7OFDG2IBYVFM"
    test_mnemonics = "monster sniff airport silent try this wheat style walnut anchor pond carry air letter sign matrix permit hope sentence canyon faculty strategy spider able indoor"
    # test_mnemonics = ["monster", "sniff", "airport", "silent", "try", "this", "wheat", "style", "walnut", "anchor", "pond", "carry", "air", "letter", "sign", "matrix", "permit", "hope", "sentence", "canyon", "faculty", "strategy", "spider", "able", "indoor", ]
    test_acc = AlgoAcc(mnemonics=test_mnemonics, address=test_addr)
    print(test_acc)
