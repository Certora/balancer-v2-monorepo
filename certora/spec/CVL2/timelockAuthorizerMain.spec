methods {
    // Summarization
    function _.execute(address, bytes) external  => DISPATCHER(true);
    function _.getActionId(bytes4) external => DISPATCHER(true);
    function _.sendTo() external => DISPATCHER(true);

    // TimelockAuthorizerHarness.sol
    function getSchedExeWhere(uint256) external returns(address) envfree;
    function getSchedExeData(uint256) external returns(bytes) envfree;
    function getSchedExeExecuted(uint256) external returns(bool) envfree;
    function getSchedExeCancelled(uint256) external returns(bool) envfree;
    function getSchedExeProtected(uint256) external returns(bool) envfree;
    function getSchedExeExecutableAt(uint256) external returns(uint256) envfree;
    function getSchedExeLength() external returns(uint256) envfree;
    // function getGrantActionId() external returns(bytes4) envfree;
    // function getRevokeActionId() external returns(bytes4) envfree;
    function getActionIdHelper(uint256) external returns (bytes32) envfree;
    function getActionIdFromDataAndWhere(bytes, address) external returns(bytes32) envfree;
    // function returnGetActionIdOfSetPendingRoot() external returns(bytes32) envfree;
    function getSetAuthorizerActionId() external returns (bytes32) envfree;

    // function returnDataForScheduleGrantPermission(bytes32, address, address) external returns(bytes) envfree;

    // TimelockAuthorizer.sol constants
    function EVERYWHERE() external returns(address) envfree;
    function MINIMUM_CHANGE_DELAY_EXECUTION_DELAY() external returns(uint256) envfree;
    function MAX_DELAY() external returns(uint256) envfree;
    function GLOBAL_CANCELER_SCHEDULED_EXECUTION_ID() external returns(uint256) envfree;
    // function GENERAL_PERMISSION_SPECIFIER() external returns(bytes32) envfree;
    // function GRANT_ACTION_ID() external returns(bytes32) envfree;
    // function _GENERAL_GRANT_ACTION_ID() external returns(bytes32) envfree;
    // function _GENERAL_REVOKE_ACTION_ID() external returns(bytes32) envfree;

    // TimelockAuthorizer.sol
    function getActionIdDelay(bytes32) external returns(uint256) envfree;
    function getActionIdGrantDelay(bytes32) external returns(uint256) envfree;
    function getActionIdRevokeDelay(bytes32) external returns(uint256) envfree;
    // function getActionId(bytes4) external returns (bytes32) envfree;
    function isPermissionGrantedOnTarget(bytes32, address, address) external returns(bool) envfree;
    function getPermissionId(bytes32, address, address) external returns(bytes32) envfree;
    function _pendingRoot() external returns(address) envfree;
    // function getExecuteExecutionActionId(uint256) external returns(bytes32) envfree;
    // function getExtendedActionId(bytes32, bytes32) external returns(bytes32) envfree;
    function hasPermission(bytes32, address, address) external returns (bool) envfree;
    function _authorizerAdaptorEntrypoint() external returns (address) envfree;
    function _authorizerAdaptor() external returns (address) envfree;
    function _delaysPerActionId(bytes32) external returns(uint256) envfree;
    function _getDelayChangeExecutionDelay(uint256, uint256) external returns(uint256) envfree;

    // TimelockAuthorizerManagement.sol
    function getTimelockExecutionHelper() external returns(address) envfree;
    function isExecutor(uint256, address) external returns(bool) envfree;
    function isRoot(address) external returns (bool) envfree;
    function getRoot() external returns(address) envfree;
    function getPendingRoot() external returns(address) envfree;
    function isGranter(bytes32, address, address) external returns(bool) envfree;
    function isRevoker(address, address) external returns(bool) envfree;
    function isCanceler(uint256, address) external returns(bool) envfree;

    function _isCanceler(uint256, address) external returns(bool) envfree;
}


/**************************************************
 *                   DEFINITIONS                  *
 **************************************************/

definition limitArrayLength() returns bool = getSchedExeLength() < max_uint / 4;


/**************************************************
 *                    FUNCTIONS                   *
 **************************************************/

function helperSetDelay(env e, method f, bytes32 actionId, uint256 delayArg) {
    if (f.selector == sig:setDelay(bytes32, uint256).selector) {
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
invariant notGreaterThanMax(bytes32 actionId)
    (actionId != getSetAuthorizerActionId() && _delaysPerActionId(getSetAuthorizerActionId()) <= MAX_DELAY()) => _delaysPerActionId(actionId) <= MAX_DELAY()
    {
        preserved setDelay(bytes32 actionId1, uint256 delay) with (env e2) {
            require actionId == actionId1;
        }
    }


// STATUS - verified
// Any executableAt from _scheduledExecutions is not later in the future than MAX_DELAY
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
// For any two scheduled executions having the same action ID, 
// the execution with the lower index should have a lower or equal executableAt comparing to the execution with the higher index.
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
// No `scheduledExecution` can be executed and cancelled at the same time.
invariant oneOfThree(uint256 actionIndex)
    (!getSchedExeExecuted(actionIndex) && !getSchedExeCancelled(actionIndex))
        || (getSchedExeExecuted(actionIndex) && !getSchedExeCancelled(actionIndex))
        || (!getSchedExeExecuted(actionIndex) && getSchedExeCancelled(actionIndex))


// When `isPermissionGrantedOnTarget(id, account, where)` returns `true`, then `hasPermission(id, account, where)` also returns `true`
invariant hasPermissionIfIsGrantedOnTarget(bytes32 id, address account, address where)
    isPermissionGrantedOnTarget(id, account, where) => hasPermission(id, account, where)
    


/**************************************************
 *                  VERIFIED RULES                *
 **************************************************/


/**
 * Rule to check the access privilege for cancellling an already scheduled execution
 */
// STATUS: Verified
rule whoCanCancelExecution(method f, env e){
    uint256 index;
    uint256 length   = getSchedExeLength();
    bool _cancelled  = getSchedExeCancelled(index);
    bool _isCanceler = isCanceler(index, e.msg.sender);
    require index    < length;
    require length   < max_uint256;
    require getSchedExeLength() < max_uint / 4;

    calldataarg args;
    f(e, args);

    bool cancelled_     = getSchedExeCancelled(index);

    assert _cancelled => cancelled_, "cancellation cannot be reversed";
    assert _cancelled != cancelled_ => _isCanceler, "only canceller can cancel a scheduled execution";
}


/**
 * Rule to check change in executed status and the condition/ permission for it.
 */
// STATUS: Verified
rule schExExecutionCheck(method f, env e) {
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
    require actionIndex < getSchedExeLength();  // need this require because otherwise the tool takes index that will be created. Thus it's 0 before and > 0 after.

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
    require actionIndex < getSchedExeLength();  // need this require because otherwise the tool takes index that will be created. Thus it's 0 before and > 0 after.

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

    bool canExe = canExecute@withrevert(e, scheduledExecutionId);
    bool canReverted = lastReverted;

    execute@withrevert(e, scheduledExecutionId);
    bool exeReveted = lastReverted;

    assert (!canExe || canReverted) => exeReveted;
}


// STATUS - verified
// If it’s one of the states (executed/cancelled) it should remain in forever.
rule executedCanceledForever(env e, method f) {
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


// STATUS - verified
// account with GLOBAL_CANCELER_SCHEDULED_EXECUTION_ID() can cancel any scheduled execution.
rule almightyGlobal(env e, uint256 scheduledExecutionId) {
    bool isAlmighty = _isCanceler(GLOBAL_CANCELER_SCHEDULED_EXECUTION_ID(), e.msg.sender);
    require !_isCanceler(scheduledExecutionId, e.msg.sender);   // eliminate scenarious when a sender is a canceler for a specific scheduled execution
    require !isRoot(e.msg.sender);   // eliminate scenarious when a sender is a root

    cancel@withrevert(e, scheduledExecutionId);
    bool isReverted = lastReverted;

    assert !isReverted => isAlmighty;
}


// STATUS - violated, proves a bug
// when an action is scheduled, it has only one non-global canceler (should fail to show an issue we brought up)
// https://vaas-stg.certora.com/output/3106/48aa68dd0eee457cb14e6747a11e8967/?anonymousKey=3d5f3362a9509c7e5c997635f21c42878284bb3d
rule onlyOneCanceler(env e) {
    address where;
    bytes data;
    address[] executors;
    address user;
    address globalCanceler;

    uint256 scheduledExecutionId = schedule(e, where, data, executors);

    bool cancelerSender = isCanceler(scheduledExecutionId, e.msg.sender);
    require !_isCanceler(GLOBAL_CANCELER_SCHEDULED_EXECUTION_ID(), user);
    bool cancelerUser = isCanceler(scheduledExecutionId, user); 

    assert cancelerSender;
    assert e.msg.sender != user => !cancelerUser;
}


// STATUS - verified
// Address _root is not zero
rule rootNotZero(env e, method f)
{
    require(getRoot() != 0);
    require(e.msg.sender != 0);

    // Invoke any function
    calldataarg args;
    f(e, args);

    assert getRoot() != 0;
}


// STATUS - verified
// When execution function other than the claimRoot, only one of the roles revoker, granter
// or canceler can change during the function call and this can happen for one entity only.
rule onlyOneRoleChangeAtATimeForNonClaimRoot(env e, method f)
{
    uint256 scheduledExecution; address possibleCanceller;
    bool cancelerBefore = isCanceler(scheduledExecution, possibleCanceller);
    uint256 otherScheduledExecution; address otherPossibleCanceller;
    bool otherCancelerBefore = isCanceler(otherScheduledExecution, otherPossibleCanceller);
    address possibleRevoker; address whereRevoker;
    bool revokerBefore = isRevoker(possibleRevoker, whereRevoker);
    address otherPossibleRevoker; address otherWhereRevoker;
    bool otherRevokerBefore = isRevoker(otherPossibleRevoker, otherWhereRevoker);
    address possibleGranter; address whereGranter; bytes32 actionId;
    bool granterBefore = isGranter(actionId, possibleGranter, whereGranter);
    address otherPossibleGranter; address otherWhereGranter; bytes32 otherActionId;
    bool otherGranterBefore = isGranter(otherActionId, otherPossibleGranter, otherWhereGranter);
    bool nonClaimRoot = f.selector != sig:claimRoot().selector;

    require(possibleCanceller != otherPossibleCanceller);
    require(possibleRevoker != otherPossibleRevoker);
    require(possibleGranter != otherPossibleGranter);

    // Invoke any function
    calldataarg args;
    f(e, args);

    bool cancelerChanged = cancelerBefore != isCanceler(scheduledExecution, possibleCanceller);
    bool revokerChanged = revokerBefore != isRevoker(possibleRevoker, whereRevoker);
    bool granterChanged = granterBefore != isGranter(actionId, possibleGranter, whereGranter);

    assert cancelerChanged && nonClaimRoot => !revokerChanged && !granterChanged;
    assert revokerChanged && nonClaimRoot => !granterChanged && !cancelerChanged;
    assert granterChanged && nonClaimRoot => !cancelerChanged && !revokerChanged;

    bool otherCancelerChanged = otherCancelerBefore != isCanceler(otherScheduledExecution, otherPossibleCanceller);
    bool otherRevokerChanged = otherRevokerBefore != isRevoker(otherPossibleRevoker, otherWhereRevoker);
    bool otherGranterChanged = otherGranterBefore != isGranter(otherActionId, otherPossibleGranter, otherWhereGranter);

    assert cancelerChanged && nonClaimRoot => !otherCancelerChanged;
    assert revokerChanged && nonClaimRoot => !otherRevokerChanged;
    assert granterChanged && nonClaimRoot => !otherGranterChanged;
}


// STATUS - verified
// When `_root` is changed, it is only by calling `claimRoot`,
// the caller must be the `_pendingRoot` before the call
// and the new `_root` must also be the `_pendingRoot` before the call.
// and variables are updated appropriately.
rule rootChangesOnlyWithClaimRoot(env e, method f) {
    address rootBefore = getRoot();
    address pendingRootBefore = getPendingRoot();

    // Invoke any function
    calldataarg args;
    f(e, args);

    address rootAfter = getRoot();

    // if the function changed the root, the sender was pendingRoot
    assert rootBefore != rootAfter =>
        e.msg.sender == pendingRootBefore,
        "Root changed by somebody, who was not pending root.";
    // if the function changed the root, the new root is old pendingRoot
    assert rootBefore != rootAfter =>
        rootAfter == pendingRootBefore,
        "Pending root changed root to somebody else.";
    // if the function f changed the root, then f must be claimRoot
    assert rootBefore != rootAfter =>
        f.selector == sig:claimRoot().selector,
        "Root changed by a function other than claimRoot.";
}


// STATUS - verified
// Only two functions can change pending root: claimRoot and setPendingRoot.
// claimRoot can only be called by the execution helper.
// setPendingRoot can only be called by the root or the execution helper.
rule pendingRootChangesOnlyWithSetPendingRootOrClaimRoot(env e, method f) {
    address pendingRootBefore = getPendingRoot();
    address executionHelper = getTimelockExecutionHelper();

    // Invoke any function
    calldataarg args;
    f(e, args);

    address pendingRootAfter = getPendingRoot();

    // if the function f changed the root, then f must be setPendingRoot or claimRoot.
    assert pendingRootBefore != pendingRootAfter =>
        ( f.selector == sig:setPendingRoot(address).selector ||
        f.selector == sig:claimRoot().selector ),
        "Pending root changed by a function other than setPendingRoot or claimRoot.";
    // if the function changed the pending root, the sender was pending root or execution helper.
    assert pendingRootBefore != pendingRootAfter =>
        e.msg.sender == pendingRootBefore ||
        e.msg.sender == executionHelper,
        "Pending root changed by somebody, who was not root or executor.";
    assert (pendingRootBefore == 0 && pendingRootAfter != 0) => e.msg.sender == executionHelper,
        "Pending root changed from 0 by other entity than the executer";
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
// User cannot become an executor for already scheduled execution, meaning that
// a user has to be supplied as one of the executors when scheduling an execution,
// to be able to execute this execution.
rule cannotBecomeExecutorForAlreadyScheduledExecution(env e, method f) {
    uint256 length = getSchedExeLength();
    uint256 id;
    address user;
    require(length < max_uint256);
    require(id < length);
    bool isExecutor = isExecutor(id, user);

    // Invoke any function
    calldataarg args;
    f(e, args);

    assert !isExecutor => !isExecutor(id, user),
        "User became an executor after the scheduled execution has been scheduled.";
}


// STATUS - verified
// An execution can be executed (`canExecute`) only when it has not yet been cancelled
// or executed and its `executableAt` is not greater than current timestamp.
rule whatCanBeExecuted(env e) {
    uint256 id;
    uint256 length = getSchedExeLength();
    require(id < length);

    bool canExecute = canExecute(e, id);

    assert (
        !getSchedExeExecuted(id) &&
        !getSchedExeCancelled(id) &&
        getSchedExeExecutableAt(id) < e.block.timestamp
    ) => canExecute;
}


// STATUS - verified
// A protected scheduled execution can be executed only by an executor.
rule whoCanExecute(env e) {
    uint256 length = getSchedExeLength();
    uint256 id;
    require(id < length);

    bool canExecute = canExecute(e, id);
    bool isExecutor = isExecutor(id, e.msg.sender);
    bool isProtected = getSchedExeProtected(id);
    bool executedBefore = getSchedExeExecuted(id);

    execute(e, id);

    bool executedAfter = getSchedExeExecuted(id);

    assert !executedBefore && executedAfter => isExecutor || !isProtected;
    assert canExecute && isExecutor => executedAfter;
}


// STATUS - verified
// to cancel user must be canceler and it is impossible to execute after canceled.
rule cancelerCanCancel(env e) {
    uint256 length = getSchedExeLength();
    uint256 id;
    require(id < length);
    bool isCanceler = isCanceler(id, e.msg.sender);

    bool canceledBefore = getSchedExeCancelled(id);
    bool executed = getSchedExeExecuted(id);

    cancel(e, id);

    bool canceledAfter = getSchedExeCancelled(id);

    assert canceledAfter;
    assert !canceledBefore => isCanceler;

    execute@withrevert(e, id);
    bool reverted = lastReverted;
    assert canceledAfter => reverted;
}


// STATUS - verified
// `isExecutor` can only be changed by `_executionHelper` or
// in one of the schedule functions.
rule isExecutorChangedBySchedulerInNonScheduleFunction(env e, method f) {
    uint256 id;
    address user;
    bool executorBefore = isExecutor(id, user);

    // Invoke any function
    calldataarg args;
    f(e, args);

    bool executorAfter = isExecutor(id, user);

    assert executorBefore != executorAfter =>
            e.msg.sender == getTimelockExecutionHelper() ||
            f.selector == sig:schedule(address,bytes,address[]).selector ||
            f.selector == sig:scheduleRevokePermission(bytes32,address,address,address[]).selector ||
            f.selector == sig:scheduleGrantPermission(bytes32,address,address,address[]).selector ||
            f.selector == sig:scheduleRevokeDelayChange(bytes32,uint256,address[]).selector ||
            f.selector == sig:scheduleGrantDelayChange(bytes32,uint256,address[]).selector ||
            f.selector == sig:scheduleRootChange(address,address[]).selector ||
            f.selector == sig:scheduleDelayChange(bytes32,uint256,address[]).selector,
            "Executor status changed in non-schedule function by other entity than execution helper.";
}


// STATUS - verified
// `isGranter` can be changed only by `_root` or `_pendingRoot`
// A granter can be added only by calling `addGranter` or `claimRoot`
// A granter can only be removed by calling `removeGranter` or `claimRoot`.
rule isGranterChangesOnlyWithAddOrRemoveGranter(env e, method f) {
    bytes32 actionId;
    address account;
    address where;
    bool isGranterBefore = isGranter(actionId, account, where);
    address rootBefore = getRoot();
    address pendingRootBefore = getPendingRoot();

    // Invoke any function
    calldataarg args;
    f(e, args);

    bool isGranterAfter = isGranter(actionId, account, where);

    assert isGranterBefore && !isGranterAfter =>
                f.selector == sig:removeGranter(bytes32, address, address).selector ||
                f.selector == sig:claimRoot().selector,
                "User ceased to be granter not with removeGranter or claimRoot.";
    assert !isGranterBefore && isGranterAfter =>
                f.selector == sig:addGranter(bytes32, address, address).selector ||
                f.selector == sig:claimRoot().selector,
                "User became granter not with addGranter or claimRoot.";
    assert isGranterBefore != isGranterAfter =>
        e.msg.sender == rootBefore || e.msg.sender == pendingRootBefore,
        "Granter changed by somebody, who was not root or pending root.";
}


// STATUS - verified
// `isRevoker` can be changed only by `_root` or `_pendingRoot`
// A revoker can be added only by calling `addRevoker` or `claimRoot`
// A revoker can only be removed by calling `removeRevoker` or `claimRoot`.
rule isRevokerChangesOnlyWithAddOrRemoveRevoker(env e, method f) {
    address account;
    address where;
    bool isRevokerBefore = isRevoker(account, where);
    address rootBefore = getRoot();
    address pendingRootBefore = getPendingRoot();

    // Invoke any function
    calldataarg args;
    f(e, args);

    bool isRevokerAfter = isRevoker(account, where);

    assert isRevokerBefore && !isRevokerAfter =>
                f.selector == sig:removeRevoker(address, address).selector ||
                f.selector == sig:claimRoot().selector,
                "User ceased to be revoker not with removeRevoker or claimRoot.";
    assert !isRevokerBefore && isRevokerAfter =>
                f.selector == sig:addRevoker(address, address).selector ||
                f.selector == sig:claimRoot().selector,
                "User became revoker not with addRevoker or claimRoot.";
    assert isRevokerBefore != isRevokerAfter =>
        e.msg.sender == rootBefore || e.msg.sender == pendingRootBefore,
        "Revoker changed by somebody, who was not root or pending root.";
}


// STATUS - verified
// A canceler can be added only by calling `addCanceler`, `claimRoot`, `schedule`,
// `scheduleRevokePermission` or `scheduleGrantPermission`.
// A canceler can only be removed by calling `removeCanceler` or `claimRoot`.
rule isCancelerChangesOnlyWithAddOrRemoveCanceler(env e, method f) {
    uint256 scheduledExecution;
    address account;
    bool isCancelerBefore = isCanceler(scheduledExecution, account);
    address rootBefore = getRoot();
    address pendingRootBefore = getPendingRoot();

    // Invoke any function
    calldataarg args;
    f(e, args);

    bool isCancelerAfter = isCanceler(scheduledExecution, account);

    assert isCancelerBefore && !isCancelerAfter =>
                f.selector == sig:removeCanceler(uint256, address).selector ||
                f.selector == sig:claimRoot().selector,
                "User ceased to be canceler not with removeCanceler or claimRoot.";
    assert !isCancelerBefore && isCancelerAfter =>
                f.selector == sig:addCanceler(uint256, address).selector ||
                f.selector == sig:claimRoot().selector ||
                f.selector == sig:schedule(address,bytes,address[]).selector ||
                f.selector == sig:scheduleRevokePermission(bytes32,address,address,address[]).selector ||
                f.selector == sig:scheduleGrantPermission(bytes32,address,address,address[]).selector,
                "User became canceler not with addCanceler or claimRoot.";
}


// STATUS - verified
// When a delay is changed, it is because setDelay is executed with
// the parameter being the new delay.
rule delayChangesOnlyBySetDelay(env e, method f, bytes32 actionId, bytes32 actionId2) {
    uint256 delayBefore = getActionIdDelay(actionId);
    uint256 delayArg;

    helperSetDelay(e, f, actionId2, delayArg);

    uint256 delayAfter = getActionIdDelay(actionId);

    assert delayAfter != delayBefore =>
        (f.selector == sig:setDelay(bytes32, uint256).selector && actionId2 == actionId);
    assert delayAfter != delayBefore =>
        delayAfter == delayArg;
    assert delayAfter != delayBefore =>
            e.msg.sender == getTimelockExecutionHelper(),
        "Delay changed by other entity than execution helper.";
}


// STATUS - verified
// The array _scheduledExecution is never shortened.
// The length can either stay the same or increase by one.
rule scheduledExecutionsArrayIsNeverShortened(env e, method f) {
    uint256 lengthBefore = getSchedExeLength();

    require(lengthBefore < max_uint256);

    // Invoke any function
    calldataarg args;
    f(e, args);

    uint256 lengthAfter = getSchedExeLength();

    // If the number of scheduled executions changed, it was increased by one.
    assert lengthBefore != lengthAfter =>
        lengthBefore + 1 == to_mathint(lengthAfter),
        "Number of scheduled executions changed and did not increase by one.";
}


// STATUS - verified
// The `_scheduledExecutions` array only changes it's length
// when one of the schedule functions is called.
rule scheduledExecutionsCanBeChangedOnlyByScheduleFunctions(env e, method f) {
    uint256 lengthBefore = getSchedExeLength();

    require(lengthBefore < max_uint256);

    // Invoke any function
    calldataarg args;
    f(e, args);

    uint256 lengthAfter = getSchedExeLength();

    // If the number of scheduled executions changed, it was increased by one.
    assert lengthBefore != lengthAfter =>
        f.selector == sig:scheduleRootChange(address, address[]).selector ||
        f.selector == sig:scheduleDelayChange(bytes32, uint256, address[]).selector ||
        f.selector == sig:scheduleGrantDelayChange(bytes32, uint256, address[]).selector ||
        f.selector == sig:scheduleRevokeDelayChange(bytes32, uint256, address[]).selector ||
        f.selector == sig:schedule(address, bytes, address[]).selector ||
        f.selector == sig:scheduleGrantPermission(bytes32, address, address, address[]).selector ||
        f.selector == sig:scheduleRevokePermission(bytes32, address, address, address[]).selector,
        "Scheduled executions modified by non-schedule function.";
}

// STATUS - verified
// The grant delay of and action (stored in `_grantDelays`) is changed only
// by calling `setGrantDelay` and the caller must be the `_executionHelper`.
rule grantDelaysCanBeChangedOnlyBySetGrantDelay(env e, method f) {
    bytes32 actionId;
    uint256 delayBefore = getActionIdGrantDelay(actionId);

    // Invoke any function
    calldataarg args;
    f(e, args);

    uint256 delayAfter = getActionIdGrantDelay(actionId);

    // If the number of scheduled executions changed, it was increased by one.
    assert delayBefore != delayAfter =>
        f.selector == sig:setGrantDelay(bytes32, uint256).selector,
        "_grantDelays modified by function other than setGrantDelay.";
    assert delayAfter != delayBefore =>
            e.msg.sender == getTimelockExecutionHelper(),
        "Delay changed by other entity than execution helper.";
}


// STATUS - verified
// The revoke delay of and action is changed only
// by calling `setRevokeDelay` and the caller must be the `_executionHelper`.
rule revokeDelaysCanBeChangedOnlyBySetRevokeDelay(env e, method f) {
    bytes32 actionId;
    uint256 delayBefore = getActionIdRevokeDelay(actionId);

    // Invoke any function
    calldataarg args;
    f(e, args);

    uint256 delayAfter = getActionIdRevokeDelay(actionId);

    assert delayBefore != delayAfter =>
        f.selector == sig:setRevokeDelay(bytes32, uint256).selector,
        "_revokeDelays modified by function other than setRevokeDelay.";
    assert delayAfter != delayBefore =>
            e.msg.sender == getTimelockExecutionHelper(),
        "Delay changed by other entity than execution helper.";
}


// STATUS - verified
// Permissions granted on target is removed when:
// `revokePermission` is called by a revoker or the `_executionHelper`
// or when `renouncePermission` is called (by anybody)
// Permissions granted on target is added when `grantPermission` is
// called by the `_executionHelper` or some granter.
rule grantedPermissionsChangeOnlyByAllowedFunctions(env e, method f) {
    bytes32 actionId;
    address account;
    address where;
    bool grantedBefore = isPermissionGrantedOnTarget(actionId, account, where);

    // Invoke any function
    calldataarg args;
    f(e, args);

    bool grantedAfter = isPermissionGrantedOnTarget(actionId, account, where);

    assert grantedBefore && !grantedAfter =>
        f.selector == sig:revokePermission(bytes32, address, address).selector ||
        f.selector == sig:renouncePermission(bytes32,address).selector,
        "permission revoked by function other than revokePermission.";
    assert !grantedBefore && grantedAfter =>
        f.selector == sig:grantPermission(bytes32, address, address).selector,
        "permission granted by function other than grantPermission.";
    assert grantedBefore != grantedAfter =>
        e.msg.sender == getTimelockExecutionHelper() ||
        (grantedAfter && isGranter(actionId, e.msg.sender, where)) ||
        (grantedBefore && (isRevoker(e.msg.sender, where)) || f.selector == sig:renouncePermission(bytes32,address).selector),
        "Granted permission changed by other entity than execution helper or revoker.";
}


// STATUS - verified
// This rule checks, that when a change of delay is scheduled, a new
// ScheduledExecution is created and its executableAt meets, that
// the waiting time for the execution to be executed is at least
// MINIMUM_CHANGE_DELAY_EXECUTION_DELAY. Additionaly, when the delay has
// been lowered, then the time it will take before this execution is executable
// is at least the difference between the old delay and the new delay.
// We assume e.block.timestamp + execution delay < max_uint256
rule scheduleDelayChangeHasProperDelay(env e, bytes32 actionId) {
    uint256 delayBefore = getActionIdDelay(actionId);
    uint256 newDelay;
    address[] executors;
    uint256 numberOfScheduledExecutionsBefore = getSchedExeLength();
    uint256 calculatedDelay = _getDelayChangeExecutionDelay(delayBefore, newDelay);

    require(delayBefore <= MAX_DELAY());
    require(numberOfScheduledExecutionsBefore < max_uint256);

    uint256 executionDelay = _getDelayChangeExecutionDelay(delayBefore, newDelay);
    require(e.block.timestamp + executionDelay < max_uint256);  // avoiding overflow. In the current Ethereum state it is not possible to overflow

    uint256 timestampBefore = e.block.timestamp;

    require(timestampBefore + timestampBefore > to_mathint(timestampBefore));

    scheduleDelayChange(e, actionId, newDelay, executors);

    uint256 numberOfScheduledExecutionsAfter = getSchedExeLength();

    assert to_mathint(numberOfScheduledExecutionsAfter) == numberOfScheduledExecutionsBefore + 1;

    uint256 executableAt = getSchedExeExecutableAt(numberOfScheduledExecutionsBefore);

    assert to_mathint(executableAt) >= timestampBefore + MINIMUM_CHANGE_DELAY_EXECUTION_DELAY();
    assert newDelay <= delayBefore => executableAt - timestampBefore >= delayBefore - newDelay;
}


// STATUS - verified
// ScheduleRootChange creates a new scheduled execution and
// it doesn't change current root nor pending root.
rule scheduleRootChangeCreatesSE(env e) {
    address rootBefore = getRoot();
    address pendingRootBefore = getPendingRoot();
    uint256 numberOfSchedExeBefore = getSchedExeLength();
    address newRoot;
    address[] executors;

    require(numberOfSchedExeBefore < max_uint / 4);

    scheduleRootChange(e, newRoot, executors);

    uint256 numberOfSchedExeAfter = getSchedExeLength();

    assert to_mathint(numberOfSchedExeAfter) == numberOfSchedExeBefore + 1;
    assert rootBefore == getRoot();
    assert pendingRootBefore == getPendingRoot();
}
