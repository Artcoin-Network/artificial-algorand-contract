import { AccountStore, Runtime } from '@algo-builder/runtime';

import { LogicSigAccount } from "algosdk";
import { assert } from 'chai';
import { types } from '@algo-builder/web';

//  TODO: make sure that these are the same as in the contract. should load from env file.
const ASSET_NAME = "$ART$"
const STABLE_NAME = "aUSD"
const ASSET_SUM = "+$ART$"
const STABLE_SUM = "+aUSD"
const runtime_config = {
  approvalProgramFileName: "escrow-approval.teal",
  clearProgramFileName: "escrow-clear.teal",
}

describe.only("Algorand Smart Contracts - Stateful Counter example", function () {
  //   useFixture("stateful");
  const fee = 1000;
  const minBalance = 1e6;
  const master = new AccountStore(BigInt(minBalance + fee));
  const alice = new AccountStore(BigInt(minBalance + fee));
  const bob = new AccountStore(BigInt(minBalance + fee));

  let appID: number;
  let runtime: Runtime;
  let lsig: LogicSigAccount;

  this.beforeAll(function () {
    runtime = new Runtime([master, alice, bob]);
    const { approvalProgramFileName,
      clearProgramFileName,
    } = runtime_config;
    // deploy a new app
    appID = runtime.deployApp(
      approvalProgramFileName,
      clearProgramFileName,
      {
        sender: master.account,
        globalBytes: 1,
        globalInts: 3,
        localBytes: 1,
        localInts: 2
      },
      {}
    ).appID; // This number is always 9

    // opt-in to the app
    runtime.optInToApp(master.address, appID, {}, {});
    runtime.optInToApp(alice.address, appID, {}, {});
    runtime.optInToApp(bob.address, appID, {}, {});

    // create asset
  });


  it("test initial global states", function () {
    const sumEscrowed = runtime.getAccount(master.address).getGlobalState(appID, "+$ART$");
    const sumIssued = runtime.getAccount(master.address).getGlobalState(appID, "+aUSD");
    const initCRN = runtime.getAccount(master.address).getGlobalState(appID, "CRN");
    assert.isDefined(sumEscrowed);
    assert.isDefined(sumIssued);
    assert.isDefined(initCRN);
    assert.equal(sumEscrowed, 0n);
    assert.equal(sumIssued, 0n);
    assert.equal(initCRN, 5n << 32n);
  });

  it("escrow 100 art to mint 20 aUSD", function () {
    const txParams: types.AppCallsParam = {
      type: types.TransactionType.CallApp,
      sign: types.SignType.SecretKey,
      fromAccount: alice.account,
      appID: appID,
      payFlags: { totalFee: fee },
      appArgs: [new Uint8Array(Buffer.from('Add'))]
    }; // variable hoisting?

    runtime.executeTx(txParams);
    // runtime.getAccount(john.address).createdApps.forEach((app: any) => { console.log(app); }); // DEV_LOG_TO_REMOVE
    const globalCounter = runtime.getGlobalState(appID, ASSET_SUM);
    assert.equal(globalCounter, 1n);
  });

});