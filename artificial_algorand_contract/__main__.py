from artificial_algorand_contract.classes.account import check_main
from artificial_algorand_contract.classes.asset import create_test_asset
from .classes.teal_tester import TealTester
from .counter import counter_package

# MEMO: not deleted 69879104
# TODO0209: enable tester.acc.call()
# TODO0209: functions like call, opt_in etc should be in the tester.acc

create_test_asset()
check_main()
print("finished")
