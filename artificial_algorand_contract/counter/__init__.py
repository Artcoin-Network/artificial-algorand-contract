from .counter_contract import *

teal = {
    "approval": approval_program(),
    "clear": clear_program(),
    "param": storage_state(),
}
