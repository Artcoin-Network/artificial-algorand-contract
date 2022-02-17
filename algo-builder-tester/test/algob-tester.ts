import { AccountStore, Runtime, getProgram } from "@algo-builder/runtime";
import { mkTxParams, types } from "@algo-builder/web";

import { LogicSigAccount } from "algosdk";
import { assert } from "chai";

const adminBalance = BigInt(1e8);
const fee = 1e3;
describe.only('algob-tester', function () {
  let admin = new AccountStore(adminBalance);
  let alice = new AccountStore(adminBalance);
  let billy = new AccountStore(adminBalance);
  let runtime: Runtime;
  let appID: number;
  let lsig: LogicSigAccount;
  const runtime_config = {
    approvalProgramFileName: "algob-tester.py",
    clearProgramFileName: "escrow-clear.teal",
  }

  function syncAccounts() {
    admin = runtime.getAccount(admin.address);
    alice = runtime.getAccount(alice.address);
    billy = runtime.getAccount(billy.address);
  }

  this.beforeAll(function () {
    runtime = new Runtime([admin, alice, billy]);
    syncAccounts()
    const { approvalProgramFileName,
      clearProgramFileName,
    } = runtime_config;
    // deploy a new app
    appID = runtime.deployApp(
      approvalProgramFileName,
      clearProgramFileName,
      {
        sender: admin.account,
        globalBytes: 1,
        globalInts: 3,
        localBytes: 1,
        localInts: 2
      },
      {}
    ).appID; // This number is always 9

    // opt-in to the app
    runtime.optInToApp(admin.address, appID, {}, {});
    runtime.optInToApp(alice.address, appID, {}, {});
    runtime.optInToApp(billy.address, appID, {}, {});

  })
  it('algob tester', function () {

    const callAppParams: types.AppCallsParam = {
      type: types.TransactionType.CallApp,
      sign: types.SignType.SecretKey,
      fromAccount: alice.account,
      appID: appID,
      payFlags: { totalFee: fee },
      appArgs: ['str:escrow', 'int:100']
    };

    const escrowTxParams: types.AlgoTransferParam = {
      type: types.TransactionType.TransferAlgo,
      sign: types.SignType.SecretKey,
      fromAccount: admin.account,
      payFlags: { totalFee: fee },
      toAccountAddr: admin.address,
      amountMicroAlgos: BigInt(1e3),
    }

    runtime.executeTx(callAppParams);
    // runtime.executeTx([callAppParams, escrowTxParams]);


  })
})