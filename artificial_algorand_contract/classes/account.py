""" TODO: Move Account from algorand.py """

from .algo_config import algo_config

client = algo_config.client
adminAcc = algo_config.accounts.admin


def get_account_info(account_addr: str) -> dict:
    return client.account_info(account_addr)


def check_main():
    account_info = get_account_info(adminAcc.addr)
    print("adminAcc info:", account_info)
