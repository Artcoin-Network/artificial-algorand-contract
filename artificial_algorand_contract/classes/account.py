""" TODO: Move Account from algorand.py """

from .algo_config import algo_config

client = algo_config.client
mainAcc = algo_config.accounts.main


def get_account_info(account_addr: str) -> dict:
    return client.account_info(account_addr)


def check_main():
    account_info = get_account_info(mainAcc.addr)
    print("mainAcc info:", account_info)
