import "erc20.spec"

// using MockVault as MockVault
using Vault as Vault

methods {
    execute(address, bytes) returns(bytes) => DISPATCHER(true)
    getActionId(bytes4) returns(bytes32) => DISPATCHER(true)        // what is the "target/where" in cancel()? "where" in schedule?   setDelay()

    getSchedExeWhere(uint256) returns(address) envfree
    getSchedExeData(uint256) returns(bytes) envfree
    getSchedExeExecuted(uint256) returns(bool) envfree
    getSchedExeCancelled(uint256) returns(bool) envfree
    getSchedExeProtected(uint256) returns(bool) envfree
    getSchedExeExecutableAt(uint256) returns(uint256) envfree
    getSchedExeLength() returns(uint256) envfree
}

rule sanity(env e, method f) {
    calldataarg args;
    f(e, args);
    assert false;
}


// STATUS - verified with workarounds explained on confluence
// Checking that hashing produces different outputs for different inputs
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


// STATUS - in progress
// executableAt is immutable
rule immutableExecuteAt(env e, method f) {
    uint256 actionIndex;

    // require actionIndex < getSchedExeLength();

    uint256 executableAtBefore = getSchedExeExecutableAt(actionIndex);

    calldataarg args;
    f(e, args);

    uint256 executableAtAfter = getSchedExeExecutableAt(actionIndex);

    assert executableAtBefore == executableAtAfter;
}


// STATUS - in progress
// only claimRoot changes root and variables are updated appropriately.
rule rootChangesOnlyWithClaimRoot(env e, method f) {
    address rootBefore = getRoot();
    address pendingRootBefore = getPendingRoot();

    // Invoke any function with msg.sender being the sender account
    calldataarg args;
    f(e, args);

    address rootAfter = getRoot();

    assert rootBefore != rootAfter =>
        e.msg.sender == pendingRootBefore,
        "Root changed by somebody, who was not pending root.";
    assert rootBefore != rootAfter =>
        rootAfter == pendingRootBefore,
        "Pending root changed root to somebody else.";
    assert rootBefore != rootAfter =>
        f.selector == claimRoot().selector,
        "Root changed by a function other than claimRoot.";
}
