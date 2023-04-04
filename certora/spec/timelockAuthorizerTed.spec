import "erc20.spec"
import "timelockAuthorizerMain.spec"


rule sanity(env e, method f) {
    calldataarg args;
    f(e, args);
    assert false;
}


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


// STATUS - failing
// setPendingRoot is the only function that changes pending root
// It can only be called by the root
rule pendingRootChangesOnlyWithSetPendingRootOrClaimRoot(env eForPayableFunctions, method f) {
    address rootBefore = getRoot();
    address pendingRootBefore = getPendingRoot();

    // Invoke any function
    calldataarg args;
    f(eForPayableFunctions, args);

    address pendingRootAfter = getPendingRoot();

    // if the function f changed the root, then f must be setPendingRoot or claimRoot
    assert pendingRootBefore != pendingRootAfter =>
        ( f.selector == setPendingRoot(address).selector ||
        f.selector == claimRoot().selector ),
        "Pending root changed by a function other than setPendingRoot or claimRoot.";
    // if the function changed the pending root, the sender was root
    assert pendingRootBefore != pendingRootAfter =>
        eForPayableFunctions.msg.sender == rootBefore,
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
// When a delay is changed, it is because setDelay is executed with
// the parameter being the new delay.
// Unresolved call havoc type all contracts except TimelockExecutionHelper:
// https://prover.certora.com/output/40577/0a8cadb54810435c859098750efa8ee0/?anonymousKey=58e33df6c4063dd4882ec3f40d8b86d816951102
rule delayChangesOnlyBySetDelay(env e, method f, bytes32 actionId, bytes32 actionId2) {
    uint256 delayBefore = getActionIdDelay(actionId);
    uint256 delayArg;

    helperSetDelay(e, f, actionId2, delayArg);

    uint256 delayAfter = getActionIdDelay(actionId);

    assert delayAfter != delayBefore =>
        (f.selector == setDelay(bytes32, uint256).selector && actionId2 == actionId);
    assert delayAfter != delayBefore =>
        delayAfter == delayArg;
}


// STATUS - failing
// Delays of actions are less or equal to MAX_DELAY.
rule delaysOfActionsHaveUpperBound(env e, method f, bytes32 actionId) {
    uint256 delayBefore = getActionIdDelay(actionId);
    uint256 maximal_delay = MAX_DELAY();

    require(delayBefore <= maximal_delay);

    // Invoke any function
    calldataarg args;
    f(e, args);

    uint256 delayAfter = getActionIdDelay(actionId);

    // Note: TODO: allow the executor to change delay in any way.
    assert delayAfter <= maximal_delay,
        "Delay of an action is greater than MAX_DELAY.";
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
// https://prover.certora.com/output/40577/0a8cadb54810435c859098750efa8ee0/?anonymousKey=58e33df6c4063dd4882ec3f40d8b86d816951102
rule scheduleRootChangeCreatesSE(env e) {
    address rootBefore = getRoot();
    address pendingRootBefore = getPendingRoot();
    uint256 numberOfSchedExeBefore = getSchedExeLength();
    address newRoot;
    address[] executors;

    require newRoot != rootBefore;
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
