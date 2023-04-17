import "timelockAuthorizerMain.spec";


/**************************************************
 *             VERIFIED INVARIANTS                *
 **************************************************/


// STATUS - verified
// all _delaysPerActionId are less or equal than MAX_DELAY
invariant notGreaterThanMax(bytes32 actionId)
    (actionId != getSetAuthorizerActionId() && _delaysPerActionId(getSetAuthorizerActionId()) <= MAX_DELAY()) => _delaysPerActionId(actionId) <= MAX_DELAY()
    {
        preserved setDelay(bytes32 actionId1, uint256 delay) with (env e2) {
            require actionId == actionId1;
        }
    }


// STATUS - verified
// Any executableAt from _scheduledExecutions is not far more in the future than MAX_DELAY
invariant notFarFuture(uint256 timestamp, uint256 actionIndex)
    to_mathint(getSchedExeExecutableAt(actionIndex)) <= timestamp + MAX_DELAY()
    {
        preserved with (env e2) {
            require timestamp == e2.block.timestamp;
            requireInvariant notGreaterThanMax(getActionIdHelper(actionIndex));
            require limitArrayLength();
        }
    }


// STATUS - verified
// go over array, two the same action IDs, id with lower index should have lower or equal executableAt
// However the tool could "violate" it in two steps due of induction
invariant arrayHierarchy(env e, uint256 indexLow, uint256 indexHigh)
    (indexLow < indexHigh
        && getActionIdHelper(indexLow) == getActionIdHelper(indexHigh)) 
    => getSchedExeExecutableAt(indexLow) <= getSchedExeExecutableAt(indexHigh)
    {
        preserved {
            require limitArrayLength();
        }
    }


// STATUS - verified
// `scheduledExecutionId` can’t be executed and cancelled at the same time.
invariant oneOfThree(uint256 actionIndex)
    (!getSchedExeExecuted(actionIndex) && !getSchedExeCancelled(actionIndex))
        || (getSchedExeExecuted(actionIndex) && !getSchedExeCancelled(actionIndex))
        || (!getSchedExeExecuted(actionIndex) && getSchedExeCancelled(actionIndex))



/**************************************************
 *                  VERIFIED RULES                *
 **************************************************/


// STATUS - verified
// executableAt is immutable
rule immutableExecuteAt(env e, method f) {
    uint256 actionIndex;

    require limitArrayLength();  
    require actionIndex < getSchedExeLength();  // need this require because otherwise the tool takes index that will be created. Thus it's 0 before and > 0 after.

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
    bool isCancelled1Before = getSchedExeCancelled(actionIndex1);

    require actionIndex1 != actionIndex2;
    require limitArrayLength();

    calldataarg args;
    f(e, args);

    bool isExecuted1After = getSchedExeExecuted(actionIndex1);
    bool isCancelled1After = getSchedExeCancelled(actionIndex1);

    assert (isExecuted1Before != isExecuted1After)
            => f.selector == sig:execute(uint256).selector;
    assert (isCancelled1Before != isCancelled1After)
            => f.selector == sig:cancel(uint256).selector;
}


// STATUS - verified
// if canExecute returns true / false, execute finishes successfully / reverts.
rule canExecuteAndExecuteUnion(env e, method f) {
    uint256 scheduledExecutionId;

    bool canExe = canExecute(e, scheduledExecutionId);
    bool canReverted = lastReverted;

    execute@withrevert(e, scheduledExecutionId);
    bool exeReveted = lastReverted;

    assert (!canExe || canReverted) => exeReveted;
}


// STATUS - verified
// If it’s one of the states (executed/cancelled) it should remain in forever.
rule executedForever(env e, method f) {
    uint256 actionIndex1;

    require actionIndex1 < getSchedExeLength();
    require limitArrayLength(); 

    bool isExecutedBefore = getSchedExeExecuted(actionIndex1);
    bool isCancelledBefore = getSchedExeCancelled(actionIndex1);

    calldataarg args;
    f(e, args);

    bool isExecutedAfter = getSchedExeExecuted(actionIndex1);
    bool isCancelledAfter = getSchedExeCancelled(actionIndex1);

    assert isExecutedBefore && !isCancelledBefore => isExecutedAfter && !isCancelledAfter;
    assert !isExecutedBefore && isCancelledBefore => !isExecutedAfter && isCancelledAfter;
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
// check what function can “frontrun“ an action execution: cancel(), anything else?
rule executionFrontrun(env e, method f) {
    uint256 scheduledExecutionId;

    storage initialStorage = lastStorage;

    execute@withrevert(e, scheduledExecutionId);
    bool isRevertedSingle = lastReverted;

    calldataarg args;
    f(e, args) at initialStorage;
    execute@withrevert(e, scheduledExecutionId);
    bool isRevertedFrontrun = lastReverted;

    assert !isRevertedSingle => !isRevertedFrontrun;
}



// STATUS - in progress
// account with GLOBAL_CANCELER_SCHEDULED_EXECUTION_ID() can cancel any scheduled execution.
rule almightyGlobal(env e, uint256 scheduledExecutionId) {
    bool isAlmighty = _isCanceler(GLOBAL_CANCELER_SCHEDULED_EXECUTION_ID(), e.msg.sender);
    require !_isCanceler(scheduledExecutionId, e.msg.sender);
    require !isRoot(e.msg.sender);

    cancel@withrevert(e, scheduledExecutionId);
    bool isReverted = lastReverted;

    assert !isReverted => isAlmighty, "Remember, with great power comes great responsibility.";
}