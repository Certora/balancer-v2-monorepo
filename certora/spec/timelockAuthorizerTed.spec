import "erc20.spec"
import "timelockAuthorizerMain.spec"


// STATUS - verified
// claimRoot is the only function that changes root
// and variables are updated appropriately.
// https://prover.certora.com/output/40577/0a8cadb54810435c859098750efa8ee0/?anonymousKey=58e33df6c4063dd4882ec3f40d8b86d816951102
rule rootChangesOnlyWithClaimRoot(env eForPayableFunctions, method f) {
    address rootBefore = getRoot();
    address pendingRootBefore = getPendingRoot();

    // Invoke any function
    calldataarg args;
    f(eForPayableFunctions, args);

    address rootAfter = getRoot();

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


// STATUS - failing as anybody can change pendingRoot. TODO: Is it desired?
// setPendingRoot is the only function that changes pending root
// It can only be called by the root
// https://prover.certora.com/output/40577/fd84cc7fb32d4748b84df810aa5c557d/?anonymousKey=b6913e028107a567c85b7de953db2467f1bb8f8b
rule pendingRootChangesOnlyWithSetPendingRootOrClaimRoot(env e, method f) {
    address pendingRootBefore = getPendingRoot();

    // Invoke any function
    calldataarg args;
    f(e, args);

    address pendingRootAfter = getPendingRoot();

    // if the function f changed the root, then f must be setPendingRoot or claimRoot
    assert pendingRootBefore != pendingRootAfter =>
        ( f.selector == setPendingRoot(address).selector ||
        f.selector == claimRoot().selector ),
        "Pending root changed by a function other than setPendingRoot or claimRoot.";
    // if the function changed the pending root, the sender was root
    assert pendingRootBefore != pendingRootAfter =>
        e.msg.sender == pendingRootBefore,
        "Pending root changed by somebody, who was not root.";
}


// STATUS - verified
// ScheduledExecution that has already been cancelled or executed
// cannot be canceled again.
// https://prover.certora.com/output/40577/0a8cadb54810435c859098750efa8ee0/?anonymousKey=58e33df6c4063dd4882ec3f40d8b86d816951102
rule scheduledExecutionCanBeCancelledOnlyOnce(env e, uint256 index) {
    bool canceled_before = getSchedExeCancelled(index);
    bool executed_before = getSchedExeExecuted(index);

    cancel@withrevert(e, index);
    assert (canceled_before || executed_before) => lastReverted;
}


// STATUS - verified
// ScheduledExecution that has already been cancelled or executed
// cannot be executed again.
// https://prover.certora.com/output/40577/0a8cadb54810435c859098750efa8ee0/?anonymousKey=58e33df6c4063dd4882ec3f40d8b86d816951102
rule scheduledExecutionCanBeExecutedOnlyOnce(env e, uint256 index) {
    bool canceled_before = getSchedExeCancelled(index);
    bool executed_before = getSchedExeExecuted(index);

    execute@withrevert(e, index);
    assert (canceled_before || executed_before) => lastReverted;
}


// STATUS - verified
// Scheduled execution can only be executed by those supplied as executors during scheduling
// https://prover.certora.com/output/40577/f84672d68a6d42498d6899d27b9288a1/?anonymousKey=cf4c6f18c3a8fad6fc659a983a8ed595775a061a
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
// https://prover.certora.com/output/40577/fd84cc7fb32d4748b84df810aa5c557d/?anonymousKey=b6913e028107a567c85b7de953db2467f1bb8f8b
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
                f.selector == removeGranter(bytes32, address, address).selector ||
                f.selector == claimRoot().selector,
                "User ceased to be granter not with removeGranter or claimRoot.";
    assert !isGranterBefore && isGranterAfter =>
                f.selector == addGranter(bytes32, address, address).selector ||
                f.selector == claimRoot().selector,
                "User became granter not with addGranter or claimRoot.";
    assert isGranterBefore != isGranterAfter =>
        e.msg.sender == rootBefore || e.msg.sender == pendingRootBefore,
        "Granter changed by somebody, who was not root or pending root.";
}


// STATUS - verified
// https://prover.certora.com/output/40577/fd84cc7fb32d4748b84df810aa5c557d/?anonymousKey=b6913e028107a567c85b7de953db2467f1bb8f8b
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
                f.selector == removeRevoker(address, address).selector ||
                f.selector == claimRoot().selector,
                "User ceased to be revoker not with removeRevoker or claimRoot.";
    assert !isRevokerBefore && isRevokerAfter =>
                f.selector == addRevoker(address, address).selector ||
                f.selector == claimRoot().selector,
                "User became revoker not with addRevoker or claimRoot.";
    assert isRevokerBefore != isRevokerAfter =>
        e.msg.sender == rootBefore || e.msg.sender == pendingRootBefore,
        "Revoker changed by somebody, who was not root or pending root.";
}


// STATUS - verified
// https://prover.certora.com/output/40577/fd84cc7fb32d4748b84df810aa5c557d/?anonymousKey=b6913e028107a567c85b7de953db2467f1bb8f8b
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
                f.selector == removeCanceler(uint256, address).selector ||
                f.selector == claimRoot().selector,
                "User ceased to be canceler not with removeCanceler or claimRoot.";
    assert !isCancelerBefore && isCancelerAfter =>
                f.selector == addCanceler(uint256, address).selector ||
                f.selector == claimRoot().selector ||
                f.selector == schedule(address,bytes,address[]).selector ||
                f.selector == scheduleRevokePermission(bytes32,address,address,address[]).selector ||
                f.selector == scheduleGrantPermission(bytes32,address,address,address[]).selector,
                "User became canceler not with addCanceler or claimRoot.";
}


// STATUS - verified
// When a delay is changed, it is because setDelay is executed with
// the parameter being the new delay.
// Unresolved call havoc type all contracts except TimelockExecutionHelper:
// https://prover.certora.com/output/40577/fb12ffffa89847579f737148a17ee3c3/?anonymousKey=87bc45cf7a3575f6baaf7702943e8c8dee9ad5d9
rule delayChangesOnlyBySetDelay(env e, method f, bytes32 actionId, bytes32 actionId2) {
    uint256 delayBefore = getActionIdDelay(actionId);
    uint256 delayArg;

    helperSetDelay(e, f, actionId2, delayArg);

    uint256 delayAfter = getActionIdDelay(actionId);

    assert delayAfter != delayBefore =>
        (f.selector == setDelay(bytes32, uint256).selector && actionId2 == actionId);
    assert delayAfter != delayBefore =>
        delayAfter == delayArg;
    assert delayAfter != delayBefore =>
            e.msg.sender == getTimelockExecutionHelper(),
        "Delay changed by other entity than execution helper.";
}


// STATUS - verified
// The array _scheduledExecution is never shortened.
// Unresolved call havoc type all contracts except TimelockExecutionHelper:
// https://prover.certora.com/output/40577/0a8cadb54810435c859098750efa8ee0/?anonymousKey=58e33df6c4063dd4882ec3f40d8b86d816951102
rule scheduledExecutionsArrayIsNeverShortened(env e, method f) {
    uint256 lengthBefore = getSchedExeLength();

    require(lengthBefore < max_uint256);

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
// https://prover.certora.com/output/40577/2ccdf706be7e404e9ada9ecddec30ab8/?anonymousKey=d9e3be8168c4a8290ba7d5480acb9dd4afd7ffb4
rule scheduledExecutionsCanBeChangedOnlyByScheduleFunctions(env e, method f) {
    uint256 lengthBefore = getSchedExeLength();

    require(lengthBefore < max_uint256);

    // Invoke any function
    calldataarg args;
    f(e, args);

    uint256 lengthAfter = getSchedExeLength();

    // If the number of scheduled executions changed, it was increased by one.
    assert lengthBefore != lengthAfter =>
        f.selector == scheduleRootChange(address, address[]).selector ||
        f.selector == scheduleDelayChange(bytes32, uint256, address[]).selector ||
        f.selector == scheduleGrantDelayChange(bytes32, uint256, address[]).selector ||
        f.selector == scheduleRevokeDelayChange(bytes32, uint256, address[]).selector ||
        f.selector == schedule(address, bytes, address[]).selector ||
        f.selector == scheduleGrantPermission(bytes32, address, address, address[]).selector ||
        f.selector == scheduleRevokePermission(bytes32, address, address, address[]).selector,
        "Scheduled executions modified by non-schedule function.";
}

// STATUS - verified
// https://prover.certora.com/output/40577/4fc440c4a1654fdda243cc1a30151573/?anonymousKey=2f909d3f7a3fe4ed878c24c6e69892b127296685
rule grantDelaysCanBeChangedOnlyBySetGrantDelay(env e, method f) {
    bytes32 actionId;
    uint256 delayBefore = getActionIdGrantDelay(actionId);

    // Invoke any function
    calldataarg args;
    f(e, args);

    uint256 delayAfter = getActionIdGrantDelay(actionId);

    // If the number of scheduled executions changed, it was increased by one.
    assert delayBefore != delayAfter =>
        f.selector == setGrantDelay(bytes32, uint256).selector,
        "_grantDelays modified by function other than setGrantDelay.";
    assert delayAfter != delayBefore =>
            e.msg.sender == getTimelockExecutionHelper(),
        "Delay changed by other entity than execution helper.";
}


// STATUS - verified
// https://prover.certora.com/output/40577/457f4ae249cf4f6c96d09aa709578277/?anonymousKey=5c0926936c949b5e66bccc3c1969fbaa236c2e94
rule revokeDelaysCanBeChangedOnlyBySetRevokeDelay(env e, method f) {
    bytes32 actionId;
    uint256 delayBefore = getActionIdRevokeDelay(actionId);

    // Invoke any function
    calldataarg args;
    f(e, args);

    uint256 delayAfter = getActionIdRevokeDelay(actionId);

    // If the number of scheduled executions changed, it was increased by one.
    assert delayBefore != delayAfter =>
        f.selector == setRevokeDelay(bytes32, uint256).selector,
        "_revokeDelays modified by function other than setRevokeDelay.";
    assert delayAfter != delayBefore =>
            e.msg.sender == getTimelockExecutionHelper(),
        "Delay changed by other entity than execution helper.";
}


// STATUS - verified
// grantPermission ... is "granter" or "execution helper"
// revokePermission ... is "revoker" or "execution helper"
// https://prover.certora.com/output/40577/519200fb133e44c0a368c5b8a0ba2363/?anonymousKey=d54f3a36650ac03fe922c8bd52d202b074723321
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
        f.selector == revokePermission(bytes32, address, address).selector ||
        f.selector == renouncePermission(bytes32,address).selector,
        "permission revoked by function other than revokePermission.";
    assert !grantedBefore && grantedAfter =>
        f.selector == grantPermission(bytes32, address, address).selector,
        "permission granted by function other than grantPermission.";
    assert grantedBefore != grantedAfter =>
        e.msg.sender == getTimelockExecutionHelper() ||
        (grantedAfter && isGranter(actionId, e.msg.sender, where)) ||
        (grantedBefore && (isRevoker(e.msg.sender, where)) || f.selector == renouncePermission(bytes32,address).selector),
        "Granted permission changed by other entity than execution helper or revoker.";
}


// STATUS - verified
// This rule checks, that what a change of delay is scheduled, the created
// ScheduledExecution has appropriate executableAt (waiting time to be executed).
// https://prover.certora.com/output/40577/0a8cadb54810435c859098750efa8ee0/?anonymousKey=58e33df6c4063dd4882ec3f40d8b86d816951102
rule scheduleDelayChangeHasProperDelay(env e, env eForPayableFunctions, bytes32 actionId) {
    uint256 delayBefore = getActionIdDelay(actionId);
    uint256 newDelay;
    address[] executors;
    uint256 numberOfScheduledExecutionsBefore = getSchedExeLength();

    require(delayBefore <= MAX_DELAY());
    require(newDelay >= MINIMUM_CHANGE_DELAY_EXECUTION_DELAY());
    require(numberOfScheduledExecutionsBefore < max_uint256);

    uint256 timestampBefore = eForPayableFunctions.block.timestamp;

    require(to_uint256(timestampBefore + timestampBefore) > timestampBefore);

    scheduleDelayChange(eForPayableFunctions, actionId, newDelay, executors);

    uint256 numberOfScheduledExecutionsAfter = getSchedExeLength();

    assert numberOfScheduledExecutionsAfter == numberOfScheduledExecutionsBefore + 1;

    uint256 executableAt = getSchedExeExecutableAt(numberOfScheduledExecutionsBefore);

    assert executableAt >= timestampBefore + MINIMUM_CHANGE_DELAY_EXECUTION_DELAY();
    assert newDelay <= delayBefore =>
        executableAt - timestampBefore >= delayBefore - newDelay;
}


// STATUS - verified
// ScheduleRootChange creates a new scheduled execution and
// it doesn't change current root nor pending root.
// https://prover.certora.com/output/40577/8caf238ec03c439c8441b0676ab9ed71/?anonymousKey=b85e92cf6c33c9b40528d5ee9c8e0b98bc8a620c
rule scheduleRootChangeCreatesSE(env e) {
    address rootBefore = getRoot();
    address pendingRootBefore = getPendingRoot();
    uint256 numberOfSchedExeBefore = getSchedExeLength();
    address newRoot;
    address[] executors;

    require(numberOfSchedExeBefore < max_uint / 4);

    scheduleRootChange(e, newRoot, executors);

    uint256 numberOfSchedExeAfter = getSchedExeLength();

    assert numberOfSchedExeAfter == numberOfSchedExeBefore + 1;
    assert rootBefore == getRoot();
    assert pendingRootBefore == getPendingRoot();
}


//rule loweringDelayRequiresProperWaitingTime(env e) {
    // In this rule we would like to execute any function (parametrical) and say, that if delay of action was lowered,
    // it happened by calling the execute function with scheduledExecution,
    // which has been scheduled before long-enough period of time.

    // This has two problems:
    // 1. We do not have harness for execute
    // 2. We do not store timestamp capturing time, when a ScheduledExecution has been created.

    // This is why I propose to change the way we check this to:
    // 1.
    // 2. Check, that scheduleDelayChange creates execution with correct executableAt. (Done)
    // 3. Check, that when ScheduledExecution is scheduled, it is impossible to execute it before the executableAt time
    //
//}
