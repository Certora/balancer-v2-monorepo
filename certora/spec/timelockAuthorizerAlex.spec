import "erc20.spec"
import "timelockAuthorizerMain.spec"


/**
 * This rule checks that if the cancelled or executed flag for a scheduled execution changed
 * due to a function call, then the called must have had the permission to do so.
 * cancelled: caller must be the root or hasPermission(actionID, msg.sender, scheduledExecution.where)
 * executed: hasPermission(executeScheduledActionId, msg.sender, address(this))
 */

// rule sanity{
//     env e;
//     bytes4 selector;
//     address where;
//     where.getActionId(e, selector);

//     assert false;
// }

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
    address executer = _executor();
    address _pendingRoot = getPendingRoot();
    calldataarg args;
    
    f(e, args);
    // scheduleGrantPermission(e, args);
    // scheduleRevokePermission(e, args);

    address pendingRoot_ = getPendingRoot();
    assert (_pendingRoot == 0 && pendingRoot_ != 0) => e.msg.sender == executer,"pendingRoot can only be changed by the executer";
}

/**
 * Rule to check that the _root can be changed only by the _pendingRoot
 */
// STATUS: Verified
rule rootChangedOnlyByPendingRoot(method f, env e){
    address _root = _root();
    address _pendingRoot = getPendingRoot();
    calldataarg args;
    f(e, args);

    address root_ = _root();

    assert _root != root_ => e.msg.sender == _pendingRoot,"only pending root can change the root";
}

/**
 * Rule to check that only the root can add a scheduledExecution
 */
// STATUS: in progress
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
// STATUS: in progress
rule monotonicIncreaseOfScheduledExecutionLength(method f, env e){
    uint256 _length = getSchedExeLength();

    calldataarg args;
    f(e, args);

    uint256 length_ = getSchedExeLength();

    assert length_ >= _length,"scheduled execution length cannot decrease";
}

/**
 * Rule to check the access privilege for cancellling an already scheduled execution
 */
// STATUS: in progress
rule whoCanCancelExecution(method f, env e){
    uint256 index;
    bool _cancelled = getSchedExeCancelled(index);
    bytes32 actionId = getActionIdHelper(index);
    address where = getSchedExeWhere(index);
    bool _isRoot = isRoot(e.msg.sender);

    bool _hasPermission = hasPermission(actionId, e.msg.sender, where);

    calldataarg args;
    f(e, args);
    
    bool cancelled_ = getSchedExeCancelled(index);

    assert _cancelled != cancelled_ => _isRoot || _hasPermission,"only the root or an account with the permission of the corresponding actionID and where can cancel a scheduled execution";
}

/**
 * Rule to check change in exected status and the condition/ permission for it.
 */
// STATUS: in progress
rule schExExecutionCheck(method f, env e){
    uint256 index;
    bool _executed = getSchedExeExecuted(index);
    bool protected = getSchedExeProtected(index);
    bytes32 actionId = getActionIdHelper(index);
    address where = getSchedExeWhere(index);

    bool _hasPermission = hasPermission(actionId, e.msg.sender, where);

    calldataarg args;
    f(e, args);
    
    bool executed_ = getSchedExeExecuted(index);

    assert !executed_ => !_executed,"execution cannot be reversed";
    assert _executed != executed_ => !protected || _hasPermission,"only the root or an account with the permission of the corresponding actionID and where can cancel a scheduled execution";
}

rule WhoChangedRoot(method f, env e){
    address _root = _root();
    calldataarg args;
    f(e, args);
    address root_ = _root();

    assert _root == root_;
}