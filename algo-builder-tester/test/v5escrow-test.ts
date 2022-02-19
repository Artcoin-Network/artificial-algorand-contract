import { AccountStore, Runtime } from '@algo-builder/runtime';
import { parsing, types } from '@algo-builder/web';

import { LogicSigAccount } from "algosdk";
import { assert } from 'chai';

const decoder = new TextDecoder("utf-8");
const u8a2Str = (u8a: Uint8Array) => decoder.decode(u8a);
// TODO:chore: Wrap u8a2Str(alice.getLocalState(appID, "last_msg") as Uint8Array) to a function.
// TODO: make sure that these are the same as in the contract. should load from env file.
const ASSET_NAME = "$ART$"
const STABLE_NAME = "aUSD"
const ASSET_SUM = "+$ART$"
const STABLE_SUM = "+aUSD"
const runtime_config = {
  approvalProgramFileName: "escrow-approval.teal",
  clearProgramFileName: "escrow-clear.teal",
}

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
      alice_addr: alice.address,
      billy_addr: billy.address
    }
    console.log('addresses used in this test : ', _addresses);

    // create asset
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
    const adminAssets = admin.createdAssets;
    artID = ART.assetID
    usdID = aUSD.assetID

    // opt-in to the asa with alice and billy
    runtime.optIntoASA(artID, alice.address, {});
    runtime.optIntoASA(artID, billy.address, {});
    runtime.optIntoASA(usdID, alice.address, {});
    runtime.optIntoASA(usdID, billy.address, {});

    // TODO:ref: split to another function that calls this one.
    // dispense 1k $ART$ to each alice and billy
    syncAccounts();
    const dispenseTxParams: types.AssetTransferParam = {
      type: types.TransactionType.TransferAsset,
      sign: types.SignType.SecretKey,
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

    return { adminAssets }
  }

  describe("related ASA", function () {
    it("asset creation and dispense", function () {
      const { adminAssets } = createAssets()
      syncAccounts();
      assert.isTrue(adminAssets.has(artID) && adminAssets.has(usdID));
      // dispensed 1k $ART$ to alice and billy 
      assert.equal(1000n, alice.assets.get(artID)!['amount']!);
      assert.equal(1000n, billy.assets.get(artID)!['amount']!);
    })
  })

  describe.only("mint smart contract", function () {
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

    it("assert alice opted in", function () {
      syncAccounts();
      const last_msg: Uint8Array = alice.getLocalState(appID, "last_msg") as Uint8Array;
      assert.equal(u8a2Str(last_msg), "OptIn OK.");
    });

    it.skip("escrow 100 art to mint 20 aUSD", function () {
      const { adminAssets } = createAssets()
      syncAccounts();
      assert.isTrue(adminAssets.has(artID) && adminAssets.has(usdID));
      console.log('last_msg :', u8a2Str(alice.getLocalState(appID, "last_msg") as Uint8Array)); // DEV_LOG_TO_REMOVE

      const mintCallParams: types.AppCallsParam = {
        type: types.TransactionType.CallApp,
        sign: types.SignType.SecretKey,
        fromAccount: alice.account,
        appID: appID,
        payFlags: { totalFee: fee },
        appArgs: ['str:mint']
      };

      const mintPayTxParams: types.AssetTransferParam = {
        type: types.TransactionType.TransferAsset,
        sign: types.SignType.SecretKey,
        fromAccount: alice.account,
        assetID: artID,
        payFlags: { totalFee: fee },
        toAccountAddr: admin.address,
        amount: 100,
      }



      runtime.executeTx([mintCallParams, mintPayTxParams]);
      console.log('last_msg : ', (alice.getLocalState(appID, "str:last_msg"))); // DEV_LOG_TO_REMOVE

      const globalCounter = runtime.getGlobalState(appID, ASSET_SUM);
      assert.equal(globalCounter, 1n);
    });
  });

});