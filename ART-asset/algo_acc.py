from algosdk import mnemonic, account
from typed_algosdk import decode_address, account as t_account


def address_to_public_key(address: str) -> str:
    """Convert an address to a public key."""
    import base64

    return base64.b32encode(decode_address(address)).decode()


class AlgoAcc:

    pk: str
    sk: str
    addr: str

    def __init__(self, mnemonics: list[str], id):
        private_key, address = t_account.generate_account()
        print("My address: {}".format(address))
        print("My passphrase: {}".format(mnemonic.from_private_key(private_key)))
        self.pk = address_to_public_key(address)
        self.sk = private_key
        self.addr = address

    def __getitem__(self, item):
        return self.__dict__[item]


acct = account.generate_account()
address1 = acct[1]
print("Account 1")
print(address1)
mnemonic1 = mnemonic.from_private_key(acct[0])
