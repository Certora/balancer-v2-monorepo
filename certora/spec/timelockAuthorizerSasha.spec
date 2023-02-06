import "erc20.spec"
import "timelockAuthorizerMain.spec"


// STATUS - in progress (strange storage results: https://vaas-stg.certora.com/output/3106/188ba27f84ac4b9286b6d3df5efb6623/?anonymousKey=85ca8fd3448f6f49e55502ed3dda9cac9689ced7)
// executableAt is immutable
rule immutableExecuteAt(env e, method f) {
    uint256 actionIndex;

    uint256 executableAtBefore = getSchedExeExecutableAt(actionIndex);

    calldataarg args;
    f(e, args);

    uint256 executableAtAfter = getSchedExeExecutableAt(actionIndex);

    assert executableAtBefore == executableAtAfter;
}


// STATUS - verified
// (Helper) ensure that two ways to get ID mathc each other (saw before that it didn't, needed to check)
invariant matchingGenralActionIds()
    _GENERAL_GRANT_ACTION_ID() == getExtendedActionId(getActionId(getGrantActionId()), GENERAL_PERMISSION_SPECIFIER())
    && _GENERAL_REVOKE_ACTION_ID() == getExtendedActionId(getActionId(getRevokeActionId()), GENERAL_PERMISSION_SPECIFIER())


// STATUS - in progress (`getActionIdFromArrayIndex` doesn't return differnt values for different indexes, meaybe because of broken encodePacked. Waiting for fix.)
// go over array, two the same action IDs, id with lower index should have lower or equal executableAt
invariant arrayHierarchy(env e, uint256 indexLow, uint256 indexHigh)
    (indexLow < indexHigh
        && getActionIdFromArrayIndex(indexLow) == getActionIdFromArrayIndex(indexHigh)) // always return the same even for different indexes
    => getSchedExeExecutableAt(indexLow) <= getSchedExeExecutableAt(indexHigh)

rule checkGetActionId(env e, method f) {
    uint256 indexLow; uint256 indexHigh;
    calldataarg args;
    f(e, args);
    assert getActionIdFromArrayIndex(indexLow) != getActionIdFromArrayIndex(indexHigh), "Remember, with great power comes great responsibility.";
}

// STATUS - in progress
// All the time there is only one address, that has root permissions and this address is currentRoot.
invariant theOnlyRoot(bytes32 actionId, address account1, address account2)
    (actionId == _GENERAL_GRANT_ACTION_ID()
        || actionId == _GENERAL_REVOKE_ACTION_ID())
    //     && _isPermissionGranted(getPermissionId(actionId, account1, EVERYWHERE())))
    //      && _isPermissionGranted(getPermissionId(actionId, account2, EVERYWHERE())))
    // => account1 == _root()
    // => _isPermissionGranted(getPermissionId(actionId, _root(), EVERYWHERE()))

    {
        preserved {
            requireInvariant matchingGenralActionIds();
        }
    }


// STATUS - in progress
// Only root has root permissions
rule rootRights(env e, method f) {
    bytes32 actionId;
    address accountRand;

    bool isGrantedRootBefore = _isPermissionGranted(getPermissionId(actionId, _root(), EVERYWHERE()));
    bool isGrantedRandBefore = _isPermissionGranted(getPermissionId(actionId, accountRand, EVERYWHERE()));

    require e.msg.sender != _root(); // CAUTION!!!!!! Added for testing. need to check if it's correct
    require currentContract != EVERYWHERE();
    require accountRand != _root();
    require accountRand != _pendingRoot();
    require actionId == _GENERAL_GRANT_ACTION_ID()
            || actionId == _GENERAL_REVOKE_ACTION_ID();
    require isGrantedRootBefore && !isGrantedRandBefore;

    grantpermissionHelper(f, e);

    bool isGrantedRootAfter = _isPermissionGranted(getPermissionId(actionId, _root(), EVERYWHERE()));
    bool isGrantedRandAfter = _isPermissionGranted(getPermissionId(actionId, accountRand, EVERYWHERE()));

    assert !isGrantedRandAfter, "Remember, with great power comes great responsibility.";
}   

function grantpermissionHelper(method f, env e){
    if (f.selector == grantPermissions(bytes32[], address, address[]).selector){
        bytes32[] actionIds;
        address account;
        address[] where;

        require actionIds[0] != _executor();

        grantPermissions(e, actionIds, account, where);
    } else {
        calldataarg args;
        f(e, args);
    }
} 


// STATUS - in progress / verified / error / timeout / etc.
// only one flag executed/cancelled can be changed at a time
rule executeCancelOnlyOne(env e, method f) {
    uint256 actionIndex1; uint256 actionIndex2;
    bool isExecuted1Before = getSchedExeExecuted(actionIndex1);
    bool isExecuted2Before = getSchedExeExecuted(actionIndex2);
    bool isCancelled1Before = getSchedExeCancelled(actionIndex1);
    bool isCancelled2Before = getSchedExeCancelled(actionIndex2);

    require actionIndex1 != actionIndex2;

    calldataarg args;
    f(e, args);

    bool isExecuted1After = getSchedExeExecuted(actionIndex1);
    bool isExecuted2After = getSchedExeExecuted(actionIndex2);
    bool isCancelled1After = getSchedExeCancelled(actionIndex1);
    bool isCancelled2After = getSchedExeCancelled(actionIndex2);

    assert isExecuted1Before != isExecuted1After => isExecuted2Before == isExecuted2After && isCancelled1Before == isCancelled1After && isCancelled2Before == isCancelled2After;
    assert isCancelled1Before != isCancelled1After => isExecuted1Before == isExecuted1After && isExecuted2Before == isExecuted2After && isCancelled2Before == isCancelled2After;
    assert isExecuted2Before != isExecuted2After => isExecuted1Before == isExecuted1After && isCancelled1Before == isCancelled1After && isCancelled2Before == isCancelled2After;
    assert isCancelled2Before != isCancelled2After => isExecuted1Before == isExecuted1After && isExecuted2Before == isExecuted2After && isCancelled1Before == isCancelled1After;
}
