interface ExchangeInterface {
  atfPrice: number;
  aEthPrice: number;
  stakedAtfVal: number;
  issuedAssetVal: number;
  CCR: number;
  users: ExUser[];
}

class ExUser {
  atf: number;
  stakedATF: number;
  aUsd: number;
  aEth: number;
  CCR: number;
  ex: Exchange;
  constructor(atf: number, aEth: number, aUsd: number) {
    this.atf = atf;
    this.aEth = aEth;
    this.aUsd = aUsd;
    this.CCR = 5;
  }
  joinEx(ex: Exchange) {
    ex.users.push(this);
    this.ex = ex;
  }
  topUpATF(amount: number) {
    this.atf += amount;
  }
  mint(atf: number) {
    this.atf -= atf;
    this.stakedATF += atf;
    this.ex.stakedAtfVal += atf * this.ex.atfPrice;
    this.aUsd = (atf * this.ex.atfPrice) / 5;
  }
  buyValue(aUsd: number) {
    if (this.aUsd < aUsd) {
      throw new Error("Not enough aUSD");
    }
    this.aUsd -= aUsd;
    this.aEth += aUsd / this.ex.aEthPrice;
  }
}

const Admin: ExUser = new ExUser(100_000, 100, 0);
const ExampleUser = new ExUser(0, 0, 5);
const ExchangeDefaultParams = {
  atfPrice: 10,
  aEthPrice: 2000,
  aAssetValue: 0,
  stakedAtfVal: 0,
  CCR: 5,
  users: [],
};

class Exchange implements ExchangeInterface {
  atfPrice: number;
  aEthPrice: number;
  stakedAtfVal: number;
  issuedAssetVal: number;
  CCR: number;
  users: ExUser[];

  constructor() {
    this.atfPrice = ExchangeDefaultParams.atfPrice;
    this.aEthPrice = ExchangeDefaultParams.aEthPrice;
    this.stakedAtfVal = ExchangeDefaultParams.stakedAtfVal;
    this.issuedAssetVal = ExchangeDefaultParams.aAssetValue;
    this.CCR = ExchangeDefaultParams.CCR;
    this.users = ExchangeDefaultParams.users;
  }

  updateInfo() {
    this.issuedAssetVal = this.users.reduce(
      (acc, user) => acc + user.aUsd + user.aEth * this.aEthPrice,
      0
    );

    this.CCR = this.stakedAtfVal
      ? this.stakedAtfVal / this.issuedAssetVal
      : 100;
  }
  printInfo() {
    console.log(`
      atfPrice: ${this.atfPrice}
      aEthPrice: ${this.aEthPrice}
      stakedAtfVal: ${this.stakedAtfVal}
      issuedAssetVal: ${this.issuedAssetVal}
      users: ${this.users.length}
      CCR: ${this.CCR}`);
  }
  print() {
    this.updateInfo();
    this.printInfo();
  }
}

const ex = new Exchange();
// Admin.joinEx(ex);
ExampleUser.joinEx(ex);
// const admin = ex.users[0];
const alice = ex.users[0];

// Alice mints 100 atf
alice.topUpATF(1000);
alice.mint(1000);
alice.buyValue(2000);
// ex.print();

// ETH price goes down to 1000
ex.aEthPrice = 1000;

// ex.print();
