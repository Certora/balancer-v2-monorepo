import "erc20.spec"
import "timelockAuthorizerMain.spec"



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
// All the time there is only one address, that has root permissions and this address is currentRoot.
invariant theOnlyRoot(bytes32 actionId, address account1, address account2, address where)
    (EVERYWHERE() == where 
        && _isPermissionGranted(getPermissionId(actionId, account1, where)) 
        && _isPermissionGranted(getPermissionId(actionId, account2, where)))
    => account1 == account2 && account1 == _root()




// fucntion cancel can be called by root, then msg.sender is a root.

// go over array, two the same action IDs, id with lower index should have lower or equal executableAt
