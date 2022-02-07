from artificial_algorand_contract.helper.classes.algorand import AlgoAcc
from . import __secrets__


status_initialized = False


class TestAccounts:
    main_account: AlgoAcc
    alice: AlgoAcc
    bob: AlgoAcc

    def __init__(self) -> None:
        self.main_account = AlgoAcc(
            mnemonics=__secrets__.ACCOUNT1_MNEMONIC,
            address=__secrets__.ACCOUNT1_ADDRESS,
        )
        self.alice = AlgoAcc(
            mnemonics=__secrets__.ACCOUNT2_MNEMONIC,
            address=__secrets__.ACCOUNT2_ADDRESS,
        )
        self.bob = AlgoAcc(
            mnemonics=__secrets__.ACCOUNT3_MNEMONIC,
            address=__secrets__.ACCOUNT3_ADDRESS,
        )


class Status:
    accounts: TestAccounts

    def __init__(self) -> None:
        global status_initialized
        if status_initialized:
            raise Exception("Status has already been initialized")

        self.accounts = TestAccounts()

        status_initialized = True
