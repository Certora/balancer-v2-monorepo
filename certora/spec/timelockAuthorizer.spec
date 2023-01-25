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

    EVERYWHERE() returns(address) envfree
    _isPermissionGranted(bytes32) returns(bool) envfree
    getPermissionId(bytes32, address, address) returns(bytes32) envfree
    _root() returns(address) envfree
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

    permission1 = getPermissionId(actionId1, account1, where1);
    permission2 = getPermissionId(actionId2, account2, where2);

    assert (actionId1 != actionId2 || account1 != account2 || where1 != where2) => permission1 != permission2;
}


// STATUS - in progress (wating for dispatcher fix https://vaas-stg.certora.com/output/3106/c3db9b875e134fa4b41f807e4e3e6631/?anonymousKey=3b4a38924e9079133b83f39f60cb9c15d4cbcb16)
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
// STATUS - in progress
// All the time there is only one address, that has root permissions and this address is currentRoot.
invariant theOnlyRoot(bytes32 actionId, address account1, address account2, address where)
    (EVERYWHERE() == where 
        && _isPermissionGranted(getPermissionId(actionId, account1, where)) 
        && _isPermissionGranted(getPermissionId(actionId, account2, where)))
    => account1 == account2 && account1 == _root()

// fucntion cancel can be called by root, then msg.sender is a root.


// go over array, two the same action IDs, id with lower index should have lower or equal executableAt
