from ctypes import Union
from typing import Literal, Optional, TypedDict

from algosdk.future import transaction
from algosdk.v2client.algod import AlgodClient
from artificial_algorand_contract.helper.contract_helper import (
    call_app,
    clear_app,
    close_out_app,
    compile_program,
    create_app,
    delete_app,
    opt_in_app,
    read_global_state,
    read_local_state,
    update_app,
)

from artificial_algorand_contract.helper.external import open_algo_explorer

from .algo_config import TestAccounts
from .algorand import AlgoAcc, TealNoOpArgs, TealPackage


class TealTesterSetting(TypedDict):
    no_browser: bool


class TealTester:
    app_id: int
    accounts: TestAccounts
    client: AlgodClient
    teal: TealPackage

    def __init__(
        self,
        teal_package: TealPackage,
        app_id: int | None = None,
        settings: Optional[TypedDict] = None,
    ):
        from .algo_config import algo_config, config_initialized

        assert config_initialized
        self.teal = teal_package
        self.client = algo_config.client
        self.accounts = algo_config.accounts
        if app_id is None:
            self.app_id = self.create()
        else:
            self.app_id = app_id
        if settings is None or not settings["no_browser"]:
            open_algo_explorer(self.app_id)

    def _literal_to_account(
        self, account: None | Literal["admin", "alice", "bob"] | AlgoAcc
    ):
        if account is None:
            acc = self.accounts.admin
        elif isinstance(account, AlgoAcc):
            acc = account
        elif account == "admin":
            acc = self.accounts.admin
        elif account == "alice":
            acc = self.accounts.alice
        elif account == "bob":
            acc = self.accounts.bob
        return acc

    def create(self) -> int:
        appid = create_app(
            client=self.client,
            private_key=self.accounts.admin.get_secret_key(),
            approval_program=self.teal.approval,
            clear_program=self.teal.clear,
            global_schema=transaction.StateSchema(
                self.teal.param["global_ints"], self.teal.param["global_bytes"]
            ),
            local_schema=transaction.StateSchema(
                self.teal.param["local_ints"], self.teal.param["local_bytes"]
            ),
        )
        self.app_id = appid
        return appid

    def opt_in(
        self,
        account: Literal["admin", "alice", "bob"] | AlgoAcc,
    ) -> None:
        sk = self._literal_to_account(account).get_secret_key()
        opt_in_app(self.client, sk, self.app_id)

    def close_out(
        self,
        account: Literal["admin", "alice", "bob"] | AlgoAcc,
    ) -> None:
        sk = self._literal_to_account(account).get_secret_key()
        close_out_app(self.client, sk, self.app_id)

    def clear(
        self,
        account: Literal["admin", "alice", "bob"] | AlgoAcc,
    ) -> None:
        sk = self._literal_to_account(account).get_secret_key()
        clear_app(self.client, sk, self.app_id)

    def call(
        self,
        account: Literal["admin", "alice", "bob"] | AlgoAcc,
        args: TealNoOpArgs | None = None,
    ):
        # app_args = [args..encode("utf-8")]
        # TODO: add args check
        call_app(
            client=self.client,
            private_key=self._literal_to_account(account).get_secret_key(),
            index=self.app_id,
            app_args=[arg.encode("utf-8") for arg in args]
            if args is not None
            else None,
        )

    def update(self, new_teal: TealPackage):
        self.teal = new_teal
        update_app(
            client=self.client,
            private_key=self.accounts.admin.get_secret_key(),
            app_id=self.app_id,
            approval_program=compile_program(self.client, self.teal.approval),
            clear_program=compile_program(self.client, self.teal.clear),
        )

    def delete(self):
        delete_app(
            client=self.client,
            private_key=self.accounts.admin.get_secret_key(),
            index=self.app_id,
        )

    def read_local_state(self, account: Literal["admin", "alice", "bob"] | AlgoAcc):
        addr = self._literal_to_account(account).addr
        read_local_state(self.client, addr, self.app_id)

    def read_global_state(self, account: Literal["admin", "alice", "bob"] | AlgoAcc):
        addr = self._literal_to_account(account).addr
        read_global_state(self.client, addr, self.app_id)
