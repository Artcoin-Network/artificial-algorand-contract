## DEV Resources

## Install

1. Install [Poetry](https://python-poetry.org/) with [Poetry Install Guide](https://python-poetry.org/docs/master/#installing-with-the-official-installer)
2. Initiate Poetry: `poetry shell`
3. Activate python venv:
4. Use [symmetric-secret-share](https://github.com/PabloLION/symmetric-secret-share) (installed by poetry): initiate local key chain`sss key` and add the following key. Then download file `sss inject ./sss.json` (or use `sss inject -k <key> ./sss.json`). ASK SOMEONE IN OUR TEAM TO USE OUR KEY.

   ```json
       "artificial-dev-console": {
         "url": "https://raw.githubusercontent.com/PabloLION/symmetric-secrete-share/main/tests/sample.encrypted",
         "key": `{ASK SOMEONE IN OUR TEAM TO USE OUR KEY}`,
         "comment": ""
       }
   ```

## Use

After preparing the all the steps above in the [Install Chapter](#install), you may want to switch algod-client, test PyTeal code, etc.

### Switch Algod Client

Currently all `client` are using the same algod client initialized by last line in [algo_config](./artificial_algorand_contract/classes/algo_config.py). This param currently supports

- `pure_stake` (testnet of PureStake)
- `sandbox` (Algorand sandbox)

### Test PyTeal

1. Write some PyTeal file, and bundle them to a class `TealPackage`, defined in [algorand.py](./artificial_algorand_contract/classes/algorand.py). E.g. `counter_package = TealPackage(approval_program(), clear_program(), teal_param, cmd_list)`
2. Instance the `TealPackage` to a `TealTester` defined in [teal_tester.py](./artificial_algorand_contract/classes/teal_tester.py). E.g. `TealTester(counter_package)`.  
   To manipulate an old AppId(type: int), use `TealTester(TealPackage, old_app_id)`
3. Call the methods of `TealTester`. The auto-complete function will help you pass the args. E.g. `counter_full_test()` in [tests.py](./artificial_algorand_contract/tests.py)
4. Hints:
   - To use the preset test accounts, just past "main", "alice", "bob" as the account arg.
   - To NOT open the indexer AlgoExplore in browser, add a `settings` arg when instancing the `TealTester` (see code in [teal_tester.py](./artificial_algorand_contract/classes/teal_tester.py) `TealTester.__init__`,`TealTesterSetting`).

### Algorand Tools

- Class `AlgoAcc` with no arg will create an account on the testnet. The mnemonic words will only show once.
- Create an Algorand Standard Asset (ASA) with [asset.py](./artificial_algorand_contract/classes/asset.py)

## Contribute

- Use `poetry add` to add a package.

See TODOs and more in [CONTRIBUTE.md](./docs/CONTRUBUTE.md)
