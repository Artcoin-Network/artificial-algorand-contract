""" AlgoSDK.ENCODING """
from algosdk.encoding import decode_address as decode_address_algosdk
from algosdk import account as algosdk_account


def decode_address(address: str) -> bytes:
    if address is None:
        raise ValueError("address is None")
    result = decode_address_algosdk(address)
    if not isinstance(result, bytes):
        raise TypeError("type is not bytes")
    return result


class account:
    @staticmethod
    def generate_account() -> tuple[str, str]:
        sk, addr = algosdk_account.generate_account()
        if not isinstance(sk, str) or not isinstance(addr, str):
            raise Exception("generate_account() failed")
        return sk, addr

    @staticmethod
    def address_from_private_key(private_key: str) -> str:
        if not isinstance(private_key, str):
            raise TypeError("private_key is not str")
        result = algosdk_account.address_from_private_key(private_key)
        if not isinstance(result, str):
            raise TypeError("type is not str")
        return result


""" not working, to note: """
# def generate_account() -> tuple[str, str]:
#     sk, addr = algosdk_account.generate_account()
#     if not isinstance(sk, str) or not isinstance(addr, str):
#         raise Exception("generate_account() failed")
#     return sk, addr
# algosdk_account.generate_account = generate_account
# account = algosdk_account


# account.generate_account = generate_account

r""" still not working: not typing method: based on https://stackoverflow.com/a/16719281/16223122 """
# classify = lambda module: type(module.__name__, (), {key: staticmethod(value) if callable(value) else value for key, value in ((name, getattr(module, name)) for name in dir(module))})
