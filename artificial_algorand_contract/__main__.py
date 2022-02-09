from .helper.contract_helper import TealTester
from .counter import counter_package

# from .global_state import algo_config
# not deleted : 69879104


tester = TealTester(counter_package)
tester.opt_in("alice")
tester.call("alice", None)
tester.read_local_state("alice")
tester.read_global_state("alice")
tester.delete()


# full_contract_test()

# test_clean_up(69762334)
# test_clean_up(69761527)
# test_clean_up(69745078)
# test_clean_up(69738415)
# test_clean_up(69730407)
# test_clean_up(69656591)

print("finished")
