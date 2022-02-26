import { AccountStore, Runtime, types as typesRT } from "@algo-builder/runtime";
import { parsing, types as typesW } from "@algo-builder/web";

import { LogicSigAccount } from "algosdk";
import { assert } from "chai";

// TEST PARAMS
const runtime_config = {
  approvalProgramFileName: "Bitcoin-approval.teal",
  clearProgramFileName: "Bitcoin-clear.teal",
};
const dispensedInit = BigInt(1e8);
const totalUsd = BigInt(1e18);
const totalBtc = BigInt(1e18);
const initialUsd = totalUsd - dispensedInit * 2n;
const initialBtc = totalBtc - dispensedInit * 2n;
// TODO:ref: should make an aUSD asset and read from there.
const STABLE_NAME = "aUSD";
const ASSET_NAME = "aBTC";
// TODO:ref: these function are repeating v5stake-test.ts
// Uint8Array to Hex string
const u8a2Hex = (u8a: Uint8Array) => {
  return Array.from(u8a)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join(" ");
};
// Uint8Array to Dec string
const u8a2Dec = (u8a: Uint8Array) => {
  return Array.from(u8a)
    .map((b) => b.toString(10).padStart(2, "0"))
    .join(" ");
};
// Uint8Array to string
const u8a2Str = (u8a: Uint8Array) =>
  String.fromCharCode.apply(null, Array.from(u8a));
// array to Uint8Array
const arr2u8a = (arr: number[]) => {
  return Uint8Array.from(arr);
};
describe.only("aUSD-aBTC buy/sell smart contract", function () {
  const fee = 1000;
  const minBalance = 1e6;

  let appID: number;
  let btcID: number;
  let usdID: number;
  let runtime: Runtime;
  let lsig: LogicSigAccount;
  let admin = new AccountStore(BigInt(minBalance + fee));
  let alice = new AccountStore(BigInt(minBalance + fee));
  let billy = new AccountStore(BigInt(minBalance + fee));
  /* HELPERS */

  function syncAccounts() {
    admin = runtime.getAccount(admin.address);
    alice = runtime.getAccount(alice.address);
    billy = runtime.getAccount(billy.address);
  }

  this.beforeAll(function () {
    runtime = new Runtime([admin, alice, billy]);
    const { approvalProgramFileName, clearProgramFileName } = runtime_config;
    // deploy a new app
    appID = runtime.deployApp(
      approvalProgramFileName,
      clearProgramFileName,
      {
        sender: admin.account,
        globalBytes: 1,
        globalInts: 0,
        localBytes: 1,
        localInts: 3,
      },
      {}
    ).appID; // This number is always 9

    // opt-in to the app
    runtime.optInToApp(admin.address, appID, {}, {});
    runtime.optInToApp(alice.address, appID, {}, {});
    runtime.optInToApp(billy.address, appID, {}, {});

    syncAccounts();
    createAssets();

    const _addresses = {
      admin_addr: admin.address,
      admin_pubKDec: u8a2Dec(parsing.addressToPk(admin.address)),
      admin_pubKHex: u8a2Hex(parsing.addressToPk(admin.address)),
      alice_addr: alice.address,
      alice_pubKDec: u8a2Dec(parsing.addressToPk(alice.address)),
      alice_pubKHex: u8a2Hex(parsing.addressToPk(alice.address)),
      billy_addr: billy.address,
      billy_pubKDec: u8a2Dec(parsing.addressToPk(billy.address)),
      billy_pubKHex: u8a2Hex(parsing.addressToPk(billy.address)),
    };
    const _assets = {
      aBTC: btcID,
      aUSD: usdID,
    };
    console.log("addresses used in this test : ", _addresses);
    console.log("asset ID used in this test : ", _assets);
    // create asset
  });

  function createAssets() {
    // also dispense.
    syncAccounts();
    const aBTC = runtime.deployASA(ASSET_NAME, {
      creator: {
        ...admin.account,
        name: "aBTC-creator",
      },
    });
    const aUSD = runtime.deployASA(STABLE_NAME, {
      creator: {
        ...admin.account,
        name: "aUSD-creator",
      },
    });
    btcID = aBTC.assetID;
    usdID = aUSD.assetID;

    // opt-in to the asa with alice and billy
    // runtime.optIntoASA(btcID, admin.address, {});
    // runtime.optIntoASA(usdID, admin.address, {});
    // creator opts in automatically .
    runtime.optIntoASA(btcID, alice.address, {});
    runtime.optIntoASA(usdID, alice.address, {});
    runtime.optIntoASA(btcID, billy.address, {});
    runtime.optIntoASA(usdID, billy.address, {});

    // TODO:ref: split to another function that calls this one.
    // dispense 1k $ART$ to each alice and billy
    syncAccounts();
    const dispenseBtcTxParams: typesW.AssetTransferParam = {
      type: typesW.TransactionType.TransferAsset,
      sign: typesW.SignType.SecretKey,
      fromAccount: admin.account,
      assetID: btcID,
      payFlags: { totalFee: fee },
      toAccountAddr: admin.address,
      amount: dispensedInit, // 1 aBTC
    };
    dispenseBtcTxParams.toAccountAddr = alice.address;
    runtime.executeTx(dispenseBtcTxParams);
    dispenseBtcTxParams.toAccountAddr = billy.address;
    runtime.executeTx(dispenseBtcTxParams);
    const dispenseUsdTxParams: typesW.AssetTransferParam = {
      type: typesW.TransactionType.TransferAsset,
      sign: typesW.SignType.SecretKey,
      fromAccount: admin.account,
      assetID: usdID,
      payFlags: { totalFee: fee },
      toAccountAddr: admin.address,
      amount: dispensedInit, // 1 aBTC
    };
    dispenseUsdTxParams.toAccountAddr = alice.address;
    runtime.executeTx(dispenseUsdTxParams);
    dispenseUsdTxParams.toAccountAddr = billy.address;
    runtime.executeTx(dispenseUsdTxParams);
    return { aBTC, aUSD };
  }

  describe("buy/sell with smart contract, static price ", function () {
    let aliceCallParam: typesW.AppCallsParam;
    let alicePayTxParam: typesW.AssetTransferParam;
    let aliceCollectTxParam: typesW.AssetTransferParam;
    this.beforeAll(function () {
      aliceCallParam = {
        type: typesW.TransactionType.CallApp,
        sign: typesW.SignType.SecretKey,
        fromAccount: alice.account,
        appID: appID,
        payFlags: { totalFee: fee },
        appArgs: [],
      };
      alicePayTxParam = {
        type: typesW.TransactionType.TransferAsset,
        sign: typesW.SignType.SecretKey,
        assetID: 0,
        amount: 0,
        fromAccount: alice.account,
        toAccountAddr: admin.address,
        payFlags: { totalFee: fee },
      };
      aliceCollectTxParam = {
        type: typesW.TransactionType.TransferAsset,
        sign: typesW.SignType.SecretKey,
        assetID: 0,
        amount: 0,
        fromAccount: admin.account,
        toAccountAddr: alice.address,
        payFlags: { totalFee: fee },
      };
    });
    it("check creator", function () {
      const btcCreator = runtime.getAssetAccount(btcID);
      const usdCreator = runtime.getAssetAccount(usdID);
      const SCCreator = runtime.getApp(appID).creator;
      assert.equal(btcCreator.address, admin.address);
      assert.equal(usdCreator.address, admin.address);
      assert.equal(SCCreator, admin.address);
    });
    it("assert alice opted into ASA", function () {
      syncAccounts();
      const last_msg: Uint8Array = alice.getLocalState(
        appID,
        "last_msg"
      ) as Uint8Array;
      assert.equal(u8a2Str(last_msg), "OptIn OK.");
    });
    function assertInitStatus(aliceOut) {
      console.log("not good : "); // DEV_LOG_TO_REMOVE
      console.log("aliceIn.appsLocalState : ", alice.appsLocalState); // DEV_LOG_TO_REMOVE
      console.log("aliceOut.appsLocalState: ", aliceOut.appsLocalState); // DEV_LOG_TO_REMOVE
      // syncAccounts();
      let als2 = alice.getLocalState(appID, "AAA_balance");
      console.log("als2 : ", als2); // DEV_LOG_TO_REMOVE
      assert.equal(0n, als2); // holding 0 AAA
    }
    it.only("buy aBTC of 2aUSD ", function () {
      const usdPaid = BigInt(2e6); // 2aUSD, 2/38613.14 *10^8 = 5179 smallest units of BTC.
      const btcCollected = BigInt(
        Math.floor((Number(usdPaid) * 1e8) / 1e6 / 38613.14)
        // trade_contract.py: aBTC_amount/AAA_ATOM_IN_ONE = aUSD_amount/USD_ATOM_IN_ONE/price
      );
      aliceCallParam.appArgs = ["str:buy"];
      alicePayTxParam.assetID = usdID;
      alicePayTxParam.amount = usdPaid;
      aliceCollectTxParam.assetID = btcID;
      aliceCollectTxParam.amount = btcCollected;

      const receipt = runtime.executeTx(
        [aliceCallParam, alicePayTxParam, aliceCollectTxParam],
        0
      );
      // console.log('receipt : ', receipt);

      /* Check status after txn */
      let als = alice.appsLocalState.get(appID)?.["key-value"];
      console.log("als : ", als); // DEV_LOG_TO_REMOVE

      let nls = alice.setLocalState(appID, "AAA_balance", 0n);
      console.log("nls : ", nls); // DEV_LOG_TO_REMOVE
      assert.equal(0n, alice.getLocalState(appID, "AAA_balance")); // holding 0 AAA
      // syncAccounts();
      let als1 = alice.getLocalState(appID, "AAA_balance");
      console.log("als1 : ", als1); // DEV_LOG_TO_REMOVE
      console.log("good : "); // DEV_LOG_TO_REMOVE
      assertInitStatus(alice);
    });
  });
});
