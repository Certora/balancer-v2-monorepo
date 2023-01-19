import "erc20.spec"

// using MockVault as MockVault
using Vault as Vault

methods {
    execute(address, bytes) returns(bytes) => DISPATCHER(true)
    getActionId(bytes4) returns(bytes32) => DISPATCHER(true)        // what is the "target/where" in cancel()? "where" in schedule?   setDelay()

    // unresolved calls
    // execute() - dispatcher doesn't work, don't know why
    // cancel() - solved
    // schedule() - solved
    // setDelay() - dispatcher doesn't work, don't know why
}

rule sanity(env e, method f) {
    calldataarg args;
    f(e, args);
    assert false;
}

// STATUS - in progress
rule permissionCheck(env e, env e2) {
    bytes32 actionId1;
    address account1;
    address where1;

    bytes32 actionId2;
    address account2;
    address where2;

    bytes32 permission1;
    bytes32 permission2;

    permission1 = getPermissionId(e, actionId1, account1, where1);
    permission2 = getPermissionId(e, actionId2, account2, where2);

    assert (actionId1 != actionId2 || account1 != account2 || where1 != where2) => permission1 != permission2;
}



// rule whoChangedBalanceOf(env eB, env eF, method f) {
//     address u;
//     calldataarg args;
//     uint256 before = execu(eB, u);
//     f(eF, args);
//     assert balanceOf(eB, u) == before, "balanceOf changed";
// }


// LiquidStakingManager - blocked by bytes array issue
// SaveEthVault - blocked by bytes array issue
// StakingFundsVault - blocked by several issues




