# Properties For Timelock Authorizer

***Valid State*** - MIN_DELAY is not zero

***Valid State*** - `MAX_DELAY + MAX_DELAY >= MAX_DELAY >= MIN_DELAY`

***Variable transition*** - Functions which should change nothing:
`isRoot`,
`isPendingRoot`,
`getActionId`,
`getGrantPermissionActionId`,
`getRevokePermissionActionId`,
`getExecuteExecutionActionId`,
`getScheduleDelayActionId`,
`getExtendedActionId` (note that this one is not a view, but pure),
`getActionIdDelay`,
`getPermissionId` (note that this one is not a view, but pure),
`isPermissionGrantedOnTarget`,
`hasPermission`,
`isGranter`,
`isRevoker`,
`canPerform`,
`canGrant`,
`canRevoke`,
`getScheduledExecution`,
`canExecute`

***Variable transition*** - The following functions can change state of the TimelockAuthorizer:
`scheduleRootChange` (require root),
`setPendingRoot` (require executor),
`claimRoot` (require pending root),
`setDelay` (require executor),
`scheduleDelayChange` (require root),
`schedule` (anybody),
`execute` (anybody),
`cancel` (anybody),
`manageGranter` (),
`grantPermissions` (),
`scheduleGrantPermission` (),
`manageRevoker` (),
`scheduleRevokePermission` (),
`renouncePermissions` ()

***Variable transition*** - When `scheduleRootChange` is called and `msg.sender` is root, then a new scheduled event is created with actionId of `setPendingRoot`.

***Variable transition*** - When `scheduleRootChange` is called and `msg.sender` is not root, then `_pendingRoot`, `_root` remain the same and there is no new scheduled event.

***Variable transition*** - Calling `scheduleRootChange` by root with newRoot == root does not fail.

***Variable transition*** - Only executor can call these functions:
 - `setPendingRoot`
 - `setDelay`

***High-level*** - When `delay` is changed for `action`, then `setDelay` or `scheduleDelayChange` was called.

***Variable transition*** - When `setPendingRoot(pendingRoot)` is called and `msg.sender` is executor, `_pendingRoot` is set to pendingRoot.

***Variable transition*** - When `claimRoot` is called by current _root, who is also pendingRoot, then root remains the same and the _pendingRoot is set to address(0).

***Variable transition*** - When `claimRoot` is called by _pendingRoot, then _root changes to _pendingRoot and _pendingRoot is set to address(0).

***Variable transition*** - When `claimRoot` is called by anybody who is not _pendingRoot or when _pendingRoot is not set, then _root and _pendingRoot remains the same.

***Variable transition*** - When `setDelay` is called by not executor, nothing happens.

***Variable transition*** - When `setDelay` is called by an executor, TODO???

***Variable transition*** - When `scheduleDelayChange(action, newDelay, executors)` is called by root and newDelay <= MAX_DELAY a new actions is scheduled with delay and `delay+newDelay >= delay@before`.

***Note*** - I want to stress out, that method `_schedule` allows scheduling event with delay==1, so greater than `MIN_DELAY`. We need to know if this is right.

***Variable transition*** - When `schedule` is called with where other than `address(this)` and `address(_executor)` and sender has permissions, a new action is scheduled.

***High-level*** - After a root change to a different root, the previous root cannot do things, which only root can.

***Variable transition*** - If root has been changed, it was after calling claimRoot.

***Variable transition*** - manageGranter works:
If msg.sender == root then calling manageGranter results in allowed==isGranter(actionId, account, where).
If msg.sender != root and allowed is set, function does not do anything (fails)
If !allowed && isGranter(actionId, msg.sender, where), then after the call assert(!isGranter(actionId, account, where)).

***Variable transition*** - If manageRevoker makes somebody a revoker for some action, then isRevoker and canRovoke methods return true.
If msg.sender == root then calling manageRevoker results in allowed==isRevoker(actionId, account, where).
If msg.sender != root and allowed is set, function does not do anything (fails)
If !allowed && isRevoker(actionId, msg.sender, where), then after the call assert(!isRevoker(actionId, account, where)).

***Variable transition*** - If manageRevoker makes somebody NOT revoker for some action, then isRevoker and canRovoke methods return false.

***Variable transition*** - Maybe `renouncePermissions` should not be called with `where=TimelockAuthorizer`. I am not sure if we want root/executor to be able to renounce all their permissions.

***Unit tests*** - For permissions that have a delay when granting, `canRevoke` will return false.

***Unit tests*** - After calling grantPermissions with array actionIds larger than array where, the function should not do anything.
***Unit tests*** - 

</br>

---
