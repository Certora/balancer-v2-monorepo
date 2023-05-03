import "timelockAuthorizerMain.spec";


invariant notGreaterThanMaxCopy(bytes32 actionId)
    (actionId != getSetAuthorizerActionId() && _delaysPerActionId(getSetAuthorizerActionId()) <= MAX_DELAY()) => _delaysPerActionId(actionId) <= MAX_DELAY()
    {
        preserved setDelay(bytes32 actionId1, uint256 delay) with (env e2) {
            require actionId == actionId1;
        }
    }


// When `isPermissionGrantedOnTarget(id, account, where)` returns `true`, then `hasPermission(id, account, where)` also returns `true`
invariant hasPermissionIfIsGrantedOnTarget(bytes32 id, address account, address where)
    isPermissionGrantedOnTarget(id, account, where) => hasPermission(id, account, where);


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
rule onlyOneRoleChangeAtATimeForNonClaimRoot(env e, method f) filtered {
    f -> f.selector != sig:claimRoot().selector
} {
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

    require(possibleCanceller != otherPossibleCanceller);
    require(possibleRevoker != otherPossibleRevoker);
    require(possibleGranter != otherPossibleGranter);

    // Invoke any function
    calldataarg args;
    f(e, args);

    bool cancelerChanged = cancelerBefore != isCanceler(scheduledExecution, possibleCanceller);
    bool revokerChanged = revokerBefore != isRevoker(possibleRevoker, whereRevoker);
    bool granterChanged = granterBefore != isGranter(actionId, possibleGranter, whereGranter);

    assert cancelerChanged => !revokerChanged && !granterChanged;
    assert revokerChanged => !granterChanged && !cancelerChanged;
    assert granterChanged => !cancelerChanged && !revokerChanged;

    bool otherCancelerChanged = otherCancelerBefore != isCanceler(otherScheduledExecution, otherPossibleCanceller);
    bool otherRevokerChanged = otherRevokerBefore != isRevoker(otherPossibleRevoker, otherWhereRevoker);
    bool otherGranterChanged = otherGranterBefore != isGranter(otherActionId, otherPossibleGranter, otherWhereGranter);

    assert cancelerChanged => !otherCancelerChanged;
    assert revokerChanged => !otherRevokerChanged;
    assert granterChanged => !otherGranterChanged;
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
    assert (pendingRootBefore != pendingRootAfter && pendingRootAfter != 0)
        => e.msg.sender == executionHelper,
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
    uint256 id;
    address user;
    require limitArrayLength();
    require (id < getSchedExeLength());
    bool isExecutor = isExecutor(id, user);

    // Invoke any function
    calldataarg args;
    f(e, args);

    assert !isExecutor => !isExecutor(id, user),
        "User became an executor after the scheduled execution has been scheduled.";
}


// STATUS - verified
// An execution can be executed (`canExecute`) when it has not yet been cancelled
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
    uint256 length;
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
// The `_scheduledExecutions` array only changes its length
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
// The grant delay of an action (stored in `_grantDelays`) is changed only
// by calling `setGrantDelay` and the caller must be the `_executionHelper`.
rule grantDelaysCanBeChangedOnlyBySetGrantDelay(env e, method f) {
    bytes32 actionId;
    uint256 delayBefore = getActionIdGrantDelay(actionId);

    // Invoke any function
    calldataarg args;
    f(e, args);

    uint256 delayAfter = getActionIdGrantDelay(actionId);

    assert delayBefore != delayAfter =>
        f.selector == sig:setGrantDelay(bytes32, uint256).selector,
        "_grantDelays modified by function other than setGrantDelay.";
    assert delayAfter != delayBefore =>
            e.msg.sender == getTimelockExecutionHelper(),
        "Delay changed by other entity than execution helper.";
}


// STATUS - verified
// The revoke delay of an action is changed only
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

    requireInvariant notGreaterThanMaxCopy(actionId);
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

    require limitArrayLength();

    scheduleRootChange(e, newRoot, executors);

    uint256 numberOfSchedExeAfter = getSchedExeLength();

    assert to_mathint(numberOfSchedExeAfter) == numberOfSchedExeBefore + 1;
    assert rootBefore == getRoot();
    assert pendingRootBefore == getPendingRoot();
}