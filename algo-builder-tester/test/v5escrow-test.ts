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

describe.only("ART-aUSD mint/redeem smart contract", function () {
  //   useFixture("stateful");
  const fee = 1000;
  const minBalance = 1e6;

  let appID: number;
  let runtime: Runtime;
  let lsig: LogicSigAccount;
  let admin = new AccountStore(BigInt(minBalance + fee));
  let alice = new AccountStore(BigInt(minBalance + fee));
  let bob = new AccountStore(BigInt(minBalance + fee));
  /* HELPERS */

  function syncAccounts() {
    admin = runtime.getAccount(admin.address);
    alice = runtime.getAccount(alice.address);
    bob = runtime.getAccount(bob.address);
  }


  this.beforeAll(function () {
    runtime = new Runtime([admin, alice, bob]);
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
    runtime.optInToApp(bob.address, appID, {}, {});

    syncAccounts();
    // create asset
  });

  function createAssets() {
    syncAccounts();
    const ART = runtime.deployASA('$ART$', {
      creator:
      {
        ...admin.account,
        name: "art-creator"
      }
    })
    const aUSD = runtime.deployASA('aUSD', {
      creator:
      {
        ...admin.account,
        name: "aUSD-creator"
      }
    })
    const adminAssets = admin.createdAssets;
    const artID = ART.assetID
    const usdID = aUSD.assetID
    return { adminAssets, artID, usdID }
  }

  describe("related ASA", function () {
    it("asset creation", function () {
      const { adminAssets, artID, usdID } = createAssets()
      syncAccounts();
      assert.isTrue(adminAssets.has(artID) && adminAssets.has(usdID));
    })
  })

  describe("mint smart contract", function () {
    it("test initial global states", function () {
      syncAccounts();
      const sumEscrowed = admin.getGlobalState(appID, "+$ART$");
      const sumIssued = admin.getGlobalState(appID, "+aUSD");
      const initCRN = admin.getGlobalState(appID, "CRN");
      assert.isDefined(sumEscrowed);
      assert.isDefined(sumIssued);
      assert.isDefined(initCRN);
      assert.equal(sumEscrowed, 0n);
      assert.equal(sumIssued, 0n);
      assert.equal(initCRN, 5n << 32n);
    });

    it.skip("escrow 100 art to mint 20 aUSD", function () {
      syncAccounts();
      const txParams: types.AppCallsParam = {
        type: types.TransactionType.CallApp,
        sign: types.SignType.SecretKey,
        fromAccount: alice.account,
        appID: appID,
        payFlags: { totalFee: fee },
        appArgs: ['str:escrow', 'int:100']
      }; // variable hoisting?

      runtime.executeTx(txParams);
      // runtime.getAccount(john.address).createdApps.forEach((app: any) => { console.log(app); }); // DEV_LOG_TO_REMOVE
      const globalCounter = runtime.getGlobalState(appID, ASSET_SUM);
      assert.equal(globalCounter, 1n);
    });
  });

});