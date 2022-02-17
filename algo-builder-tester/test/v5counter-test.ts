import { AccountStore, Runtime } from '@algo-builder/runtime';
const { types } = require('@algo-builder/web');
const { assert } = require('chai');


describe("Algorand Smart Contracts - Stateful Counter example", function () {
  //   useFixture("stateful");
  const fee = 1000;
  const minBalance = BigInt(1e6);
  const john = new AccountStore(minBalance + BigInt(fee));

  // with `const john = new AccountStore(minBalance + BigInt(fee));` a new acc is created every time.
  // and this account is not on mainnet/testnet/betanet. So, we need to create asset every time. 
  // should wrap the creation in a outer function.
  // const addr = john.address; 
  // console.log('addr : ', addr); // XW2FDQCNDCT2R3CD2ZEUQMQHKAWX54UFUNBGVVHMK3DJU2H5F7UWDFRCUI
  // console.log('addr : ', addr); // DHVYKOECEN6W66DTEDYEWX7S26WYYNY7VS2X2T66RPOWM2X7MV55Z7JNKE

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
    approvalProgramFileName = 'counter-approval.teal'; // doesn't support `folder/approval`(will parse as full name).
    clearProgramFileName = 'counter-clear.teal'; // have to rename file. So I changed Py Exporter/TealPackage class.

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
    // console.log('txParams.appID : ', txParams.appID); // This number is always 9

    // opt-in to the app
    runtime.optInToApp(john.address, txParams.appID, {}, {});
  });

  const key = "Count";

  it("should initialize local counter to 0 after opt-in", function () {
    const globalCounter = runtime.getAccount(john.address).getGlobalState(txParams.appID, key); // get local value from john account
    // console.log('globalCounter : ', globalCounter); // DEV_LOG_TO_REMOVE
    assert.isDefined(globalCounter); // there should be a value present in local state with key "counter"
    (globalCounter)
    assert.equal(globalCounter, 0n);
  });


  it("should set global counter to 1 after first call", function () {
    txParams.appArgs = [new Uint8Array(Buffer.from('Add'))] // not in docs, algo-builder-tester/node_modules/@algo-builder/web/build/types.d.ts 
    // :up: not needed to edit here. can write it in first assignment. with ["str:Add"] 
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