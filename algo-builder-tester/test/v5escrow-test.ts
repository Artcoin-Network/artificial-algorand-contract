import { AccountStore, Runtime } from '@algo-builder/runtime';

import { LogicSigAccount } from "algosdk";
import { assert } from 'chai';
import { types } from '@algo-builder/web';

//  TODO: make sure that these are the same as in the contract. should load from env file.
const ASSET_NAME = "$ART$"
const STABLE_NAME = "aUSD"

describe.only("Algorand Smart Contracts - Stateful Counter example", function () {
  //   useFixture("stateful");
  const fee = 1000;
  const minBalance = 1e6;
  const master: AccountStore = new AccountStore(BigInt(minBalance + fee));
  const alice = new AccountStore(BigInt(minBalance + fee));
  const bob = new AccountStore(BigInt(minBalance + fee));
  let fundReceiver: AccountStore;

  let runtime: Runtime;
  let lsig: LogicSigAccount;

  const txParams: types.AppCallsParam = {
    type: types.TransactionType.CallApp,
    sign: types.SignType.SecretKey,
    fromAccount: alice.account,
    appID: 0,
    payFlags: { totalFee: fee },
    appArgs: undefined as undefined | Array<Uint8Array | string>,
  };

  let approvalProgramFileName: string;
  let clearProgramFileName: string;

  this.beforeAll(function () {
    runtime = new Runtime([master, fundReceiver]);

    // lsig = runtime.createLsigAccount(, []);
    lsig.sign(master.account.sk);
    runtime.executeTx(txParams);


    runtime = new Runtime([alice]); // setup test
    approvalProgramFileName = 'approval.teal'; // doesn't support `folder/approval`(will parse as full name).
    clearProgramFileName = 'clear.teal'; // have to rename file. So I changed Py Exporter/TealPackage class.

    // deploy a new app
    txParams.appID = runtime.deployApp(
      approvalProgramFileName,
      clearProgramFileName,
      {
        sender: master.account,
        globalBytes: 2,
        globalInts: 1,
        localBytes: 3,
        localInts: 1
      },
      {}
    ).appID; // This number is always 9

    // opt-in to the app
    runtime.optInToApp(master.address, txParams.appID, {}, {});
    runtime.optInToApp(alice.address, txParams.appID, {}, {});
    runtime.optInToApp(bob.address, txParams.appID, {}, {});
  });

  const key = "Count";

  it("should initialize local counter to 0 after opt-in", function () {
    const globalCounter = runtime.getAccount(alice.address).getGlobalState(txParams.appID, key); // get local value from john account
    // console.log('globalCounter : ', globalCounter); // DEV_LOG_TO_REMOVE
    assert.isDefined(globalCounter); // there should be a value present in local state with key "counter"
    (globalCounter)
    assert.equal(globalCounter, 0n);
  });


  it("should set global counter to 1 after first call", function () {
    txParams.appArgs = [new Uint8Array(Buffer.from('Add'))] // not in docs, algo-builder-tester/node_modules/@algo-builder/web/build/types.d.ts
    runtime.executeTx(txParams);
    // runtime.getAccount(john.address).createdApps.forEach((app: any) => { console.log(app); }); // DEV_LOG_TO_REMOVE
    const globalCounter = runtime.getGlobalState(txParams.appID, key);
    assert.equal(globalCounter, 1n);
  });

  it("should update counter by +1 for both global and local states on second call", function () {
    const globalCounter = runtime.getGlobalState(txParams.appID, key) as bigint;
    assert.isDefined(globalCounter)

    // const localCounter = runtime.getAccount(john.address).getLocalState(txParams.appID, key);

    // verify that both counters are set to 1 (by the previous test)
    assert.equal(globalCounter, 1n);
    // assert.equal(localCounter, 1n);

    runtime.executeTx(txParams);

    // after execution the counters should be updated by +1
    const newGlobalCounter = runtime.getGlobalState(txParams.appID, key);
    // const newLocalCounter = runtime.getAccount(john.address).getLocalState(txParams.appID, key);

    assert.equal(newGlobalCounter, globalCounter + 1n);
    // assert.equal(newLocalCounter, localCounter + 1n);
  });
});