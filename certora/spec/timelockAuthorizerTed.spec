import "erc20.spec"
import "timelockAuthorizerMain.spec"


// STATUS - in progress
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


// ScheduledExecution that has already been cancelled or executed
// cannot be executed nor canceled again.
rule scheduledExecutionCanCancelOrScheduleOnlyOnce(env e, method f, uint256 index) {
    bool canceled_before = getSchedExeCancelled(index);
    bool executed_before = getSchedExeExecuted(index);

    // require(canceled_before && !executed_before || !canceled_before && executed_before);
    require(canceled_before || executed_before);

    calldataarg args;
    f@withrevert(e, args);
    bool isReverted = lastReverted; // lastReverted is bool, true iff the last function call was reverted
    assert f.selector == cancel(uint256).selector
        || f.selector == execute(uint256).selector
        => isReverted;
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
