from .counter_contract import *

## TODO: call with teal.approval or teal.approval_program such things.
teal = {
    "approval": approval_program(),
    "clear": clear_program(),
    "param": storage_state(),
}
