external = {  # a global variable
    "algo_artificial_price": 1,
    "artificial_asset_id": 0,
    "exchange_app_id": 0,
}


def get_external():
    print("get_external not implemented")
    return external


def exchange_algo(amount: float):
    print("exchange_algo not implemented")


def exchange_artificial(amount: float):
    print("exchange_artificial not implemented")


def _admin_dispense_artificial(amount: float):
    print("_admin_dispense not implemented")


def test():
    print("test started")
    external = get_external()
    _admin_dispense_artificial(1)
    exchange_algo(1)
    exchange_artificial(1)
