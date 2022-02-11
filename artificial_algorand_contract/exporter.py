## non-package imports
from json import dump as json_dump
from pathlib import Path
from typing import Callable
from counter.counter_contract import *  # or next line

# from counter.counter_contract import approval_program, clear_program, state_storage
## package imports
# from counter.counter_contract import approval_program, clear_program, state_storage

# TODO: maybe add a "topic" and add this string to filename.

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "output"


def write_output_teal(filename: str, compile_func: Callable) -> None:
    output_path = OUTPUT_DIR / filename
    with open(output_path, "w") as f:
        f.write(compile_func())


def write_json_config(filename: str, config_dict) -> None:
    output_path = OUTPUT_DIR / filename
    with open(output_path, "w") as f:
        json_dump(config_dict, f, indent=4)


def main():
    write_output_teal("approval.teal", approval_program)
    write_output_teal("clear.teal", clear_program)
    write_json_config("state.json", teal_param)


if __name__ == "__main__":
    main()
    print("finished")
