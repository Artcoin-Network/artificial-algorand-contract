## DEV Resources

## Installation

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

## Contribute

- Use `poetry add` to add a package.

See TODOs and more in [CONTRIBUTE.md](./docs/CONTRUBUTE.md)
