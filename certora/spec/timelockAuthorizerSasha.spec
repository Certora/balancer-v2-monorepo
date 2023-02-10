import "erc20.spec"
import "timelockAuthorizerMain.spec"


/**************************************************
 *             VERIFIED INVARIANTS                *
 **************************************************/


// STATUS - verified
// (Helper) ensure that two ways to get ID mathc each other (saw before that it didn't, needed to check)
invariant matchingGenralActionIds()
    _GENERAL_GRANT_ACTION_ID() == getExtendedActionId(getActionId(getGrantActionId()), GENERAL_PERMISSION_SPECIFIER())
    && _GENERAL_REVOKE_ACTION_ID() == getExtendedActionId(getActionId(getRevokeActionId()), GENERAL_PERMISSION_SPECIFIER())


// STATUS - verified
// all _delaysPerActionId are less or equal than MAX_DELAY
invariant notGreaterThanMax(env e, bytes32 actionId)
    _delaysPerActionId(actionId) <= MAX_DELAY()
    {
        preserved setDelay(bytes32 actionId1, uint256 delay) with (env e2) {
            require actionId == actionId1;
            require delay <= MAX_DELAY();
        }
    }


/**************************************************
 *                  VERIFIED RULES                *
 **************************************************/


// STATUS - verified
// executableAt is immutable
rule immutableExecuteAt(env e, method f) {
    uint256 actionIndex;

    require limitArrayLength();  
    require actionIndex < getSchedExeLength();  // need this require becuase otherwise the tool takes index that will be created. Thus it's 0 before and > 0 after.

    uint256 executableAtBefore = getSchedExeExecutableAt(actionIndex);

    calldataarg args;
    f(e, args);

    uint256 executableAtAfter = getSchedExeExecutableAt(actionIndex);

    assert executableAtBefore == executableAtAfter;
}

// STATUS - verified
// where is immutable
rule immutableWhere(env e, method f) {
    uint256 actionIndex;

    require limitArrayLength();  
    require actionIndex < getSchedExeLength();  // need this require becuase otherwise the tool takes index that will be created. Thus it's 0 before and > 0 after.

    address whereBefore = getSchedExeWhere(actionIndex);

    calldataarg args;
    f(e, args);

    address whereAtAfter = getSchedExeWhere(actionIndex);

    assert whereBefore == whereAtAfter;
}


// STATUS - verified
// protected is immutable
rule immutableProtected(env e, method f) {
    uint256 actionIndex;

    require limitArrayLength();  
    require actionIndex < getSchedExeLength();  // need this require becuase otherwise the tool takes index that will be created. Thus it's 0 before and > 0 after.

    bool protectedBefore = getSchedExeProtected(actionIndex);

    calldataarg args;
    f(e, args);

    bool protectedAfter = getSchedExeProtected(actionIndex);

    assert protectedBefore == protectedAfter;
}


// STATUS - verified
// Only one flag executed/cancelled can be changed at a time
rule onlyOneExecuteOrCancelCanChangeAtTime(env e, method f) {
    uint256 actionIndex1; uint256 actionIndex2;
    bool isExecuted1Before = getSchedExeExecuted(actionIndex1);
    bool isExecuted2Before = getSchedExeExecuted(actionIndex2);
    bool isCancelled1Before = getSchedExeCancelled(actionIndex1);
    bool isCancelled2Before = getSchedExeCancelled(actionIndex2);

    require actionIndex1 != actionIndex2;
    require getSchedExeLength() < max_uint / 4;

    calldataarg args;
    f(e, args);

    bool isExecuted1After = getSchedExeExecuted(actionIndex1);
    bool isExecuted2After = getSchedExeExecuted(actionIndex2);
    bool isCancelled1After = getSchedExeCancelled(actionIndex1);
    bool isCancelled2After = getSchedExeCancelled(actionIndex2);

    assert isExecuted1Before != isExecuted1After 
                => (isExecuted2Before == isExecuted2After 
                    && isCancelled1Before == isCancelled1After 
                    && isCancelled2Before == isCancelled2After)
                    && !isExecuted1Before;
    assert isCancelled1Before != isCancelled1After 
                => (isExecuted1Before == isExecuted1After 
                    && isExecuted2Before == isExecuted2After 
                    && isCancelled2Before == isCancelled2After)
                    && !isCancelled1Before;
    assert isExecuted2Before != isExecuted2After 
                => (isExecuted1Before == isExecuted1After 
                    && isCancelled1Before == isCancelled1After 
                    && isCancelled2Before == isCancelled2After)
                    && !isExecuted2Before;
    assert isCancelled2Before != isCancelled2After 
                => (isExecuted1Before == isExecuted1After 
                    && isExecuted2Before == isExecuted2After 
                    && isCancelled1Before == isCancelled1After)
                    && !isCancelled2Before;
}

// STATUS - verified
// Flag was changed by correct function. ("only one flag can be changed at a time" was checked above)
rule onlyExecuteAndCancelCanChangeTheirFlags(env e, method f) {
    uint256 actionIndex1; uint256 actionIndex2;
    bool isExecuted1Before = getSchedExeExecuted(actionIndex1);
    bool isExecuted2Before = getSchedExeExecuted(actionIndex2);
    bool isCancelled1Before = getSchedExeCancelled(actionIndex1);
    bool isCancelled2Before = getSchedExeCancelled(actionIndex2);

    require actionIndex1 != actionIndex2;
    require limitArrayLength();

    calldataarg args;
    f(e, args);

    bool isExecuted1After = getSchedExeExecuted(actionIndex1);
    bool isExecuted2After = getSchedExeExecuted(actionIndex2);
    bool isCancelled1After = getSchedExeCancelled(actionIndex1);
    bool isCancelled2After = getSchedExeCancelled(actionIndex2);

    assert (isExecuted1Before != isExecuted1After 
                || isExecuted2Before != isExecuted2After)
            => f.selector == execute(uint256).selector;
    assert (isCancelled1Before != isCancelled1After 
                || isCancelled2Before != isCancelled2After)
            => f.selector == cancel(uint256).selector;
}



/**************************************************
 *                   IN PROGRESS                  *
 **************************************************/


// STATUS - in progress (cannot return bytes. it's considered as an array)
// data is immutable
// rule immutableData(env e, method f) {
//     uint256 actionIndex;

//     require getSchedExeLength() < max_uint / 4;
//     require limitArrayLength();  // need this require becuase otherwise the tool takes index that will be created. Thus it's 0 before and > 0 after.

//     bytes dataBefore = getSchedExeData(actionIndex);

//     calldataarg args;
//     f(e, args);

//     bytes dataAfter = getSchedExeData(actionIndex);

//     assert dataBefore == dataAfter;
// }


// STATUS - in progress
// Any executableAt from _scheduledExecutions is not far more in the future than MAX_DELAY
invariant notFarFuture(env e, uint256 actionIndex)
    getSchedExeExecutableAt(actionIndex) <= e.block.timestamp + MAX_DELAY()
    {
        preserved with (env e2) {
            require e.block.timestamp == e2.block.timestamp;
            requireInvariant notGreaterThanMax(e2, getActionIdHelper(actionIndex));
        }
        preserved schedule(address where, bytes data, address[] executors) with (env e3) {
            require e.block.timestamp == e3.block.timestamp;
            require getActionIdHelper(actionIndex) == getActionIdFromDataAndWhere(data, where);
            requireInvariant notGreaterThanMax(e3, getActionIdHelper(actionIndex));
            require limitArrayLength();
        }
        preserved scheduleGrantPermission(bytes32 actionId, address account, address where, address[] executors) with (env e4) {
            require e.block.timestamp == e4.block.timestamp;
            bytes data;
            require data == returnDataForScheduleGrantPermission(actionId, account, where);
            require getActionIdHelper(actionIndex) == getActionIdFromDataAndWhere(data, where);
            requireInvariant notGreaterThanMax(e4, getActionIdHelper(actionIndex));
            require limitArrayLength();
        }
        // preserved scheduleDelayChange(bytes32 actionId, uint256 newDelay, address[] executors) with (env e5) {
        //     require e.block.timestamp == e5.block.timestamp;
        //     require getActionIdHelper(actionIndex) == getActionIdFromDataAndWhere(data, where);
        //     requireInvariant notGreaterThanMax(e5, getActionIdHelper(actionIndex));
        //     require limitArrayLength();
        // }
        // preserved scheduleRootChange(address newRoot, address[] executors) with (env e6) {
        //     require e.block.timestamp == e6.block.timestamp;
        //     require getActionIdHelper(actionIndex) == getActionIdFromDataAndWhere(data, where);
        //     requireInvariant notGreaterThanMax(e6, getActionIdHelper(actionIndex));
        //     require limitArrayLength();
        // }
        // preserved scheduleRevokePermission(bytes32 actionId, address account, address where, address[] executors) with (env e7) {
        //     require e.block.timestamp == e7.block.timestamp;
        //     require getActionIdHelper(actionIndex) == getActionIdFromDataAndWhere(data, where);
        //     requireInvariant notGreaterThanMax(e7, getActionIdHelper(actionIndex));
        //     require limitArrayLength();
        // }
    }




/**************************************************
 *                     BLOCKED                    *
 **************************************************/


// STATUS - in progress
// go over array, two the same action IDs, id with lower index should have lower or equal executableAt
invariant arrayHierarchy(env e, uint256 indexLow, uint256 indexHigh)
    (indexLow < indexHigh
        && getActionIdHelper(indexLow) == getActionIdHelper(indexHigh)) 
    => getSchedExeExecutableAt(indexLow) <= getSchedExeExecutableAt(indexHigh)
    {
        preserved {
            require limitArrayLength();
        }
    }


