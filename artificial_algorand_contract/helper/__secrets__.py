# This file should be considered leaked. Please remove this line after next rotation.
# This file should be kept secret, added in gitignore, and copied from artificial-dev-config repo.
from time import process_time_ns

from dotenv import dotenv_values

from .. import PACKAGE_ROOT

ENV_PATH = PACKAGE_ROOT.parent / "secret.env"
assert ENV_PATH.exists(), f"{ENV_PATH.absolute()} does not exist"
secret = dotenv_values(str(ENV_PATH))

ACCOUNT1_MNEMONICS = secret.get("REACT_APP_TEST_ACCOUNT1_MNEMONIC")
ACCOUNT2_MNEMONICS = secret.get("REACT_APP_TEST_ACCOUNT2_MNEMONIC")
ACCOUNT3_MNEMONICS = secret.get("REACT_APP_TEST_ACCOUNT3_MNEMONIC")
ACCOUNT1_ADDRESS = secret.get("REACT_APP_TEST_ACCOUNT1_ADDRESS")
ACCOUNT2_ADDRESS = secret.get("REACT_APP_TEST_ACCOUNT2_ADDRESS")
ACCOUNT3_ADDRESS = secret.get("REACT_APP_TEST_ACCOUNT3_ADDRESS")
PURE_STAKE_API_KEY = secret.get("REACT_APP_PURE_STAKE_API_KEY")
