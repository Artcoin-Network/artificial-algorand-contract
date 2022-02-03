import json
from algosdk.v2client import algod


def read_settings():
    with open("algorand-settings.json") as json_file:
        data = json.load(json_file)
        return data


def get_client():
    from ..__secrets__ import PURE_STAKE_API_KEY
    settings = read_settings()
    client_type: str = settings["algorand_client"]
    algod_client: algod.AlgodClient
    # using py310
    match client_type :
        
        case "pure_stack":
            algod_address = "https://testnet-algorand.api.purestake.io/ps2"
            algod_token = PURE_STAKE_API_KEY
            headers = {
                "X-API-Key": algod_token,
            }
            algod_client = algod.AlgodClient(
                algod_token=algod_token, algod_address=algod_address,headers=headers
            )
        case _:
            print(f"Get client_type={client_type}. Using sandbox:")
            algod_address = "http://localhost:4001"
            algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            algod_client = algod.AlgodClient(
                algod_token=algod_token, algod_address=algod_address
            )
    return algod_client


def main():
    settings = read_settings()
    print(settings)


if __name__ == "__main__":
    main()
