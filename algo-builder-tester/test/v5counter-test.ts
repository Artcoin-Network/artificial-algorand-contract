import { AccountStore, Runtime } from '@algo-builder/runtime';
const { types } = require('@algo-builder/web');
const { assert } = require('chai');


describe("Algorand Smart Contracts - Stateful Counter example", function () {
  //   useFixture("stateful");
  const fee = 1000;
  const minBalance = BigInt(1e6);
  const john = new AccountStore(minBalance + BigInt(fee));

  const txParams = {
    type: types.TransactionType.CallApp,
    sign: types.SignType.SecretKey,
    fromAccount: john.account,
    appID: 0,
    payFlags: { totalFee: fee },
    appArgs: undefined as undefined | Array<Uint8Array | string>,
  };

  let runtime: Runtime;
  let approvalProgramFileName: string;
  let clearProgramFileName: string;

  this.beforeAll(function () {
    runtime = new Runtime([john]); // setup test
    approvalProgramFileName = 'approval.teal';
    clearProgramFileName = 'clear.teal';

    // deploy a new app
    txParams.appID = runtime.deployApp(
      approvalProgramFileName,
      clearProgramFileName,
      {
        sender: john.account,
        globalBytes: 0,
        globalInts: 1,
        localBytes: 0,
        localInts: 0,
      },
      {}
    ).appID;

    // opt-in to the app
    runtime.optInToApp(john.address, txParams.appID, {}, {});
  });

  const key = "Count";
  // describe('inner describe', function () {

  it("should initialize local counter to 0 after opt-in", function () {
    const globalCounter = runtime.getAccount(john.address).getGlobalState(txParams.appID, key); // get local value from john account
    // console.log('globalCounter : ', globalCounter); // DEV_LOG_TO_REMOVE
    assert.isDefined(globalCounter); // there should be a value present in local state with key "counter"
    (globalCounter)
    assert.equal(globalCounter, 0n);
  });


  it("should set global counter to 1 after first call", function () {
    txParams.appArgs = [new Uint8Array(Buffer.from('Add'))] // not in docs
    runtime.executeTx(txParams);
    runtime.getAccount(john.address).createdApps.forEach((app: any) => { console.log(app); }); // DEV_LOG_TO_REMOVE
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
  // });
});