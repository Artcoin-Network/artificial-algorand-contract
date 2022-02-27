import { AccountStore, Runtime, getProgram } from "@algo-builder/runtime";

import { LogicSigAccount } from "algosdk";
import { assert } from "chai";
import { types } from "@algo-builder/web";

const DESCRIPTION = `
TST1, TST2: Test Global.group_size()
`;
const adminBalance = BigInt(1e8);
const fee = 1e3;
describe("algob-tester", function () {
  let admin = new AccountStore(adminBalance);
  let alice = new AccountStore(adminBalance);
  let billy = new AccountStore(adminBalance);
  let runtime: Runtime;
  let appID: number;
  let lsig: LogicSigAccount;
  const runtime_config = {
    approvalProgramFileName: "algob-tester.py",
    clearProgramFileName: "stake-clear.teal",
  };

  function syncAccounts() {
    admin = runtime.getAccount(admin.address);
    alice = runtime.getAccount(alice.address);
    billy = runtime.getAccount(billy.address);
  }

  function fetchGlobalBytes(key: string) {
    syncAccounts();
    return new TextDecoder("utf-8").decode(
      admin.getGlobalState(appID, key) as Uint8Array
    );
  }
  this.beforeAll(function () {
    runtime = new Runtime([admin, alice, billy]);
    syncAccounts();
    const { approvalProgramFileName, clearProgramFileName } = runtime_config;
    // deploy a new app
    appID = runtime.deployApp(
      approvalProgramFileName,
      clearProgramFileName,
      {
        sender: admin.account,
        globalBytes: 2,
        globalInts: 4,
        localBytes: 0,
        localInts: 0,
      },
      {}
    ).appID; // This number is always 9

    // opt-in to the app
    runtime.optInToApp(admin.address, appID, {}, {});
    runtime.optInToApp(alice.address, appID, {}, {});
    runtime.optInToApp(billy.address, appID, {}, {});
  });

  it("TST1: Global.group_size() == Int(1) without JS Array", function () {
    // call the app with one transaction
    const callAppParams: types.AppCallsParam = {
      type: types.TransactionType.CallApp,
      sign: types.SignType.SecretKey,
      fromAccount: alice.account,
      appID: appID,
      payFlags: { totalFee: fee },
    };
    const resetAppParams: types.AppCallsParam = {
      type: types.TransactionType.CallApp,
      sign: types.SignType.SecretKey,
      fromAccount: alice.account,
      appID: appID,
      payFlags: { totalFee: fee },
      appArgs: ["str:reset"],
    }; // TODO:ref: Too many replicas, refactor with beforeEach.
    runtime.executeTx(resetAppParams);
    assert.equal(fetchGlobalBytes("console"), "empty");
    runtime.executeTx(callAppParams);
    // runtime.executeTx([callAppParams, escrowTxParams]);
    assert.equal(fetchGlobalBytes("console"), "group1");
  });
  it("TST2: Global.group_size() == Int(1) with JS Array", function () {
    // call the app with one transaction
    const callAppParams: types.AppCallsParam = {
      type: types.TransactionType.CallApp,
      sign: types.SignType.SecretKey,
      fromAccount: alice.account,
      appID: appID,
      payFlags: { totalFee: fee },
    };
    const resetAppParams: types.AppCallsParam = {
      type: types.TransactionType.CallApp,
      sign: types.SignType.SecretKey,
      fromAccount: alice.account,
      appID: appID,
      payFlags: { totalFee: fee },
      appArgs: ["str:reset"],
    }; // TODO:ref: Too many replicas, refactor with beforeEach.
    runtime.executeTx(resetAppParams);
    assert.equal(fetchGlobalBytes("console"), "empty");
    runtime.executeTx([callAppParams]);
    // runtime.executeTx([callAppParams, escrowTxParams]);
    assert.equal(fetchGlobalBytes("console"), "group1");
  });

  it("TST3: Global.group_size() == Int(1) with JS Array with len3 reject by TEAL", function () {
    const callAppParams: types.AppCallsParam = {
      type: types.TransactionType.CallApp,
      sign: types.SignType.SecretKey,
      fromAccount: alice.account,
      appID: appID,
      payFlags: { totalFee: fee },
    };
    const resetAppParams: types.AppCallsParam = {
      type: types.TransactionType.CallApp,
      sign: types.SignType.SecretKey,
      fromAccount: alice.account,
      appID: appID,
      payFlags: { totalFee: fee },
      appArgs: ["str:reset"],
    }; // TODO:ref: Too many replicas, refactor with beforeEach.
    runtime.executeTx(resetAppParams);
    assert.equal(fetchGlobalBytes("console"), "empty");
    assert.throws(() => {
      runtime.executeTx([callAppParams, callAppParams, callAppParams]);
    }, "RUNTIME_ERR1007: Teal code rejected by logic");
    // runtime.executeTx();
  });
  it("TST4: Global.group_size() == Int(1) with 2 txn", function () {
    const resetAppParams: types.AppCallsParam = {
      type: types.TransactionType.CallApp,
      sign: types.SignType.SecretKey,
      fromAccount: alice.account,
      appID: appID,
      payFlags: { totalFee: fee },
      appArgs: ["str:reset"],
    }; // TODO:ref: Too many replicas, refactor with beforeEach.

    const callAppParams: types.AppCallsParam = {
      type: types.TransactionType.CallApp,
      sign: types.SignType.SecretKey,
      fromAccount: alice.account,
      appID: appID,
      payFlags: { totalFee: fee },
    };

    const escrowTxParams: types.AlgoTransferParam = {
      type: types.TransactionType.TransferAlgo,
      sign: types.SignType.SecretKey,
      fromAccount: admin.account,
      payFlags: { totalFee: fee },
      toAccountAddr: admin.address,
      amountMicroAlgos: BigInt(1e3),
    };
    runtime.executeTx(resetAppParams);
    assert.equal(fetchGlobalBytes("console"), "empty");
    // this didn't call the app
    runtime.executeTx([escrowTxParams, escrowTxParams]);
    assert.equal(fetchGlobalBytes("console"), "empty");
    runtime.executeTx([callAppParams, escrowTxParams]);
    assert.equal(fetchGlobalBytes("console"), "group2");
    runtime.executeTx([callAppParams, callAppParams]);
    assert.equal(fetchGlobalBytes("console"), "group2");
  });

  it("TST5: `Gtxn[0]` and `Txn` are the same", function () {
    const callAppParams: types.AppCallsParam = {
      type: types.TransactionType.CallApp,
      sign: types.SignType.SecretKey,
      fromAccount: alice.account,
      appID: appID,
      payFlags: { totalFee: fee },
      appArgs: [],
    };
    callAppParams.appArgs = ["str:TST5", "str:txn"];
    runtime.executeTx(callAppParams);
    // we've already known that txn can read by gtxn[0] from TST2
    assert.equal(fetchGlobalBytes("console"), "txn>txn");

    callAppParams.appArgs = ["str:TST5", "str:gtxn"];
    runtime.executeTx([callAppParams]); // this is a gtxn, but can read by txn
    assert.equal(fetchGlobalBytes("console"), "gtxn>txn");
    assert.notEqual(fetchGlobalBytes("console"), "gtxn>gtxn");
  });

  // it.skip('TST7: str:str:something', function () {
  it.skip("TST6: PyTeal.Mul is not necessary with `*`?", function () {
    const callAppParams: types.AppCallsParam = {
      type: types.TransactionType.CallApp,
      sign: types.SignType.SecretKey,
      fromAccount: alice.account,
      appID: appID,
      payFlags: { totalFee: fee },
      appArgs: [],
    };
    callAppParams.appArgs = ["str:TST5", "str:txn"];
    runtime.executeTx(callAppParams);
    callAppParams.appArgs = ["str:TST5", "str:gtxn"];
    runtime.executeTx([callAppParams]);
    assert.throws(() => {
      runtime.executeTx([callAppParams]);
    }, "RUNTIME_ERR1007: Teal code rejected by logic");
    // runtime.executeTx();
  });
  it.skip("TST3: Global.group_size() == Int(1) with JS Array, fail with len2", function () {
    const callAppParams: types.AppCallsParam = {
      type: types.TransactionType.CallApp,
      sign: types.SignType.SecretKey,
      fromAccount: alice.account,
      appID: appID,
      payFlags: { totalFee: fee },
      appArgs: ["str:escrow", "int:100"],
    };

    const escrowTxParams: types.AlgoTransferParam = {
      type: types.TransactionType.TransferAlgo,
      sign: types.SignType.SecretKey,
      fromAccount: admin.account,
      payFlags: { totalFee: fee },
      toAccountAddr: admin.address,
      amountMicroAlgos: BigInt(1e3),
    };
    assert.throws(() => {
      runtime.executeTx([callAppParams, escrowTxParams]);
    }, "RUNTIME_ERR1007: Teal code rejected by logic");
    // runtime.executeTx();
  });
});
