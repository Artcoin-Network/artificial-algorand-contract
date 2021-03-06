""" from https://raw.githubusercontent.com/algorand/docs/master/examples/smart_contracts/v2/python/stateful_smart_contracts.py """
# TODO 0209: Fix local state read etc.
# TODO 0209: Add new contract for stake.
# TODO 0209: Dispense some asset for test accounts.
import base64
from typing import Literal, TypedDict, overload

from algosdk import account, mnemonic
from algosdk.future import transaction
from algosdk.v2client.algod import AlgodClient

from artificial_algorand_contract.helper.external import open_algo_explorer

from ..classes.algo_config import TestAccounts, algo_config
from ..classes.algorand import AlgoAcc, TealNoOpArgs, TealPackage
from .transaction_helper import get_default_params, wait_for_confirmation


# helper function to compile program source
def compile_program(client: AlgodClient, source_code: str):
    return base64.b64decode(client.compile(source_code)["result"])


# create new application
def create_app(
    client: AlgodClient,
    private_key,
    approval_program,
    clear_program,
    global_schema,
    local_schema,
):
    # define sender as creator
    sender = account.address_from_private_key(private_key)

    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    params = get_default_params(client)

    # create unsigned transaction
    txn = transaction.ApplicationCreateTxn(
        sender,
        params,
        on_complete,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
    )

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response["application-index"]
    print("Created new app-id: ", app_id)

    return app_id


# opt-in to application
def opt_in_app(client: AlgodClient, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)
    print("OptIn from account: ", sender)

    params = get_default_params(client)

    # create unsigned transaction
    txn = transaction.ApplicationOptInTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("OptIn to app-id: ", transaction_response["txn"]["txn"]["apid"])


# call application
def call_app(client: AlgodClient, private_key, index, app_args):
    # declare sender
    sender = account.address_from_private_key(private_key)
    print("Call from account: ", sender)

    params = get_default_params(client)
    # create unsigned transaction
    txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("Called app-id: ", transaction_response["txn"]["txn"]["apid"])
    if "global-state-delta" in transaction_response:
        print("Global State updated :\n", transaction_response["global-state-delta"])
    if "local-state-delta" in transaction_response:
        print("Local State updated :\n", transaction_response["local-state-delta"])


# read user local state
def read_local_state(client: AlgodClient, addr, app_id):
    results = client.account_info(addr)

    local_state = results["apps-local-state"]
    print(
        f"local_state of account {addr} (showing all) for app_id {app_id}: ",
        local_state,
        # TODO: this key doesn't exist. Maybe old version? #pragma version 2
    )
    # for index in local_state:
    #     if local_state[index] == app_id:
    #         print(
    #             f"local_state of account {addr} for app_id {app_id}: ",
    #             # local_state["key-value"],
    #             # TODO: this key doesn't exist. Maybe old version? #pragma version 2
    #         )


# read app global state
# TODO: this and read local state should go to client helper (new file).
def read_global_state(client: AlgodClient, addr, app_id):
    results = client.account_info(addr)
    apps_created = results["created-apps"]
    for app in apps_created:
        if app["id"] == app_id:
            print(f"global_state for app_id {app_id}: ", app["params"]["global-state"])


# update existing application
def update_app(
    client: AlgodClient, private_key, app_id, approval_program, clear_program
):
    # declare sender
    sender = account.address_from_private_key(private_key)

    #    # define initial value for key "timestamp"
    #    app_args = [b'initial value']

    params = get_default_params(client)

    # create unsigned transaction
    txn = transaction.ApplicationUpdateTxn(
        sender, params, app_id, approval_program, clear_program
    )  # , app_args)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response["txn"]["txn"]["apid"]
    print("Updated existing app-id: ", app_id)


# delete application
def delete_app(client: AlgodClient, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)

    params = get_default_params(client)

    # create unsigned transaction
    txn = transaction.ApplicationDeleteTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("Deleted app-id: ", transaction_response["txn"]["txn"]["apid"])


# close out from application
def close_out_app(client: AlgodClient, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)

    params = get_default_params(client)

    # create unsigned transaction
    txn = transaction.ApplicationCloseOutTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("Closed out from app-id: ", transaction_response["txn"]["txn"]["apid"])


# clear application
def clear_app(client: AlgodClient, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)

    params = get_default_params(client)

    # create unsigned transaction
    txn = transaction.ApplicationClearStateTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print(
        "Cleared", sender, "from app-id: ", transaction_response["txn"]["txn"]["apid"]
    )


def full_contract_test():
    from ..counter import counter_package  # TODO: dynamic imports by name.

    algod_client = algo_config.client

    approval_program_source_initial = counter_package.approval
    approval_program_source_refactored = counter_package.approval
    clear_program_source = counter_package.clear

    # declare application state storage (immutable)
    local_ints = 0
    local_bytes = 0
    global_ints = 1
    global_bytes = 0
    global_schema = transaction.StateSchema(global_ints, global_bytes)
    local_schema = transaction.StateSchema(local_ints, local_bytes)

    # compile programs
    approval_program = compile_program(algod_client, approval_program_source_initial)
    clear_program = compile_program(algod_client, clear_program_source)

    # user declared account mnemonics
    creator_mnemonic = algo_config.accounts.admin.request_mnemonics()
    user_mnemonic = algo_config.accounts.bob.request_mnemonics()
    # define private keys
    creator_private_key = mnemonic.to_private_key(creator_mnemonic)
    user_private_key = mnemonic.to_private_key(user_mnemonic)

    # create new application
    app_id = create_app(
        algod_client,
        creator_private_key,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
    )

    # opt-in to application
    opt_in_app(algod_client, user_private_key, app_id)

    # call application without arguments
    call_app(algod_client, user_private_key, app_id, None)

    # read local state of application from user account
    read_local_state(
        algod_client, account.address_from_private_key(user_private_key), app_id
    )

    # read global state of application
    read_global_state(
        algod_client, account.address_from_private_key(creator_private_key), app_id
    )

    # update application
    approval_program = compile_program(algod_client, approval_program_source_refactored)
    update_app(
        algod_client, creator_private_key, app_id, approval_program, clear_program
    )

    # call application with arguments
    # now = datetime.datetime.now().strftime("%H:%M:%S")
    # app_args = [now.encode("utf-8")]
    args = "Add"
    app_args = [args.encode("utf-8")]
    call_app(algod_client, user_private_key, app_id, app_args)

    # read local state of application from user account
    read_local_state(
        algod_client, account.address_from_private_key(user_private_key), app_id
    )

    # close-out from application
    close_out_app(algod_client, user_private_key, app_id)

    # opt-in again to application
    opt_in_app(algod_client, user_private_key, app_id)

    # call application with arguments
    call_app(algod_client, user_private_key, app_id, app_args)

    # read local state of application from user account
    read_local_state(
        algod_client, account.address_from_private_key(user_private_key), app_id
    )

    # delete application
    delete_app(algod_client, creator_private_key, app_id)

    # clear application from user account
    clear_app(algod_client, user_private_key, app_id)


def test_clean_up(app_id: int):
    algod_client = algo_config.client
    creator_mnemonic = algo_config.accounts.admin.request_mnemonics()
    creator_private_key = mnemonic.to_private_key(creator_mnemonic)
    delete_app(algod_client, creator_private_key, app_id)
