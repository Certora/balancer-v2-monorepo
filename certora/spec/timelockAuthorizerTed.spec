import "erc20.spec"
import "timelockAuthorizerMain.spec"


// STATUS - in progress
// claimRoot is the only function that changes root
// and variables are updated appropriately.
rule rootChangesOnlyWithClaimRoot(env e, method f) {
    address rootBefore = getRoot(e);
    address pendingRootBefore = getPendingRoot(e);

    // Invoke any function
    calldataarg args;
    f(e, args);

    address rootAfter = getRoot(e);

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
