import { AccountStore, Runtime } from '@algo-builder/runtime';

import { LogicSigAccount } from "algosdk";
import { assert } from 'chai';
import { types } from '@algo-builder/web';

//  TODO: make sure that these are the same as in the contract. should load from env file.
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
      admin: admin.address,
      alice: alice.address,
      billy: billy.address
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

  describe("mint smart contract", function () {
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

    it.skip("escrow 100 art to mint 20 aUSD", function () {
      const { adminAssets } = createAssets()
      syncAccounts();
      assert.isTrue(adminAssets.has(artID) && adminAssets.has(usdID));

      const txParams: types.AppCallsParam = {
        type: types.TransactionType.CallApp,
        sign: types.SignType.SecretKey,
        fromAccount: alice.account,
        appID: appID,
        payFlags: { totalFee: fee },
        appArgs: ['str:escrow', 'int:100']
      };

      const escrowTxParams: types.AssetTransferParam = {
        type: types.TransactionType.TransferAsset,
        sign: types.SignType.SecretKey,
        fromAccount: admin.account,
        assetID: artID,
        payFlags: { totalFee: fee },
        toAccountAddr: admin.address,
        amount: 1000,
      }



      runtime.executeTx([txParams, escrowTxParams]);
      const globalCounter = runtime.getGlobalState(appID, ASSET_SUM);
      assert.equal(globalCounter, 1n);
    });
  });

});