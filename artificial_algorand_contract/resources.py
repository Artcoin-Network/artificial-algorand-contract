""" This should work as a resource config loader. """
# from classes/asset.py
ASSET_ID = 70214956  # with name $artificial$, unit $ART$
STABLE_ID = 70214962  # with name $artificial$ USD, unit aUSD

# TODO: read some plain config file to sync accross repos
ASSET_NAME = "$ART$"
SUM_ASSET = f"+{ASSET_NAME}"
STABLE_NAME = "aUSD"
SUM_STABLE = f"+{STABLE_NAME}"

if __name__ == "__main__":
    print(f"SUM_ASSET: {SUM_ASSET}")
