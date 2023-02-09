import "erc20.spec"
import "timelockAuthorizerMain.spec"


/**
 * This rule checks that if the cancelled or executed flag for a scheduled execution changed
 * due to a function call, then the called must have had the permission to do so.
 * cancelled: caller must be the root or hasPermission(actionID, msg.sender, scheduledExecution.where)
 * executed: hasPermission(executeScheduledActionId, msg.sender, address(this))
 */

//  rule checkPermissionForCancellingExecuting(method f, env e){

//     // scheduling and action

//     // there is a scheduled execution with a state before
//     uint256 index;
//     bool _cancelled = getSchedExeCancelled(index);
//     bool _executed = getSchedExeExecuted(index);
//     address where = getSchedExeWhere(index);

//     bool isRoot = e.msg.sender == _root();
//     bytes32 actionId = where.getActionId(_decodeSelector(getSchedExeData(index)));
    
//     f(e, args);
    
//     bool cancelled_ = getSchedExeCancelled(index);
//     bool executed_ = getSchedExeExecuted(index);

//     assert 
//  }

/**
 * Rule to check that the _pendingRoot can be changed only by the executor
 */
// STATUS: Verified
rule pendingRootChangeOnlyByExecutor(method f, env e){
    address executer        = _executor();
    address _pendingRoot    = getPendingRoot();
    calldataarg args;
    
    f(e, args);

    address pendingRoot_    = getPendingRoot();
    assert (_pendingRoot == 0 && pendingRoot_ != 0) => e.msg.sender == executer,"pendingRoot can only be changed by the executer";
}

// rule whoChangedPendingRoot(method f, env e){

// }

/**
 * Rule to check that the _root can be changed only by the _pendingRoot
 */
// STATUS: Verified
rule rootChangedOnlyByPendingRoot(method f, env e){
    address _root           = _root();
    address _pendingRoot    = getPendingRoot();
    
    calldataarg args;
    f(e, args);

    address root_           = _root();

    assert _root != root_ => e.msg.sender == _pendingRoot,"only pending root can change the root";
}


/**
 * Rule to check that only the root can add a scheduledExecution
 */
// STATUS: FAILING
// fails for schedule(), scheduleRevokePermission() and scheduleGrantPermission() 
// that create a new scheduledExecution that does not require the caller to be the root.
// https://vaas-stg.certora.com/output/11775/563831424bdd396a192e/?anonymousKey=e21e47ed98096788ec82c386e0bca74088910bee
rule scheduledExecutionLengthIncreaseByRootOnly(method f, env e){
    uint256 _length = getSchedExeLength();
    
    calldataarg args;
    f(e, args);

    uint256 length_ = getSchedExeLength();

    assert _length != length_ => e.msg.sender == _root(),"scheduled execution length can be changed only by the root";
}

/**
 * Rule to check that the scheduledExecution array can only increase in length
 */
// STATUS: Verified
// https://vaas-stg.certora.com/output/11775/fbdbf344b011d569e7a7/?anonymousKey=32c8fc3829f77691b50b091df7798b73fc51dcd2
rule monotonicIncreaseOfScheduledExecutionLength(method f, env e){
    uint256 _length = getSchedExeLength();
    require _length < max_uint256;
    calldataarg args;
    f(e, args);

    uint256 length_ = getSchedExeLength();

    assert length_ >= _length,"scheduled execution length cannot decrease";
}

/**
 * Rule to check the access privilege for cancellling an already scheduled execution
 */
// STATUS: Verified
// https://vaas-stg.certora.com/output/11775/7b1a794b6a263a14632e/?anonymousKey=7f40bbaccc123cc47e3a1bd745a9a0bdb13b8e78
rule whoCanCancelExecution(method f, env e){
    uint256 index;
    uint256 length      = getSchedExeLength();
    bool _cancelled     = getSchedExeCancelled(index);
    bytes32 actionId    = getActionIdHelper(index);
    address where       = getSchedExeWhere(index);
    bool _isRoot        = isRoot(e.msg.sender);
    bool _hasPermission = hasPermission(actionId, e.msg.sender, where);
    require index       < length;
    require length      < max_uint256;
    require getSchedExeLength() < max_uint / 4;

    calldataarg args;
    f(e, args);
    
    bool cancelled_     = getSchedExeCancelled(index);

    assert _cancelled != cancelled_ => _isRoot || _hasPermission,
    "only the root or an account with the permission of the corresponding actionID and where can cancel a scheduled execution";
}

/**
 * Rule to check change in executed status and the condition/ permission for it.
 */
// STATUS: Verified
// https://vaas-stg.certora.com/output/11775/ecb18fb6c4126ebcb8fc/?anonymousKey=2665ea0baeb63f53a7f67641ed18ef18ed88031c
rule schExExecutionCheck(method f, env e){
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
 * Rule to check only the executor can change delays.
 */
// STATUS: Verified
rule delayPerActionIdChangeAccess(method f, env e){
    bytes32 actionID;
    uint256 _delay = getActionIdDelay(actionID);
    address executor = _executor();

    calldataarg args;
    f(e, args);

    uint256 delay_ = getActionIdDelay(actionID);

    // assert _delay == delay_;
    assert delay_ != _delay => e.msg.sender == executor,"only executor should be able to change delaysPerActionID";
}

rule whoChangedDelay(method f, env e){
    bytes32 actionID;
    uint256 _delay = getActionIdDelay(actionID);
    
    calldataarg args;
    f(e, args);
    
    uint256 delay_ = getActionIdDelay(actionID);

    assert _delay == delay_;    
}


rule WhoChangedRoot(method f, env e){
    address _root = _root();
    calldataarg args;
    f(e, args);
    address root_ = _root();

    assert _root == root_;
}

rule delayedActionExecutionOnlyByExecutor(method f, env e){
    // there is an execution with an actionID that has a delay

    // f

    // execution is executed

}