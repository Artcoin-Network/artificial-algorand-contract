import { AccountStore, Runtime, types as typesRT } from '@algo-builder/runtime';
import { parsing, types as typesW } from '@algo-builder/web';

import { LogicSigAccount } from "algosdk";
import { assert } from 'chai';

/* GENERAL HELPER FUNCTIONS */
const decoder = new TextDecoder("utf-8");
const u8a2Str = (u8a: Uint8Array) => decoder.decode(u8a);
// Uint8Array to Hex string
const u8a2Hex = (u8a: Uint8Array) => {
  return Array.from(u8a).map(b => b.toString(16).padStart(2, '0')).join(' ');
}
// Uint8Array to Dec string
const u8a2Dec = (u8a: Uint8Array) => {
  return Array.from(u8a).map(b => b.toString(10).padStart(2, '0')).join(' ');
}
// Buffer to Hex string
const buf2Hex = (buf: Buffer) => {
  return Array.from(buf).map(b => b.toString(16).padStart(2, '0')).join(' ');
}
// ArrayBuffer to Hex string
const ab2Hex = (ab: ArrayBuffer) => {
  return Array.from(new Uint8Array(ab)).map(b => b.toString(16).padStart(2, '0')).join(' ');
}

// TODO:chore: Wrap u8a2Str(alice.getLocalState(appID, "last_msg") as Uint8Array) to a function.
// TODO: make sure that these are the same as in the contract. should load from env file.
// TODO: OptIn to ASA when OptIn App (in SC)
const ASSET_NAME = "$ART$"
const STABLE_NAME = "aUSD"
const ASSET_SUM = "+$ART$"
const STABLE_SUM = "+aUSD"
const runtime_config = {
  approvalProgramFileName: "escrow-approval.teal",
  clearProgramFileName: "escrow-clear.teal",
}

describe.only("ART-aUSD mint/redeem smart contract", function () {
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
    }
    console.log('addresses used in this test : ', _addresses);
    // create asset
    createAssets()
  });

  function createAssets() { // also dispense.
    syncAccounts();
    const ART = runtime.deployASA(ASSET_NAME, {
      creator:
      {
        ...admin.account,
        name: "$ART$-creator"
      }
    })
    const aUSD = runtime.deployASA(STABLE_NAME, {
      creator:
      {
        ...admin.account,
        name: "aUSD-creator"
      }
    })
    artID = ART.assetID
    usdID = aUSD.assetID

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
    }
    dispenseTxParams.toAccountAddr = alice.address;
    runtime.executeTx(dispenseTxParams);
    dispenseTxParams.toAccountAddr = billy.address;
    runtime.executeTx(dispenseTxParams);
  }

  describe("related ASA", function () {
    it("asset creation and dispense", function () {
      const adminAssets = admin.createdAssets;
      syncAccounts();
      assert.isTrue(adminAssets.has(artID) && adminAssets.has(usdID));
      // dispensed 1k $ART$ to alice and billy 
      assert.equal(1000n, alice.assets.get(artID)!['amount']!);
      assert.equal(1000n, billy.assets.get(artID)!['amount']!);
      // from admin was $ART$ dispensed
      assert.equal(999999998000n, admin.assets.get(artID)!['amount']!);
    })

    it("Asset transfer", function () {
      syncAccounts();
      assert.equal(1000n, alice.assets.get(artID)!['amount']!);
      assert.equal(1000n, billy.assets.get(artID)!['amount']!);
      const artPayTxParams: typesW.AssetTransferParam = {
        type: typesW.TransactionType.TransferAsset,
        sign: typesW.SignType.SecretKey,
        assetID: artID, // passing asa name is also supported
        amount: 100,
        fromAccount: alice.account,
        toAccountAddr: billy.address,
        payFlags: { totalFee: fee },
      }
      const receipt = runtime.executeTx(artPayTxParams) as typesRT.TxReceipt;
      console.log('receipt : ', receipt); // DEV_LOG_TO_REMOVE
      console.log('receipt.txn.snd : ', receipt.txn.snd); // DEV_LOG_TO_REMOVE
      assert.equal(buf2Hex(receipt.txn.snd), u8a2Hex(parsing.addressToPk(alice.address)))
      assert.equal(buf2Hex(receipt.txn.arcv!), u8a2Hex(parsing.addressToPk(billy.address)))
      assert.equal(ab2Hex(receipt.txn.snd.buffer.slice(0, 32)), buf2Hex(receipt.txn.arcv!)) // Why??
      assert.equal(ab2Hex(receipt.txn.arcv!.buffer), ab2Hex(receipt.txn.snd.buffer)) // Why??
      // receipt.txn.snd.buffer seems to be the same as receipt.txn.arcv!.buffer
      syncAccounts();
      assert.equal(900n, alice.assets.get(artID)!['amount']!);
      assert.equal(1100n, billy.assets.get(artID)!['amount']!);
    })

  })

  describe.only("mint smart contract", function () {
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
      const last_msg: Uint8Array = alice.getLocalState(appID, "last_msg") as Uint8Array;
      assert.equal(u8a2Str(last_msg), "OptIn OK.");
    });

    it.only("escrow 100 art to mint 20 aUSD", function () {
      // const adminAssets = admin.createdAssets;
      // assert.isTrue(adminAssets.has(artID) && adminAssets.has(usdID));
      syncAccounts();

      const mintCallParams: typesW.AppCallsParam = {
        type: typesW.TransactionType.CallApp,
        sign: typesW.SignType.SecretKey,
        fromAccount: alice.account,
        appID: appID,
        payFlags: { totalFee: fee },
        appArgs: ['str:mint']
      };

      const mintPayTxParams: typesW.AssetTransferParam = {
        type: typesW.TransactionType.TransferAsset,
        sign: typesW.SignType.SecretKey,
        assetID: artID,
        amount: 100,
        fromAccount: alice.account,
        toAccountAddr: admin.address,
        payFlags: { totalFee: fee },
      }

      syncAccounts();
      assert.equal(1000n, alice.assets.get(artID)!['amount']!);
      assert.equal(999999998000n, admin.assets.get(artID)!['amount']!);
      const receipt = runtime.executeTx([mintCallParams, mintPayTxParams]);
      console.log('receipt : ', receipt); // DEV_LOG_TO_REMOVE
      syncAccounts();
      assert.equal(900n, alice.assets.get(artID)!['amount']!);
      assert.equal(999999998100n, admin.assets.get(artID)!['amount']!);

      syncAccounts();
      const last_msg = u8a2Str(alice.getLocalState(appID, "last_msg") as Uint8Array)
      console.log('last_msg :', last_msg); // DEV_LOG_TO_REMOVE
      const aliceAsset = alice.getLocalState(appID, ASSET_NAME);
      console.log('aliceAsset : ', aliceAsset); // DEV_LOG_TO_REMOVE


    });
  });

});