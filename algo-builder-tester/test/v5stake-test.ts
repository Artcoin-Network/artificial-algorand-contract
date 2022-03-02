import { AccountStore, Runtime, types as typesRT } from "@algo-builder/runtime";
import { parsing, types as typesW } from "@algo-builder/web";

import { LogicSigAccount } from "algosdk";
import { assert } from "chai";

/* GENERAL HELPER FUNCTIONS */
// const decoder = new TextDecoder("utf-8");
// const u8a2Str = (u8a: Uint8Array) => decoder.decode(u8a);
// Uint8Array to string
const u8a2Str = (u8a: Uint8Array) =>
  String.fromCharCode.apply(null, Array.from(u8a));

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
// Buffer to Hex string
const buf2Hex = (buf: Buffer) => {
  return Array.from(buf)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join(" ");
};
// ArrayBuffer to Hex string
const ab2Hex = (ab: ArrayBuffer) => {
  return Array.from(new Uint8Array(ab))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join(" ");
};

// TODO:chore: Wrap u8a2Str(alice.getLocalState(appID, "last_msg") as Uint8Array) to a function.
// TODO: make sure that these are the same as in the contract. should load from env file.
// TODO: OptIn to ASA when OptIn App (in SC)
const ASSET_NAME = "$ART$";
const STABLE_NAME = "aUSD";
const ASSET_SUM = "+$ART$";
const STABLE_SUM = "+aUSD";
const runtime_config = {
  approvalProgramFileName: "stake-approval.teal",
  clearProgramFileName: "stake-clear.teal",
};

describe("ART-aUSD mint/redeem smart contract", function () {
  //   useFixture("stateful");
  const fee = 1000;
  const minBalance = 1e6;

  let appID: number;
  let artID: number;
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
    const ART = runtime.deployASA(ASSET_NAME, {
      creator: {
        ...admin.account,
        name: "$ART$-creator",
      },
    });
    const aUSD = runtime.deployASA(STABLE_NAME, {
      creator: {
        ...admin.account,
        name: "aUSD-creator",
      },
    });
    artID = ART.assetID;
    usdID = aUSD.assetID;

    // opt-in to the asa with alice and billy
    // runtime.optIntoASA(artID, admin.address, {});
    // runtime.optIntoASA(usdID, admin.address, {});
    // creator opts in automatically .
    runtime.optIntoASA(artID, alice.address, {});
    runtime.optIntoASA(usdID, alice.address, {});
    runtime.optIntoASA(artID, billy.address, {});
    runtime.optIntoASA(usdID, billy.address, {});

    // TODO:ref: split to another function that calls this one.
    // dispense 1k $ART$ to each alice and billy
    syncAccounts();
    const dispenseTxParams: typesW.AssetTransferParam = {
      type: typesW.TransactionType.TransferAsset,
      sign: typesW.SignType.SecretKey,
      fromAccount: admin.account,
      assetID: artID,
      payFlags: { totalFee: fee },
      toAccountAddr: admin.address,
      amount: 1000,
    };
    dispenseTxParams.toAccountAddr = alice.address;
    runtime.executeTx(dispenseTxParams);
    dispenseTxParams.toAccountAddr = billy.address;
    runtime.executeTx(dispenseTxParams);
  }

  describe("related ASA", function () {
    it("Asset creation and dispense", function () {
      const adminAssets = admin.createdAssets;
      syncAccounts();
      assert.isTrue(adminAssets.has(artID) && adminAssets.has(usdID));
      // dispensed 1k $ART$ to alice and billy
      assert.equal(1000n, alice.assets.get(artID)!["amount"]!);
      assert.equal(1000n, billy.assets.get(artID)!["amount"]!);
      // from admin was $ART$ dispensed
      assert.equal(999999998000n, admin.assets.get(artID)!["amount"]!);
    });
    it.skip("SKIP:ref:#1(block others, only with ONLY) Asset transfer", function () {
      syncAccounts();
      assert.equal(1000n, alice.assets.get(artID)!["amount"]!);
      assert.equal(1000n, billy.assets.get(artID)!["amount"]!);
      const artPayTxParams: typesW.AssetTransferParam = {
        type: typesW.TransactionType.TransferAsset,
        sign: typesW.SignType.SecretKey,
        assetID: artID, // passing asa name is also supported
        amount: 100,
        fromAccount: alice.account,
        toAccountAddr: billy.address,
        payFlags: { totalFee: fee },
      };
      const receipt = runtime.executeTx(artPayTxParams) as typesRT.TxReceipt;
      // console.log('receipt : ', receipt); // DEV_LOG, for refactor
      // console.log('receipt.txn.snd : ', receipt.txn.snd); // DEV_LOG, for refactor
      // TODO:ref: compare buffer/uint8array https://www.chaijs.com/plugins/chai-bytes/,
      assert.equal(
        buf2Hex(receipt.txn.snd),
        u8a2Hex(parsing.addressToPk(alice.address))
      );
      assert.equal(
        buf2Hex(receipt.txn.arcv!),
        u8a2Hex(parsing.addressToPk(billy.address))
      );
      // assert.equal(ab2Hex(receipt.txn.snd.buffer.slice(0, 32)), buf2Hex(receipt.txn.arcv!)) // Why??
      assert.equal(
        ab2Hex(receipt.txn.arcv!.buffer),
        ab2Hex(receipt.txn.snd.buffer)
      ); // Why??
      // receipt.txn.snd.buffer seems to be the same as receipt.txn.arcv!.buffer
      syncAccounts();
      assert.equal(900n, alice.assets.get(artID)!["amount"]!);
      assert.equal(1100n, billy.assets.get(artID)!["amount"]!);
      // TODO:ref:#1: should return to the initial state after each test
    });
    it("Asset cannot change blank addr(changeable if not-blank)", function () {
      syncAccounts();
      const assetModParams: typesW.AssetModFields = {
        manager: admin.address,
        reserve: admin.address,
      };
      assert.throws(() => {
        admin.modifyAsset(artID, assetModParams);
        const artInfo = runtime.getApp(artID);
        console.log("artInfo : ", artInfo); // DEV_LOG_TO_REMOVE
      }, "RUNTIME_ERR1507: Cannot reset a blank address");
    });
    it.skip("SKIP(block others, only with ONLY) destroy asset", function () {
      syncAccounts();
      admin.destroyAsset(artID);
      assert.throws(() => {
        const artInfo = runtime.getAssetDef(artID);
      }, "Error: RUNTIME_ERR1508: All of the created assets should be in creator's account");
    });
  });

  describe("mint smart contract", function () {
    it("check creator", function () {
      const ASACreator = runtime.getAssetAccount(artID);
      const SCCreator = runtime.getApp(appID).creator;
      assert.equal(ASACreator.address, admin.address);
      assert.equal(SCCreator, admin.address);
    });
    it("test initial global states", function () {
      syncAccounts();
      const sumEscrowed = admin.getGlobalState(appID, ASSET_SUM);
      const sumIssued = admin.getGlobalState(appID, STABLE_SUM);
      const initCRN = admin.getGlobalState(appID, "CRN");
      assert.isDefined(sumEscrowed);
      assert.isDefined(sumIssued);
      assert.isDefined(initCRN);
      assert.equal(sumEscrowed, 0n);
      assert.equal(sumIssued, 0n);
      assert.equal(initCRN, 5n << 32n);
    });
    it("assert alice opted into ASA", function () {
      syncAccounts();
      const last_msg: Uint8Array = alice.getLocalState(
        appID,
        "last_msg"
      ) as Uint8Array;
      assert.equal(u8a2Str(last_msg), "OptIn OK.");
    });
    it("stake 100 $ART$ to mint 100*10/5 (#$ART$*price/CR)== 200 aUSD", function () {
      // Here both units of $ART$ and aUSD are the same, 1e-6 (by ASA.decimals).
      const artPaid = 100n; // can be 100 (bigint is not a must)
      // CR unit is 2^-16. 5n next line means 5>>16 * UnitCR.
      const aUsdCollected = (artPaid * 10n) / 5n; // (num*price/CR)

      const mintCallParams: typesW.AppCallsParam = {
        type: typesW.TransactionType.CallApp,
        sign: typesW.SignType.SecretKey,
        fromAccount: alice.account,
        appID: appID,
        payFlags: { totalFee: fee },
        appArgs: ["str:mint"],
        // accounts: [admin.address], // :+1L: not working with this method, throwing error
        // foreignAssets: [artID, usdID], // unsupported type for itxn_submit at line 211, for version 5
      }; // TODO:ref: store a basic call params
      const mintPayTxParams: typesW.AssetTransferParam = {
        type: typesW.TransactionType.TransferAsset,
        sign: typesW.SignType.SecretKey,
        assetID: artID,
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
      /* Check status before txn */
      syncAccounts();
      assert.equal(1000n, alice.assets.get(artID)!["amount"]!); // 1k from dispense
      assert.equal(999999998000n, admin.assets.get(artID)!["amount"]!); // 2k dispensed
      assert.equal(0n, alice.getLocalState(appID, ASSET_NAME)); // staked 0 $ART$ Unit
      assert.equal(0n, alice.getLocalState(appID, STABLE_NAME)); // minted 0 aUSD Unit

      const receipt = runtime.executeTx([
        mintCallParams,
        mintPayTxParams,
        mintCollectTxParams,
      ]);
      // console.log('receipt : ', receipt);

      /* Check status after txn */
      syncAccounts();
      assert.equal(900n, alice.assets.get(artID)!["amount"]!);
      assert.equal(999999998100n, admin.assets.get(artID)!["amount"]!);
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
        assetID: artID,
        amount: artRedeemed,
        fromAccount: admin.account,
        toAccountAddr: alice.address,
        payFlags: { totalFee: fee },
      }; // TODO:ref: store a basic transfer params

      /* Check status before txn */

      syncAccounts();
      // TODO:ref:#1: should return to the initial state after each test
      assert.equal(900n, alice.assets.get(artID)!["amount"]!); // FROM LAST TEST (stake)
      assert.equal(999999998100n, admin.assets.get(artID)!["amount"]!); // FROM LAST TEST (stake)
      assert.equal(100n, alice.getLocalState(appID, ASSET_NAME)); // FROM LAST TEST (stake)
      assert.equal(200n, alice.getLocalState(appID, STABLE_NAME)); // FROM LAST TEST (stake)

      const receipt = runtime.executeTx([
        burnCallParams,
        burnPayTxParams,
        burnCollectTxParams,
      ]);
      // console.log('receipt : ', receipt);

      /* Check status after txn */
      syncAccounts();
      assert.equal(1000n, alice.assets.get(artID)!["amount"]!);
      assert.equal(999999998000n, admin.assets.get(artID)!["amount"]!);
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
        assetID: artID,
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
        // foreignAssets: [artID, usdID], // unsupported type for itxn_submit at line 211, for version 5
      }; // TODO:ref: store a basic call params
      const mintPayTxParams: typesW.AssetTransferParam = {
        type: typesW.TransactionType.TransferAsset,
        sign: typesW.SignType.SecretKey,
        assetID: artID,
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
        assetID: artID,
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
