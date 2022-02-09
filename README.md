## DEV Resources

## installation

- python venv with [poetry](https://python-poetry.org/) `poetry shell`. [Poetry Install Guide](https://python-poetry.org/docs/master/#installing-with-the-official-installer)
- [ ] use artificial-dev-console
- [ ] use [symmetric-secrete-share](https://github.com/PabloLION/symmetric-secrete-share)
- [ ] TODO: finish docs on these two.

  ```shellscript
  python3 -m venv algovenv
  source algovenv/bin/activate
  # should see (algovenv) in the terminal after this
  pip install py-algorand-sdk pyteal
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

| Package           | Version |
| ----------------- | ------- |
| black             | 21.12b0 |
| cffi              | 1.15.0  |
| click             | 8.0.3   |
| msgpack           | 1.0.3   |
| mypy-extensions   | 0.4.3   |
| pathspec          | 0.9.0   |
| pip               | 21.3.1  |
| platformdirs      | 2.4.0   |
| py-algorand-sdk   | 1.8.0   |
| pycparser         | 2.21    |
| pycryptodomex     | 3.12.0  |
| PyNaCl            | 1.4.0   |
| pyteal            | 0.9.1   |
| setuptools        | 59.0.1  |
| six               | 1.16.0  |
| tomli             | 1.2.3   |
| typing_extensions | 4.0.1   |
