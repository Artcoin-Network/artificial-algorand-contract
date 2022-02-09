from artificial_algorand_contract.fulltest import test
from .helper.contract_helper import TealTester, clear_app, close_out_app
from .counter import counter_package

# from .global_state import algo_config
# not deleted : 69879104


tester = TealTester(counter_package, 69879104)
tester.opt_in("alice")
tester.call("alice", None)
tester.read_local_state("alice")
tester.read_global_state("alice")
tester.call("alice", ["Add"])
tester.read_local_state("alice")
tester.call("alice", ["Add"])
tester.call("alice", ["Add"])
tester.read_local_state("alice")
tester.close_out("alice")
tester.opt_in("alice")
tester.call("alice", ["Add"])
tester.read_local_state("alice")
tester.delete()
tester.clear("alice")

# for app_id in [69880656, 69880746, 69880981]:
#     clear_app(tester.client, tester.accounts.alice.get_secret_key(), app_id)


# full_contract_test()

# test_clean_up(69762334)
# test_clean_up(69761527)
# test_clean_up(69745078)
# test_clean_up(69738415)
# test_clean_up(69730407)
# test_clean_up(69656591)

print("finished")
