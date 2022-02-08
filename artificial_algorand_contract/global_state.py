from typing import Literal
from artificial_algorand_contract.helper.classes.algorand import AlgoAcc
from .helper.__secrets__ import (
    ACCOUNT1_MNEMONICS,
    ACCOUNT1_ADDRESS,
    ACCOUNT2_MNEMONICS,
    ACCOUNT2_ADDRESS,
    ACCOUNT3_MNEMONICS,
    ACCOUNT3_ADDRESS,
    PURE_STAKE_API_KEY,
)
from algosdk.v2client import algod

""" TYPES """
Client_Type = Literal["pure_stake", "sandbox"]

""" GLOBAL VARIABLES """
state_initialized = False


class TestAccounts:
    main: AlgoAcc
    alice: AlgoAcc
    bob: AlgoAcc

    def __init__(self) -> None:
        self.main = AlgoAcc(
            mnemonics=ACCOUNT1_MNEMONICS,
            address=ACCOUNT1_ADDRESS,
        )
        self.alice = AlgoAcc(
            mnemonics=ACCOUNT2_MNEMONICS,
            address=ACCOUNT2_ADDRESS,
        )
        self.bob = AlgoAcc(
            mnemonics=ACCOUNT3_MNEMONICS,
            address=ACCOUNT3_ADDRESS,
        )


class ClientInfo:
    client_type: Client_Type
    algod_address: str
    algod_token: str
    headers: dict | None

    def __init__(self, client_type: Client_Type):
        self.client_type = client_type
        if client_type == "pure_stake":
            self.algod_address = "https://testnet-algorand.api.purestake.io/ps2"
            assert PURE_STAKE_API_KEY
            self.algod_token = PURE_STAKE_API_KEY
            self.headers = {
                "X-API-Key": self.algod_token,
            }
        elif client_type == "sandbox":
            print(f"Get client_type={client_type}. Using sandbox:")
            self.algod_address = "http://localhost:4001"
            self.algod_token = (
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            )
        else:
            raise ValueError(f"client_type={client_type} not supported.")


class AlgoConfig:
    accounts: TestAccounts
    client_info: ClientInfo
    client: algod.AlgodClient

    def __init__(self, client_type: Client_Type) -> None:
        global state_initialized
        if state_initialized:
            raise Exception("State has already been initialized")

        self.accounts = TestAccounts()
        self.client_info = ClientInfo(client_type)
        self.client = algod.AlgodClient(
            algod_token=self.client_info.algod_token,
            algod_address=self.client_info.algod_address,
            headers=self.client_info.headers,
        )
        state_initialized = True

    def initClient(self) -> None:
        pass


algo_config = AlgoConfig(client_type="pure_stake")
