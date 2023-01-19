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

***High-level*** - Solvency - Total supply of tokens is greater or equal to the sum of balances of all users. The system has enough tokens to pay everyone what the deserve.

***Unit tests*** -
***Unit tests*** - 

</br>

---

## Prioritizing

</br>

Once the list of properties is finished, the team meet to discuss it. Each property is explained by its creator to the others, and either being approved, denied or refined.
With every property the team discuss the implications of the property failing, and prioritize them accordingly.

Here is a summary of our prioritization:

### High Priority:

- Property 1 is high priority because user can win the auction and get benefits only once by initial intention. Moreover, `mint()` increases a value of `totalSupply` that can block other auctions to finish if you can claim prize multiple times.

- Properties 2 & 5 are high priority because if they fail the winner will not get his/her deserved reward which fails the entire idea of this system.

- Property 3 is high priority because `mint()` increases a value of `totalSupply` that can block other auctions to finish if you can claim huge prize. Also we want to prevent attacker from getting additional benefits.

- Properties 4 & 7 are high priority because violation of this rule means that attacker can unjustly win an auction without any competition (kind of DoS).

- Property 6 is high priority because we want to prevent DoS attack. Otherwise, there is no reason to participate in such auction.

### Medium Priority:

- Property 8 is medium priority only because there is no withdraw method that could decrease totalSupply to 0 and prevent people from getting their tokens. Otherwise, it's high priority.

### Low Priority:

- Properties 9 & 10 are low priority since:
    1. They check implementation of a specific function (as oppose to multiple functions).
    2. They fairly simple to check by other means, including by manual reviewing of the code.