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

  let runtime: Runtime;
  let lsig: LogicSigAccount;

  this.beforeAll(function () {
    runtime = new Runtime([master, alice, bob]);
    const { approvalProgramFileName,
      clearProgramFileName,
    } = runtime_config;
    // deploy a new app
    txParams.appID = runtime.deployApp(
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
    runtime.optInToApp(master.address, txParams.appID, {}, {});
    runtime.optInToApp(alice.address, txParams.appID, {}, {});
    runtime.optInToApp(bob.address, txParams.appID, {}, {});
  });

  const txParams: types.AppCallsParam = {
    type: types.TransactionType.CallApp,
    sign: types.SignType.SecretKey,
    fromAccount: alice.account,
    appID: 0,
    payFlags: { totalFee: fee },
    appArgs: undefined as undefined | Array<Uint8Array | string>,
  }; // variable hoisting?

  it.only("should initialize global ASSET_SUM to 0 after opt-in", function () {
    const masterGlobal = runtime.getAccount(master.address).getGlobalState(txParams.appID, "+$ART$");
    assert.isDefined(masterGlobal);
    assert.equal(masterGlobal, 0n);

  });
  it.only("should initialize global ASSET_SUM to 0 after opt-in", function () {
    // console.log('global-state : ', runtime.getApp(txParams.appID)['global-state']); // DEV_LOG_TO_REMOVE
    const aliceGlobal = runtime.getAccount(alice.address).getGlobalState(txParams.appID, "+$ART$");
    assert.isDefined(aliceGlobal);
    assert.equal(aliceGlobal, 0n);
  });




  it("should set global counter to 1 after first call", function () {
    txParams.appArgs = [new Uint8Array(Buffer.from('Add'))] // not in docs, algo-builder-tester/node_modules/@algo-builder/web/build/types.d.ts
    runtime.executeTx(txParams);
    // runtime.getAccount(john.address).createdApps.forEach((app: any) => { console.log(app); }); // DEV_LOG_TO_REMOVE
    const globalCounter = runtime.getGlobalState(txParams.appID, ASSET_SUM);
    assert.equal(globalCounter, 1n);
  });

  it("should update counter by +1 for both global and local states on second call", function () {
    const globalCounter = runtime.getGlobalState(txParams.appID, ASSET_SUM) as bigint;
    assert.isDefined(globalCounter)

    // const localCounter = runtime.getAccount(john.address).getLocalState(txParams.appID, ASSET_SUM);

    // verify that both counters are set to 1 (by the previous test)
    assert.equal(globalCounter, 1n);
    // assert.equal(localCounter, 1n);

    runtime.executeTx(txParams);

    // after execution the counters should be updated by +1
    const newGlobalCounter = runtime.getGlobalState(txParams.appID, ASSET_SUM);
    // const newLocalCounter = runtime.getAccount(john.address).getLocalState(txParams.appID, key);

    assert.equal(newGlobalCounter, globalCounter + 1n);
    // assert.equal(newLocalCounter, localCounter + 1n);
  });
});