import "erc20.spec"

// using MockVault as MockVault
using Vault as Vault

methods {
    // Summarization
    execute(address, bytes) returns(bytes) => DISPATCHER(true)
    getActionId(bytes4) returns(bytes32) => DISPATCHER(true)        // what is the "target/where" in cancel()? "where" in schedule?   setDelay()
    sendTo() returns(bool, bytes) => DISPATCHER(true)

    // TimelockAuthorizerHarness.sol
    getSchedExeWhere(uint256) returns(address) envfree
    getSchedExeData(uint256) returns(bytes) envfree
    getSchedExeExecuted(uint256) returns(bool) envfree
    getSchedExeCancelled(uint256) returns(bool) envfree
    getSchedExeProtected(uint256) returns(bool) envfree
    getSchedExeExecutableAt(uint256) returns(uint256) envfree
    getSchedExeLength() returns(uint256) envfree
    getGrantActionId() returns(bytes4) envfree
    getRevokeActionId() returns(bytes4) envfree
    getActionIdHelper(uint256) returns (bytes32) envfree
    getActionIdFromDataAndWhere(bytes, address) returns(bytes32) envfree
    returnGetActionIdOfSetPendingRoot() returns(bytes32) envfree
    getSetAuthorizerActionId() returns (bytes32) envfree

    returnDataForScheduleGrantPermission(bytes32, address, address) returns(bytes) envfree

    // TimelockAuthorizer.sol constants
    EVERYWHERE() returns(address) envfree
    MIN_DELAY() returns(uint256) envfree
    MAX_DELAY() returns(uint256) envfree
    GENERAL_PERMISSION_SPECIFIER() returns(bytes32) envfree
    GRANT_ACTION_ID() returns(bytes32) envfree
    _GENERAL_GRANT_ACTION_ID() returns(bytes32) envfree
    _GENERAL_REVOKE_ACTION_ID() returns(bytes32) envfree

    // TimelockAuthorizer.sol
    getActionIdDelay(bytes32) returns(uint256) envfree
    getActionId(bytes4) returns (bytes32) envfree
    _isPermissionGranted(bytes32) returns(bool) envfree
    getPermissionId(bytes32, address, address) returns(bytes32) envfree
    _root() returns(address) envfree
    _pendingRoot() returns(address) envfree
    _executor() returns(address) envfree
    getExecuteExecutionActionId(uint256) returns(bytes32) envfree
    getExtendedActionId(bytes32, bytes32) returns(bytes32) envfree
    getPendingRoot() returns(address) envfree
    hasPermission(bytes32, address, address) returns (bool) envfree
    isRoot(address) returns (bool) envfree
    _authorizerAdaptorEntrypoint() returns (address) envfree
    _authorizerAdaptor() returns (address) envfree
    _delaysPerActionId(bytes32) returns(uint256) envfree
    getExecutor() returns(address) envfree
}


/**************************************************
 *                   DEFINITIONS                  *
 **************************************************/

definition limitArrayLength() returns bool = getSchedExeLength() < max_uint / 4;


/**************************************************
 *                    FUNCTIONS                   *
 **************************************************/

function helperSetDelay(env e, method f, bytes32 actionId, uint256 delayArg) {
    if (f.selector == setDelay(bytes32, uint256).selector) {
        setDelay(e, actionId, delayArg);
    } else {
        calldataarg args;
        env e2;
        f(e2, args);
    }
}


/**************************************************
 *             VERIFIED INVARIANTS                *
 **************************************************/


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


// STATUS - verified
// Any executableAt from _scheduledExecutions is not far more in the future than MAX_DELAY
invariant notFarFuture(env e, uint256 actionIndex)
    getSchedExeExecutableAt(actionIndex) <= e.block.timestamp + MAX_DELAY()
    {
        preserved with (env e2) {
            require e.block.timestamp == e2.block.timestamp;
            requireInvariant notGreaterThanMax(e2, getActionIdHelper(actionIndex));
            require limitArrayLength();
        }
    }


// STATUS - verified
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


/**
 * Rule to check that the _pendingRoot can be changed only by the executor
 */
// STATUS: Verified
rule pendingRootChangeOnlyByExecutor(method f, env e){
    address executer        = _executor();
    address _pendingRoot    = getPendingRoot();

    calldataarg args;
    f(e, args);

    address pendingRoot_    = getPendingRoot();

    assert (_pendingRoot == 0 && pendingRoot_ != 0) => e.msg.sender == executer,"pendingRoot can only be changed by the executer";
}


/**
 * Rule to check that the _root can be changed only by the _pendingRoot
 */
// STATUS: Verified
rule rootChangedOnlyByPendingRoot(method f, env e){
    address _root           = _root();
    address _pendingRoot    = getPendingRoot();
    
    calldataarg args;
    f(e, args);

    address root_           = _root();

    assert _root != root_ => e.msg.sender == _pendingRoot,"only pending root can change the root";
}


/**
 * Rule to check the access privilege for cancellling an already scheduled execution
 */
// STATUS: Verified
rule whoCanCancelExecution(method f, env e){
    uint256 index;

    uint256 length      = getSchedExeLength();
    bool _cancelled     = getSchedExeCancelled(index);
    bytes32 actionId    = getActionIdHelper(index);
    address where       = getSchedExeWhere(index);
    bool _isRoot        = isRoot(e.msg.sender);
    bool _hasPermission = hasPermission(actionId, e.msg.sender, where);

    require index       < length;
    require length      < max_uint256;
    require getSchedExeLength() < max_uint / 4;

    calldataarg args;
    f(e, args);
    
    bool cancelled_     = getSchedExeCancelled(index);

    assert _cancelled != cancelled_ => _isRoot || _hasPermission,
    "only the root or an account with the permission of the corresponding actionID and where can cancel a scheduled execution";
}

/**
 * Rule to check change in executed status and the condition/ permission for it.
 */
// STATUS: Verified
rule schExExecutionCheck(method f, env e){
    uint256 index;

    uint256 length      = getSchedExeLength();
    bool _executed      = getSchedExeExecuted(index);
    bool protected      = getSchedExeProtected(index);
    bytes32 actionId    = getActionIdHelper(index);
    address where       = getSchedExeWhere(index);
    bool _hasPermission = hasPermission(actionId, e.msg.sender, where);

    require index       < length;
    require getSchedExeLength() < max_uint / 4;

    calldataarg args;
    f(e, args);
    
    bool executed_      = getSchedExeExecuted(index);

    assert !executed_ => !_executed,"execution cannot be reversed";
    assert _executed != executed_ => !protected || _hasPermission,
    "only the root or an account with the permission of the corresponding actionID and where can cancel a scheduled execution";
}

/**
 * Rule to check only the executor can change delays.
 */
// STATUS: Verified
rule delayPerActionIdChangeAccess(method f, env e){
    bytes32 actionID;
    
    uint256 _delay = getActionIdDelay(actionID);
    address executor = _executor();

    calldataarg args;
    f(e, args);

    uint256 delay_ = getActionIdDelay(actionID);

    assert delay_ != _delay => e.msg.sender == executor,"only executor should be able to change delaysPerActionID";
}

/**
 * A scheduled execution cannot be executed before the executableAt time
 */
// STATUS: Verified
rule schExeNotExecutedBeforeTime(method f, env e){
    uint256 index;

    uint256 executableAt = getSchedExeExecutableAt(index);
    uint256 length = getSchedExeLength();
    bool _executed = getSchedExeExecuted(index);

    calldataarg args;
    f(e, args);

    bool executed_ = getSchedExeExecuted(index);

    assert !_executed && executed_ => e.block.timestamp >= executableAt,
        "cannot execute and execution before executableAt time";
}

/**
 * A rule to check that only pendingRoot can become the new Root
 */
// STATUS: Verified
rule onlyPendingRootCanBecomeNewRoot(method f, env e){
    address _pendingRoot = _pendingRoot();
    address _root = _root();

    calldataarg args;
    f(e, args);

    address root_ = _root();
    
    assert root_ == _root || root_ == _pendingRoot,
        "root can either remain unchanged or change to the pendingRoot";
}


// STATUS - verified
// Delays of actions are less or equal to MAX_DELAY.
rule delaysOfActionsHaveUpperBound(env e, method f, bytes32 actionId) {
    uint256 delayBefore = getActionIdDelay(actionId);
    uint256 maximal_delay = MAX_DELAY();

    require(delayBefore <= maximal_delay);

    // Invoke any function
    calldataarg args;
    f(e, args);

    uint256 delayAfter = getActionIdDelay(actionId);

    // If the number of scheduled executions changed, it was increased by one.
    // Note: In this rule we allow the executor to change delay in any way.
    assert e.msg.sender == getExecutor() || delayAfter <= maximal_delay,
        "Delay of an action is greater than MAX_DELAY.";
}


// STATUS - verified
// The array _scheduledExecution is never shortened.
rule scheduledExecutionsArrayIsNeverShortened(env e, method f) {
    uint256 lengthBefore = getSchedExeLength();

    require(to_uint256(lengthBefore + 1) > lengthBefore);

    // Invoke any function
    calldataarg args;
    f(e, args);

    uint256 lengthAfter = getSchedExeLength();

    // If the number of scheduled executions changed, it was increased by one.
    assert lengthBefore != lengthAfter =>
        lengthBefore + 1 == lengthAfter,
        "Number of scheduled executions changed and did not increase by one.";
}


// STATUS - verified
// This rule checks, that what a change of delay is scheduled, the created
// ScheduledExecution has appropriate executableAt (waiting time to be executed).
rule scheduleDelayChangeHasProperDelay(env e, env eForPayableFunctions, bytes32 actionId) {
    uint256 delayBefore = getActionIdDelay(actionId);
    uint256 newDelay;
    address[] executors;
    uint256 numberOfScheduledExecutionsBefore = getSchedExeLength();

    require(delayBefore <= MAX_DELAY());
    require(newDelay >= MIN_DELAY());
    require(numberOfScheduledExecutionsBefore < max_uint256);

    uint256 timestampBefore = eForPayableFunctions.block.timestamp;

    require(to_uint256(timestampBefore + timestampBefore) > timestampBefore);

    scheduleDelayChange(eForPayableFunctions, actionId, newDelay, executors);

    uint256 numberOfScheduledExecutionsAfter = getSchedExeLength();
    
    assert numberOfScheduledExecutionsAfter == numberOfScheduledExecutionsBefore + 1;

    uint256 executableAt = getSchedExeExecutableAt(numberOfScheduledExecutionsBefore);

    assert executableAt >= timestampBefore + MIN_DELAY();
    assert newDelay <= delayBefore =>
        executableAt - timestampBefore >= delayBefore - newDelay;
}


// STATUS - verified
// ScheduleRootChange creates a new scheduled execution and
// it doesn't change current root nor pending root.
rule scheduleRootChangeCreatesSE(env e) {
    address rootBefore = _root();
    address pendingRootBefore = getPendingRoot();
    uint256 numberOfSchedExeBefore = getSchedExeLength();
    address newRoot;
    address[] executors;

    require newRoot != rootBefore;
    require(numberOfSchedExeBefore < max_uint / 4);

    scheduleRootChange@withrevert(e, newRoot, executors);

    bool reverted = lastReverted;
    uint256 numberOfSchedExeAfter = getSchedExeLength();

    assert !reverted => numberOfSchedExeAfter == numberOfSchedExeBefore + 1;
    assert !reverted => rootBefore == _root();
    assert !reverted => pendingRootBefore == getPendingRoot();
}


// STATUS - verified
// claimRoot is the only function that changes root
// and variables are updated appropriately.
rule rootChangesOnlyWithClaimRoot(env eForPayableFunctions, method f) {
    address rootBefore = _root();
    address pendingRootBefore = getPendingRoot();

    // Invoke any function
    calldataarg args;
    f(eForPayableFunctions, args);

    address rootAfter = _root();

    // if the function changed the root, the sender was pendingRoot
    assert rootBefore != rootAfter =>
        eForPayableFunctions.msg.sender == pendingRootBefore,
        "Root changed by somebody, who was not pending root.";
    // if the function changed the root, the new root is old pendingRoot
    assert rootBefore != rootAfter =>
        rootAfter == pendingRootBefore,
        "Pending root changed root to somebody else.";
    // if the function f changed the root, then f must be claimRoot
    assert rootBefore != rootAfter =>
        f.selector == claimRoot().selector,
        "Root changed by a function other than claimRoot.";
}


// STATUS - verified
// ScheduledExecution that has already been cancelled or executed
// cannot be canceled again.
rule scheduledExecutionCanBeCancelledOnlyOnce(env e, uint256 index) {
    bool canceled_before = getSchedExeCancelled(index);
    bool executed_before = getSchedExeExecuted(index);

    cancel@withrevert(e, index);
    assert (canceled_before || executed_before) => lastReverted;
}


// STATUS - verified
// ScheduledExecution that has already been cancelled or executed
// cannot be executed again.
rule scheduledExecutionCanBeExecutedOnlyOnce(env e, uint256 index) {
    bool canceled_before = getSchedExeCancelled(index);
    bool executed_before = getSchedExeExecuted(index);

    execute@withrevert(e, index);
    assert (canceled_before || executed_before) => lastReverted;
}


// STATUS - verified
// When a delay is changed, it is because setDelay is executed with
// the parameter being the new delay.
rule delayChangesOnlyBySetDelay(env e, method f, bytes32 actionId) {
    uint256 delayBefore = getActionIdDelay(actionId);
    uint256 delayArg;

    helperSetDelay(e, f, actionId, delayArg);

    uint256 delayAfter = getActionIdDelay(actionId);

    assert delayAfter != delayBefore =>
        f.selector == setDelay(bytes32, uint256).selector;
    assert delayAfter != delayBefore =>
        delayAfter == delayArg;
}