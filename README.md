## TODO

- [ ] remove sensitive data like test account mnemonics before making this repo public

## DEV Resources

### test accounts

These accounts are on testnet. If they are contaminated by other users, we can always create some new ones.

```plaintext
# Account 1 # this acc has 20 algos
Z2CNMQ6JQQUBEOOJRDHTWVHJX55ZL7CRILNNBICBFY6Q5V7OFDG2IBYVFM
# Account 2 # this acc has 10 algos
CANWUHR4F2JXRSRMCDIAZI6S45HFO25WP4CMCPC2N73IE7K4C6AHFGWE5I
# Account 3 # this acc has 10 algos
S3OJFP27GULY6LVBAQVHPJIPJOZWZHETHIZO5HOU263UHZ7ZF4F6HWDAHU
```

Mnemonics for these accounts.

```python
mnemonic1 = "monster sniff airport silent try this wheat style walnut anchor pond carry air letter sign matrix permit hope sentence canyon faculty strategy spider able indoor"
mnemonic2 = "budget enemy ladder screen meat profit want appear humble village sick blur first wage junk fashion effort around sausage ostrich code airport fix ability shield"
mnemonic3 = "symptom craft quote wisdom jungle debate split happy pause decline jump diet access entire calm cereal come clay crop winter volume release false abandon solve"
```

## installation

- [ ] install sandbox #TODO
- use python venv

  ```shellscript
  python3 -m venv algovenv
  source algovenv/bin/activate
  # should see (algovenv) in the terminal after this
  pip install py-algorand-sdk pyteal
  ```

## pip list

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
