import "erc20.spec"
import "timelockAuthorizerMain.spec"


// STATUS - done
// claimRoot is the only function that changes root
// and variables are updated appropriately.
rule rootChangesOnlyWithClaimRoot(env eForGetters, env eForPayableFunctions, method f) {
    address rootBefore = getRoot(eForGetters);
    address pendingRootBefore = getPendingRoot(eForGetters);

    // Invoke any function
    calldataarg args;
    f(eForPayableFunctions, args);

    address rootAfter = getRoot(eForGetters);

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


// STATUS - done, passing
// ScheduledExecution that has already been cancelled or executed
// cannot be canceled again.
rule scheduledExecutionCanBeCancelledOnlyOnce(env e, uint256 index) {
    bool canceled_before = getSchedExeCancelled(index);
    bool executed_before = getSchedExeExecuted(index);

    // require(canceled_before && !executed_before || !canceled_before && executed_before);
    require(canceled_before || executed_before);

    cancel@withrevert(e, index);
    assert lastReverted;
}


// STATUS - done, passing
// ScheduledExecution that has already been cancelled or executed
// cannot be executed again.
rule scheduledExecutionCanBeExecutedOnlyOnce(env e, uint256 index) {
    bool canceled_before = getSchedExeCancelled(index);
    bool executed_before = getSchedExeExecuted(index);

    // require(canceled_before && !executed_before || !canceled_before && executed_before);
    require(canceled_before || executed_before);

    execute@withrevert(e, index);
    assert lastReverted;
}


// When a delay is changed, it is because setDelay is executed with the parameter being the new delay.
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


function helperSetDelay(env e, method f, bytes32 actionId, uint256 delayArg) {
    if (f.selector == setDelay(bytes32, uint256).selector) {
        setDelay(e, actionId, delayArg);
    } else {
        calldataarg args;
        env e2;
        f(e2, args);
    }
}


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
    assert e.msg.sender == getExecutor(e) || delayAfter <= maximal_delay,
        "Delay of an action is greater than MAX_DELAY.";
}


// The array _scheduledExecution is never shortened.
rule scheduledExecutionsArrayIsNeverShortened(env e, method f) {
    uint256 lengthBefore = getSchedExeLength();

    require(lengthBefore + 1 > lengthBefore);

    // Invoke any function
    calldataarg args;
    f(e, args);

    uint256 lengthAfter = getSchedExeLength();

    // If the number of scheduled executions changed, it was increased by one.
    assert lengthBefore != lengthAfter =>
        lengthBefore + 1 == lengthAfter,
        "Number of scheduled executions changed and did not increase by one.";
}


rule scheduleDelayChangeHasProperDelay(env e, env eForPayableFunctions, bytes32 actionId) {

    uint256 delayBefore = getActionIdDelay(actionId);
    uint256 newDelay;
    address[] executors;
    uint256 numberOfScheduledExecutionsBefore = getSchedExeLength();
    require(delayBefore <= MAX_DELAY());
    require(newDelay <= delayBefore);
    require(newDelay >= MIN_DELAY());
    require(numberOfScheduledExecutionsBefore < max_uint256);

    uint256 timestampBefore = eForPayableFunctions.block.timestamp;
    require(timestampBefore + newDelay + newDelay < max_uint256);
    scheduleDelayChange(eForPayableFunctions, actionId, newDelay, executors);

    uint256 numberOfScheduledExecutionsAfter = getSchedExeLength();
    assert numberOfScheduledExecutionsAfter == numberOfScheduledExecutionsBefore + 1;
    //TODO: assert, that getSchedExeExecutableAt(numberOfScheduledExecutionsBefore)

    uint256 executableAt = getSchedExeExecutableAt(numberOfScheduledExecutionsBefore);
    assert executableAt >= timestampBefore;
    assert executableAt + newDelay >= timestampBefore + delayBefore;
}
