import "timelockAuthorizerMain.spec";



// /**
//  * Rule to check that the _pendingRoot can be changed only by the executor
//  * Replaced by stronger pendingRootChangesOnlyWithSetPendingRootOrClaimRoot
//  */
// STATUS: Verified
// rule pendingRootChangeOnlyByExecutor(method f, env e){
//     bool isExecutor      = e.msg.sender == getTimelockExecutionHelper();
//     address _pendingRoot = getPendingRoot();
//     calldataarg args;

//     f(e, args);

//     address pendingRoot_ = getPendingRoot();
//     assert (_pendingRoot == 0 && pendingRoot_ != 0) => isExecutor, "pendingRoot can only be changed by the executer";
// }

// /**
//  * Rule to check that the _root can be changed only by the _pendingRoot
//  * Commented out as rootChangesOnlyWithClaimRoot is stronger.
//  */
// // STATUS: Verified
// rule rootChangedOnlyByPendingRoot(method f, env e){
//     address _root           = getRoot();
//     address _pendingRoot    = getPendingRoot();

//     calldataarg args;
//     f(e, args);

//     address root_           = getRoot();

//     assert _root != root_ => e.msg.sender == _pendingRoot,"only pending root can change the root";
// }

// /**
//  * Rule to check that the scheduledExecution array can only increase in length
//  * Commented out as scheduledExecutionsArrayIsNeverShortened is stronger.
//  */
// // STATUS: Verified
// // https://vaas-stg.certora.com/output/11775/fbdbf344b011d569e7a7/?anonymousKey=32c8fc3829f77691b50b091df7798b73fc51dcd2
// rule monotonicIncreaseOfScheduledExecutionLength(method f, env e){
//     uint256 _length = getSchedExeLength();
//     require _length < max_uint256;
//     calldataarg args;
//     f(e, args);

//     uint256 length_ = getSchedExeLength();

//     assert length_ >= _length,"scheduled execution length cannot decrease";
// }

/**
 * Rule to check the access privilege for cancellling an already scheduled execution
 */
// STATUS: Verified
// https://vaas-stg.certora.com/output/11775/7b1a794b6a263a14632e/?anonymousKey=7f40bbaccc123cc47e3a1bd745a9a0bdb13b8e78
rule whoCanCancelExecution(method f, env e){
    uint256 index;
    bool _cancelled  = getSchedExeCancelled(index);
    bool _isCanceler = isCanceler(index, e.msg.sender);
    require limitArrayLength();
    require index    < getSchedExeLength();

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
// https://vaas-stg.certora.com/output/11775/ecb18fb6c4126ebcb8fc/?anonymousKey=2665ea0baeb63f53a7f67641ed18ef18ed88031c
rule schExExecutionCheck(method f, env e) {
    uint256 index;
    bool _executed      = getSchedExeExecuted(index);
    bool protected      = getSchedExeProtected(index);
    bytes32 actionId    = getActionIdHelper(index);
    address where       = getSchedExeWhere(index);
    bool _hasPermission = hasPermission(actionId, e.msg.sender, where);
    require index       < getSchedExeLength();
    require limitArrayLength();

    calldataarg args;
    f(e, args);

    bool executed_      = getSchedExeExecuted(index);

    assert !executed_ => !_executed,"execution cannot be reversed";
    assert _executed != executed_ => !protected || _hasPermission;
}

// /**
//  * Rule to check only the executor can change delays.
//  * Replaced by delayChangesOnlyBySetDelay (stronger).
//  */
// // STATUS: Verified
// // https://vaas-stg.certora.com/output/11775/b4275f9fd1a4d31dc76e/?anonymousKey=0418a2c8f8a9f36046b64e2ce34dec49c1808120
// rule delayPerActionIdChangeAccess(method f, env e){
//     bytes32 actionID;
//     uint256 _delay  = getActionIdDelay(actionID);
//     bool isExecutor = e.msg.sender == getTimelockExecutionHelper();

//     calldataarg args;
//     f(e, args);

//     uint256 delay_ = getActionIdDelay(actionID);

//     // assert _delay == delay_;
//     assert delay_ != _delay => isExecutor,"only executor should be able to change delaysPerActionID";
// }

/**
 * A scheduled execution cannot be executed before the executableAt time
 */
// STATUS: Verified
// https://vaas-stg.certora.com/output/11775/a9fcc103e081a3c63600/?anonymousKey=6daa0dd98a2b7c92f20b1f2e3cd0cc0bdeed483d
rule schExeNotExecutedBeforeTime(method f, env e){
    uint256 index;
    uint256 executableAt = getSchedExeExecutableAt(index);
    uint256 length = getSchedExeLength();
    bool _executed = getSchedExeExecuted(index);

    calldataarg args;
    f(e, args);

    bool executed_ = getSchedExeExecuted(index);

    assert !_executed && executed_ => e.block.timestamp >= executableAt,
        "cannot execute an execution before executableAt time";
}

// /**
//  * A rule to check that only pendingRoot can become the new Root
//  * Commented out as rootChangesOnlyWithClaimRoot is stronger.
//  */
// // STATUS: Verified
// // https://vaas-stg.certora.com/output/11775/d9fddcc284739529e05d/?anonymousKey=3848d16e8c96553a5e8faf7ca9a4b3fb134bb058
// rule onlyPendingRootCanBecomeNewRoot(method f, env e){
//     address _pendingRoot = _pendingRoot();
//     address _root = getRoot();

//     calldataarg args;
//     f(e, args);

//     address root_ = getRoot();

//     assert root_ == _root || root_ == _pendingRoot,
//         "root can either remain unchanged or change to the pendingRoot";
// }