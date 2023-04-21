import "timelockAuthorizerMain.spec";


invariant hasPermissionIfIsGrantedOnTarget(bytes32 id, address account, address where)
    isPermissionGrantedOnTarget(id, account, where) => hasPermission(id, account, where)


// STATUS - verified
// https://prover.certora.com/output/40577/43649cf8b8f148a98a7fb83a7647cc34/?anonymousKey=f4c1e5e509629a8ad342dc1997b0cc430264cd84
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
// https://prover.certora.com/output/40577/e38e4eb130054ebb88922acd43f27777/?anonymousKey=d847f9e3d234739e3652f5e73b5d2dce9d404039
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
// claimRoot is the only function that changes root
// and variables are updated appropriately.
// https://prover.certora.com/output/40577/0a8cadb54810435c859098750efa8ee0/?anonymousKey=58e33df6c4063dd4882ec3f40d8b86d816951102
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
// https://vaas-stg.certora.com/output/40577/7efc90865f0f47d09d3d42dab4214400/?anonymousKey=26431befd59fbb32ae6201c42e7f456e7ccceb06
rule pendingRootChangesOnlyWithSetPendingRootOrClaimRoot(env e, method f) {
    address pendingRootBefore = getPendingRoot();
    address executionHelper = getTimelockExecutionHelper();

    // Invoke any function
    calldataarg args;
    f(e, args);

    address pendingRootAfter = getPendingRoot();

    // if the function f changed the root, then f must be setPendingRoot or claimRoot
    assert pendingRootBefore != pendingRootAfter =>
        ( f.selector == sig:setPendingRoot(address).selector ||
        f.selector == sig:claimRoot().selector ),
        "Pending root changed by a function other than setPendingRoot or claimRoot.";
    // if the function changed the pending root, the sender was root
    assert pendingRootBefore != pendingRootAfter =>
        e.msg.sender == pendingRootBefore ||
        e.msg.sender == executionHelper,
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
// https://prover.certora.com/output/40577/0b63385b7d2c4389acfcd10e8e4babfa/?anonymousKey=602c9b0b12b1e83f7625b142d5244a03f6ef6a3c
rule executorCanExecute(env e) {
    uint256 length = getSchedExeLength();
    uint256 id;
    require(id < length);

    bool canExecute = canExecute(e, id);
    bool isExecutor = isExecutor(id, e.msg.sender);
    bool isProtected = getSchedExeProtected(id);

    assert (
        !getSchedExeExecuted(id) &&
        !getSchedExeCancelled(id) &&
        getSchedExeExecutableAt(id) < e.block.timestamp
    ) => canExecute;

    bool executedBefore = getSchedExeExecuted(id);

    execute(e, id);

    bool executedAfter = getSchedExeExecuted(id);

    assert !executedBefore && executedAfter => isExecutor || !isProtected;
    assert canExecute && isExecutor => executedAfter;

    cancel@withrevert(e, id);
    bool reverted = lastReverted;
    assert executedAfter => reverted;
}

// STATUS - verified
// https://prover.certora.com/output/40577/932a5378e8b043c2ac0a07b82dd2e3f3/?anonymousKey=9b663bca7afe0aff0559fe37a922e54193765410
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
// https://prover.certora.com/output/40577/cd669744022849bd8b49be6ca23c2749/?anonymousKey=29341486144142477ebd5eb60b1bf54e90d3b765
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
// Unresolved call havoc type all contracts except TimelockExecutionHelper:
// https://prover.certora.com/output/40577/fb12ffffa89847579f737148a17ee3c3/?anonymousKey=87bc45cf7a3575f6baaf7702943e8c8dee9ad5d9
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
        lengthBefore + 1 == to_mathint(lengthAfter),
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
        f.selector == sig:setGrantDelay(bytes32, uint256).selector,
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
        f.selector == sig:setRevokeDelay(bytes32, uint256).selector,
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
// This rule checks, that what a change of delay is scheduled, the created
// ScheduledExecution has appropriate executableAt (waiting time to be executed).
// We assume e.block.timestamp + new delay < max_uint256
// https://vaas-stg.certora.com/output/40577/41aa47833fe3406c924f0a9e3b0963b0/?anonymousKey=9aadea70b2a378e36ac5016f1bb3dc10df2f94d1
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

    assert to_mathint(numberOfSchedExeAfter) == numberOfSchedExeBefore + 1;
    assert rootBefore == getRoot();
    assert pendingRootBefore == getPendingRoot();
}
