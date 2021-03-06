from json import dump as json_dump
from os import mkdir

from artificial_algorand_contract import OUTPUT_DIR
from artificial_algorand_contract.classes.algorand import TealPackage

# TODO: Add "contract-name" and add this string to filename.
# TODO:ref: export should be part of "TealPackage"


class Exporter:
    def __init__(self, teal_package: TealPackage) -> None:
        self.teal_package = teal_package
        self.name = teal_package.name

    def export_teal_approval(self) -> None:
        if not OUTPUT_DIR.exists():
            mkdir(OUTPUT_DIR)
        with open(OUTPUT_DIR / (self.name + "-approval.teal"), "w") as f:
            f.write(self.teal_package.approval)

    def export_teal_clear(self) -> None:
        with open(OUTPUT_DIR / (self.name + "-clear.teal"), "w") as f:
            f.write(self.teal_package.clear)

    def export_teal_param(self) -> None:
        with open(OUTPUT_DIR / (self.name + "-param.json"), "w") as f:
            json_dump(self.teal_package.param, f, indent=4)

    def export(self) -> None:
        self.export_teal_approval()
        self.export_teal_clear()
        self.export_teal_param()
        print("Exported Teal files to:", OUTPUT_DIR.absolute())


def exporter_test():
    # from .counter import counter_package
    # Exporter(counter_package).export()

    # from .stake import stake_package
    # Exporter(stake_package).export()

    from .trade.contract_generator import gen_trade_contract_package
    from .trade.asset_config import aBTC_config

    Exporter(gen_trade_contract_package(aBTC_config)).export()


if __name__ == "__main__":
    exporter_test()
