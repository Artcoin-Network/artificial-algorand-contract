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
        globalInts: 3,
        localBytes: 1,
        localInts: 2,
      },
      {}
    ).appID; // This number is always 9

    // opt-in to the app
    runtime.optInToApp(admin.address, appID, {}, {});
    runtime.optInToApp(alice.address, appID, {}, {});
    runtime.optInToApp(billy.address, appID, {}, {});

    syncAccounts();
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
    console.log("addresses used in this test : ", _addresses);
    // create asset
    createAssets();
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
  }

  describe("related ASA", function () {
    it("Asset creation and dispense", function () {
      const adminAssets = admin.createdAssets;
      syncAccounts();
      assert.isTrue(adminAssets.has(btcID) && adminAssets.has(usdID));
      // dispensed 1k $ART$ to alice and billy
      assert.equal(dispensedInit, alice.assets.get(btcID)!["amount"]!);
      assert.equal(dispensedInit, billy.assets.get(btcID)!["amount"]!);
      assert.equal(dispensedInit, alice.assets.get(usdID)!["amount"]!);
      assert.equal(dispensedInit, billy.assets.get(usdID)!["amount"]!);
      // from admin was $ART$ dispensed
      assert.equal(initialBtc, admin.assets.get(btcID)!["amount"]!);
      assert.equal(initialUsd, admin.assets.get(usdID)!["amount"]!);
    });
  });

  describe("buy/sell with smart contract, static price ", function () {
    let aliceCallParam: typesW.AppCallsParam;
    let alicePayTxParams: typesW.AssetTransferParam;
    let aliceCollectTxParams: typesW.AssetTransferParam;
    this.beforeAll(function () {
      aliceCallParam = {
        type: typesW.TransactionType.CallApp,
        sign: typesW.SignType.SecretKey,
        fromAccount: alice.account,
        appID: appID,
        payFlags: { totalFee: fee },
        appArgs: [],
      };
      alicePayTxParams = {
        type: typesW.TransactionType.TransferAsset,
        sign: typesW.SignType.SecretKey,
        assetID: 0,
        amount: 0,
        fromAccount: alice.account,
        toAccountAddr: admin.address,
        payFlags: { totalFee: fee },
      };
      aliceCollectTxParams = {
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

    it.only("buy 1 btc", function () {
      // Here both units of $ART$ and aUSD are the same, 1e-6 (by ASA.decimals).
      const usdPaid = 100000n; // can be 100 (bigint is not a must)
      // CR unit is 2^-16. 5n next line means 5>>16 * UnitCR.
      const btcCollected = usdPaid; // (num*price/CR)

      aliceCallParam.appArgs = ["str:buy"];
      alicePayTxParams.assetID = usdID;
      alicePayTxParams.amount = usdPaid;
      aliceCollectTxParams.assetID = btcID;
      aliceCollectTxParams.amount = btcCollected;
      /* Check status before txn */
      syncAccounts();
      assert.equal(dispensedInit, alice.assets.get(usdID)!["amount"]!); // 1k from dispense
      assert.equal(dispensedInit, alice.assets.get(btcID)!["amount"]!); // 1k from dispense
      assert.equal(initialUsd, admin.assets.get(usdID)!["amount"]!); // 2k dispensed
      assert.equal(initialBtc, admin.assets.get(btcID)!["amount"]!); // 2k dispensed
      assert.equal(0n, alice.getLocalState(appID, "AAA_balance")); // staked 0 $ART$ Unit

      const receipt = runtime.executeTx([
        aliceCallParam,
        alicePayTxParams,
        aliceCollectTxParams,
      ]);
      // console.log('receipt : ', receipt);

      /* Check status after txn */
      syncAccounts();
      assert.equal(
        dispensedInit - usdPaid,
        alice.assets.get(btcID)!["amount"]!
      );
      assert.equal(999999998100n, admin.assets.get(btcID)!["amount"]!);
      assert.equal(100n, alice.getLocalState(appID, ASSET_NAME)); // staked 100 $ART$ Unit
      assert.equal(200n, alice.getLocalState(appID, STABLE_NAME)); // minted 200 aUSD Unit
      // TODO:ref:#1: should return to the initial state after each test
    });
    it("burn 200 aUSD to redeem 200/10*5 (#aUSD/$ART$price*CR) == 100 $ART$", function () {
      // Here both units of $ART$ and aUSD are the same, 1e-6 (by ASA.decimals).
      const aUsdBurned = 200n;
      const artRedeemed = (aUsdBurned / 10n) * 5n;

      const burnCallParams: typesW.AppCallsParam = {
        type: typesW.TransactionType.CallApp,
        sign: typesW.SignType.SecretKey,
        fromAccount: alice.account,
        appID: appID,
        payFlags: { totalFee: fee },
        appArgs: ["str:burn"],
      }; // TODO:ref: store a basic call params
      const burnPayTxParams: typesW.AssetTransferParam = {
        type: typesW.TransactionType.TransferAsset,
        sign: typesW.SignType.SecretKey,
        assetID: usdID,
        amount: aUsdBurned,
        fromAccount: alice.account,
        toAccountAddr: admin.address,
        payFlags: { totalFee: fee },
      }; // TODO:ref: store a basic transfer params
      const burnCollectTxParams: typesW.AssetTransferParam = {
        type: typesW.TransactionType.TransferAsset,
        sign: typesW.SignType.SecretKey,
        assetID: btcID,
        amount: artRedeemed,
        fromAccount: admin.account,
        toAccountAddr: alice.address,
        payFlags: { totalFee: fee },
      }; // TODO:ref: store a basic transfer params

      /* Check status before txn */

      syncAccounts();
      // TODO:ref:#1: should return to the initial state after each test
      assert.equal(900n, alice.assets.get(btcID)!["amount"]!); // FROM LAST TEST (escrow)
      assert.equal(999999998100n, admin.assets.get(btcID)!["amount"]!); // FROM LAST TEST (escrow)
      assert.equal(100n, alice.getLocalState(appID, ASSET_NAME)); // FROM LAST TEST (escrow)
      assert.equal(200n, alice.getLocalState(appID, STABLE_NAME)); // FROM LAST TEST (escrow)

      const receipt = runtime.executeTx([
        burnCallParams,
        burnPayTxParams,
        burnCollectTxParams,
      ]);
      // console.log('receipt : ', receipt);

      /* Check status after txn */
      syncAccounts();
      assert.equal(1000n, alice.assets.get(btcID)!["amount"]!);
      assert.equal(999999998000n, admin.assets.get(btcID)!["amount"]!);
      assert.equal(0n, alice.getLocalState(appID, ASSET_NAME)); // staked 0 $ART$ Unit
      assert.equal(0n, alice.getLocalState(appID, STABLE_NAME)); // minted 0 aUSD Unit
    });
    it("throws error if not 3 transactions.", function () {
      // Here both units of $ART$ and aUSD are the same, 1e-6 (by ASA.decimals).
      const aUsdBurned = 200n;
      const artRedeemed = (aUsdBurned / 10n) * 5n;

      const burnCallParams: typesW.AppCallsParam = {
        type: typesW.TransactionType.CallApp,
        sign: typesW.SignType.SecretKey,
        fromAccount: alice.account,
        appID: appID,
        payFlags: { totalFee: fee },
        appArgs: ["str:burn"],
      }; // TODO:ref: store a basic call params
      const burnPayTxParams: typesW.AssetTransferParam = {
        type: typesW.TransactionType.TransferAsset,
        sign: typesW.SignType.SecretKey,
        assetID: usdID,
        amount: aUsdBurned,
        fromAccount: alice.account,
        toAccountAddr: admin.address,
        payFlags: { totalFee: fee },
      }; // TODO:ref: store a basic transfer params
      const burnCollectTxParams: typesW.AssetTransferParam = {
        type: typesW.TransactionType.TransferAsset,
        sign: typesW.SignType.SecretKey,
        assetID: btcID,
        amount: artRedeemed,
        fromAccount: admin.account,
        toAccountAddr: alice.address,
        payFlags: { totalFee: fee },
      }; // TODO:ref: store a basic transfer params

      /* Check status before txn */

      assert.throws(
        () => runtime.executeTx([burnCallParams, burnPayTxParams]),
        "RUNTIME_ERR1007: Teal code rejected by logic"
      );
      assert.throws(
        () =>
          runtime.executeTx([
            burnCallParams,
            burnPayTxParams,
            burnCollectTxParams,
            burnCollectTxParams,
          ]),
        "RUNTIME_ERR1007: Teal code rejected by logic"
      );
      // console.log('receipt : ', receipt);
    });
    it("burn>minted would fail", function () {
      // Here both units of $ART$ and aUSD are the same, 1e-6 (by ASA.decimals).
      const artPaid = 100n;
      const aUsdCollected = (artPaid * 10n) / 5n;
      const aUsdBurned = 200n + 1n; // burn 1 unit (1e-6) more aUSD than minted
      const artRedeemed = (aUsdBurned / 10n) * 5n;

      const mintCallParams: typesW.AppCallsParam = {
        type: typesW.TransactionType.CallApp,
        sign: typesW.SignType.SecretKey,
        fromAccount: alice.account,
        appID: appID,
        payFlags: { totalFee: fee },
        appArgs: ["str:mint"],
        // accounts: [admin.address], // :+1L: not working with this method, throwing error
        // foreignAssets: [btcID, usdID], // unsupported type for itxn_submit at line 211, for version 5
      }; // TODO:ref: store a basic call params
      const mintPayTxParams: typesW.AssetTransferParam = {
        type: typesW.TransactionType.TransferAsset,
        sign: typesW.SignType.SecretKey,
        assetID: btcID,
        amount: artPaid,
        fromAccount: alice.account,
        toAccountAddr: admin.address,
        payFlags: { totalFee: fee },
      }; // TODO:ref: store a basic transfer params
      const mintCollectTxParams: typesW.AssetTransferParam = {
        type: typesW.TransactionType.TransferAsset,
        sign: typesW.SignType.SecretKey,
        assetID: usdID,
        amount: aUsdCollected,
        fromAccount: admin.account,
        toAccountAddr: alice.address,
        payFlags: { totalFee: fee },
      }; // TODO:ref: store a basic transfer params
      const burnCallParams: typesW.AppCallsParam = {
        type: typesW.TransactionType.CallApp,
        sign: typesW.SignType.SecretKey,
        fromAccount: alice.account,
        appID: appID,
        payFlags: { totalFee: fee },
        appArgs: ["str:burn"],
      }; // TODO:ref: store a basic call params
      const burnPayTxParams: typesW.AssetTransferParam = {
        type: typesW.TransactionType.TransferAsset,
        sign: typesW.SignType.SecretKey,
        assetID: usdID,
        amount: aUsdBurned,
        fromAccount: alice.account,
        toAccountAddr: admin.address,
        payFlags: { totalFee: fee },
      }; // TODO:ref: store a basic transfer params
      const burnCollectTxParams: typesW.AssetTransferParam = {
        type: typesW.TransactionType.TransferAsset,
        sign: typesW.SignType.SecretKey,
        assetID: btcID,
        amount: artRedeemed,
        fromAccount: admin.account,
        toAccountAddr: alice.address,
        payFlags: { totalFee: fee },
      }; // TODO:ref: store a basic transfer params

      /* Check status before txn */

      const mintReceipt = runtime.executeTx([
        mintCallParams,
        mintPayTxParams,
        mintCollectTxParams,
      ]);
      assert.throws(() => {
        const burnReceipt = runtime.executeTx([
          burnCallParams,
          burnPayTxParams,
          burnCollectTxParams,
        ]);
      }, "RUNTIME_ERR1007: Teal code rejected by logic");
    });
  });
});
