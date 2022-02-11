from ..classes.algorand import TealPackage
from .escrow_contract import *

counter_package = TealPackage(approval_program(), clear_program(), teal_param, cmd_list)
