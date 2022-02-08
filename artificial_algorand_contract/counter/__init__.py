from artificial_algorand_contract.helper.classes.algorand import TealPackage
from .counter_contract import *

## TODO: call with teal.approval or teal.approval_program such things.
# teal : = {
#     "approval": approval_program(),
#     "clear": clear_program(),
#     "param": teal_param(),
# }
counter_package = TealPackage(approval_program(), clear_program(), teal_param, cmd_list)
