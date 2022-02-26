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
const initialAdminUsd = totalUsd - dispensedInit * 2n;
const initialAdminBtc = totalBtc - dispensedInit * 2n;
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

  describe("smart contract basic set up", function () {
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
  });
  describe("buy/sell with smart contract, static price", function () {
    let aliceCallParam: typesW.AppCallsParam;
    let alicePayTxParam: typesW.AssetTransferParam;
    let aliceCollectTxParam: typesW.AssetTransferParam;
    this.beforeEach(function () {
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

    function resetInitStatus() {
      // TODO:: can't "beforeEach" : new describe()
      syncAccounts();
      function setAccountAsset(
        account: AccountStore,
        assetID: number,
        amount: bigint
      ) {
        return (runtime.getAccount(account.address).assets.get(assetID)![
          "amount"
        ]! = amount);
      }
      setAccountAsset(alice, btcID, dispensedInit);
      setAccountAsset(alice, usdID, dispensedInit);
      setAccountAsset(billy, btcID, dispensedInit);
      setAccountAsset(billy, usdID, dispensedInit);
      setAccountAsset(admin, btcID, initialAdminBtc);
      setAccountAsset(admin, usdID, initialAdminUsd);

      assert.equal(dispensedInit, alice.assets.get(usdID)!["amount"]!); // 1k from dispense
      assert.equal(dispensedInit, alice.assets.get(btcID)!["amount"]!); // 1k from dispense
      assert.equal(initialAdminUsd, admin.assets.get(usdID)!["amount"]!); // 2k dispensed
      assert.equal(initialAdminBtc, admin.assets.get(btcID)!["amount"]!); // 2k dispensed
      assert.equal(0n, alice.getLocalState(appID, "AAA_balance")); // holding 0 AAA
    }
    this.beforeEach(resetInitStatus);
    this.afterEach(resetInitStatus);
    it("buy aBTC of 2aUSD ", function () {
      const aUsdPaid = BigInt(2e6); // 2aUSD,
      const aBtcCollected = BigInt(
        Math.floor((Number(aUsdPaid) * 1e8) / 1e6 / 38613.14)
        // trade_contract.py: aBTC_amount/AAA_ATOM_IN_ONE = aUSD_amount/USD_ATOM_IN_ONE/price
        // (aUSD_amount/1e6/price) * 1e8(AAA_decimal) = aBTC_amount
      );
      //  2/38613.14 *10^8 = 5179.58394 -> 5179 smallest units of BTC.
      // console.log("btcCollected : ", btcCollected); // 5179

      /* Transaction */
      aliceCallParam.appArgs = ["str:buy"];
      alicePayTxParam.assetID = usdID;
      alicePayTxParam.amount = aUsdPaid;
      aliceCollectTxParam.assetID = btcID;
      aliceCollectTxParam.amount = aBtcCollected;

      const receipt = runtime.executeTx(
        [aliceCallParam, alicePayTxParam, aliceCollectTxParam],
        0
      );
      // console.log('receipt : ', receipt);

      /* Check status after txn */
      syncAccounts();
      assert.equal(
        dispensedInit - aUsdPaid,
        alice.assets.get(usdID)!["amount"]!
      );
      assert.equal(
        dispensedInit + aBtcCollected,
        alice.assets.get(btcID)!["amount"]!
      );
      assert.equal(aBtcCollected, alice.getLocalState(appID, "AAA_balance")); // minted 200 aUSD Unit

      /* extra of return to initial state */
      runtime.getAccount(alice.address).setLocalState(appID, "AAA_balance", 0n);
    });

    function testSellABtcWithAlice(
      aBtcPaid: bigint,
      aUsdCollected: bigint,
      initialAliceBtc: bigint
    ) {
      runtime
        .getAccount(alice.address)
        .setLocalState(appID, "AAA_balance", initialAliceBtc);

      /* Txn */
      aliceCallParam.appArgs = ["str:sell"];
      alicePayTxParam.assetID = btcID;
      alicePayTxParam.amount = aBtcPaid;
      aliceCollectTxParam.assetID = usdID;
      aliceCollectTxParam.amount = aUsdCollected;

      const receipt = runtime.executeTx([
        aliceCallParam,
        alicePayTxParam,
        aliceCollectTxParam,
      ]);

      /* Check status after txn */
      syncAccounts();
      assert.equal(
        dispensedInit + aUsdCollected,
        alice.assets.get(usdID)!["amount"]!
      );
      assert.equal(
        dispensedInit - aBtcPaid,
        alice.assets.get(btcID)!["amount"]!
      );
      assert.equal(
        initialAliceBtc - aBtcPaid,
        alice.getLocalState(appID, "AAA_balance")
      ); // minted 200 aUSD Unit

      /* extra of return to initial state */
      runtime.getAccount(alice.address).setLocalState(appID, "AAA_balance", 0n);
    }
    it.only("sell 5179e10-8 aBTC (2aUSD)", function () {
      // Here both units of $ART$ and aUSD are the same, 1e-6 (by ASA.decimals).
      const aBtcPaid = 5179n;
      const aUsdCollected = 1999774n;
      /* not 2 aUSD mostly because aBTC rounding (in the buy process) 
      TODO:discuss: should we return this to users?
      2/38613.14 *10^8 = 5179.58394
      fractional part of (5179.58394) = 0.58394
      0.58394*38613.14/10^8 = 0.00022547757
      0.00022547757 + 1.999774 = 1.99999948
      */
      const initialAliceBtc = aBtcPaid;

      testSellABtcWithAlice(aBtcPaid, aUsdCollected, initialAliceBtc);
    });
    it.only("sell>balance would fail, TODO:ref: contract", function () {
      // TODO:discuss: should we assert? :down:
      // The `AAA_balance-aBtcPaid` will actually throw an error(overflow) for being negative;
      const aBtcPaid = 5179n;
      const aUsdCollected = 1999774n;
      const initialAliceBtc = aBtcPaid - 1n;
      assert.throws(() => {
        testSellABtcWithAlice(aBtcPaid, aUsdCollected, initialAliceBtc);
      }, "RUNTIME_ERR1007: Teal code rejected by logic");

      /* extra of return to initial state */
      runtime.getAccount(alice.address).setLocalState(appID, "AAA_balance", 0n);
    });
    it.only("throws error if not 3 transactions.", function () {
      aliceCallParam.appArgs = ["str:sell"];
      alicePayTxParam.assetID = btcID;
      alicePayTxParam.amount = 0n;
      aliceCollectTxParam.assetID = usdID;
      aliceCollectTxParam.amount = 0n;

      assert.throws(() => runtime.executeTx([aliceCallParam, aliceCallParam])); // not 3 transactions
      // "RUNTIME_ERR1007: Teal code rejected by logic"
      assert.throws(() =>
        runtime.executeTx([
          aliceCallParam,
          aliceCallParam,
          aliceCallParam,
          aliceCallParam,
        ])
      ); // not 3 transactions
      // "RUNTIME_ERR1007: Teal code rejected by logic"
    });
    it.only("throws error 3 transactions are not Call,Pay,Collect.", function () {
      aliceCallParam.appArgs = ["str:sell"];
      alicePayTxParam.assetID = btcID;
      alicePayTxParam.amount = 0n;
      aliceCollectTxParam.assetID = usdID;
      aliceCollectTxParam.amount = 0n;

      assert.throws(() =>
        runtime.executeTx([aliceCallParam, alicePayTxParam, alicePayTxParam])
      ); // not Call,Pay,Collect
      // "RUNTIME_ERR1007: Teal code rejected by logic" PyTeal.Assert fail different than this.
      // "RUNTIME_ERR1009: TEAL runtime encountered err opcode at line 144"
      // TODO:discuss: should we use Assert, Return Fail, or someway to debug Teal for further dev?
      assert.throws(() =>
        runtime.executeTx([
          aliceCallParam,
          aliceCollectTxParam,
          aliceCollectTxParam,
        ])
      ); // not Call,Pay,Collect
      // "RUNTIME_ERR1007: Teal code rejected by logic"

      alicePayTxParam.assetID = usdID;

      assert.throws(() =>
        runtime.executeTx([
          aliceCallParam,
          alicePayTxParam,
          aliceCollectTxParam,
        ])
      ); // Not paying aBTC
    });
  });
});
