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
