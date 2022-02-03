from typing import TypedDict
from algosdk import mnemonic

# from .typed_algosdk import decode_address, account as t_account


def address_to_public_key(address: str) -> str:
    """Convert an address to a public key."""
    import base64

    return base64.b32encode(decode_address(address)).decode()


""" TYPING """
Mnemonics = str


class AlgoAccSecret(TypedDict):
    sk: str | None
    mnemonics: Mnemonics | None


sampleInfo = AlgoAccSecret(
    sk="Z2CNMQ6JQQUBEOOJRDHTWVHJX55ZL7CRILNNBICBFY6Q5V7OFDG2IBYVFM", mnemonics=None
)
sampleInfo2 = AlgoAccSecret(
    sk=None,
    mnemonics="monster sniff airport silent try this wheat style walnut anchor pond carry air letter sign matrix permit hope sentence canyon faculty strategy spider able indoor",
)


class AlgoAcc:
    __sk: str
    addr: str
    addr: str
    pk: str

    def __init__(self, id, info: AlgoAccSecret):
        self.id = id
        # GET sk, and generate all from sk
        if not info:
            self.create()

        elif info["sk"]:
            self.retrive(info["sk"])

        elif info["mnemonics"]:
            self.retrive_from_mnemonics(info["mnemonics"])
        else:
            raise Exception("No info to create account")

        self.addr = t_account.address_from_private_key(self.__sk)
        self.pk = address_to_public_key(self.addr)
        self.mnemonics = mnemonic.from_private_key(self.__sk)

    def __getitem__(self, item):
        return self.__dict__[item]

    def create(self):
        private_key, address = t_account.generate_account()

        print(
            f"Created of acc #{self.id} with address and passphrase\n {address}\n {mnemonic.from_private_key(private_key)}"
        )
        self.__sk = private_key

    def retrive(self, sk):
        self.__sk = sk

    def retrive_from_mnemonics(self, mnemonics: Mnemonics):
        self.__sk = mnemonic.to_private_key(mnemonics)


if __name__ == "__main__":
    """TEST"""
    import sys

    print(sys.path)
    from ..__secrets__ import MNEMONIC1, MNEMONIC2, MNEMONIC3

    accounts = {}
    accounts[1] = AlgoAcc(1, AlgoAccSecret(sk=None, mnemonics=MNEMONIC1))
    accounts[2] = AlgoAcc(2, AlgoAccSecret(sk=None, mnemonics=MNEMONIC2))
    accounts[3] = AlgoAcc(3, AlgoAccSecret(sk=None, mnemonics=MNEMONIC3))

    print(accounts)
