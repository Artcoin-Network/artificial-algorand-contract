from .helper.contract_helper import TealTester
from .counter import counter_package

# from .global_state import algo_config

tester = TealTester(counter_package, 69871648)
tester.delete()

# full_contract_test()

# test_clean_up(69762334)
# test_clean_up(69761527)
# test_clean_up(69745078)
# test_clean_up(69738415)
# test_clean_up(69730407)
# test_clean_up(69656591)
# from artificial_algorand_contract.helper.classes.algorand import algo_acc_test
# algo_acc_test()

print("finished")
