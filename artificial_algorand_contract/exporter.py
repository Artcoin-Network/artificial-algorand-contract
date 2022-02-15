from json import dump as json_dump

from artificial_algorand_contract import OUTPUT_DIR
from artificial_algorand_contract.classes.algorand import TealPackage

# TODO: Add "contract-name" and add this string to filename.


class Exporter:
    def __init__(self, teal_package: TealPackage) -> None:
        self.teal_package = teal_package

    def export_teal_approval(self) -> None:
        with open(OUTPUT_DIR / "approval.teal", "w") as f:
            f.write(self.teal_package.approval)

    def export_teal_clear(self) -> None:
        with open(OUTPUT_DIR / "clear.teal", "w") as f:
            f.write(self.teal_package.clear)

    def export_teal_param(self) -> None:
        with open(OUTPUT_DIR / "param.json", "w") as f:
            json_dump(self.teal_package.param, f, indent=4)

    def export(self) -> None:
        self.export_teal_approval()
        self.export_teal_clear()
        self.export_teal_param()
        print("Exported Teal files to:", OUTPUT_DIR.absolute())


def exporter_test():
    from .counter import counter_package  # or next line

    Exporter(counter_package).export()


if __name__ == "__main__":
    exporter_test()
