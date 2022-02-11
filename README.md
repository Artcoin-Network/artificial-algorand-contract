## DEV Resources

## installation

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

## NEED FIX

`$ART$`: temp asset name.

## Move to contribute

This chapter focus on developing this tool, not using it.

### Observation

#### Algorand

- Python SDK returns a base64 encoded string, JS returns bytes """

### dev log

- [x] remove sensitive data like test account mnemonics before making this repo public
- [x] The purpose of the repo has changed to be only for smart contracts on Algorand blockchain. So should we refactor this repo.
- [ ] Exporter should be a module like py-leet-runner.

### pip list

`pip install py-algorand-sdk pyteal black`
