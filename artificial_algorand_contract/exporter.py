## non-package imports
from pathlib import Path
from counter.counter_contract import approval_program, clear_program

## package imports
# from counter.counter_contract import approval_program, clear_program

# TODO: maybe add a "topic" and add this string to filename.

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "output"


def write_output(filename, compile_func):
    output_path = OUTPUT_DIR / filename
    with open(output_path, "w") as f:
        f.write(compile_func())


def main():
    write_output("approval.teal", approval_program)
    write_output("clear.teal", clear_program)


if __name__ == "__main__":
    main()
