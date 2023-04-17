// SPDX-License-Identifier: GPL-3.0-or-later
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "@balancer-labs/v2-interfaces/contracts/liquidity-mining/IAuthorizerAdaptorEntrypoint.sol";
import "@balancer-labs/v2-interfaces/contracts/vault/IVault.sol";
import "@balancer-labs/v2-interfaces/contracts/vault/IAuthorizer.sol";
import "@balancer-labs/v2-interfaces/contracts/vault/ITimelockAuthorizer.sol";

// import "@balancer-labs/v2-solidity-utils/contracts/openzeppelin/Address.sol";
import "../../../../harness/Address.sol";   // HARNESS: Using harnessed Address.sol (harnessing low-level code) instead of OZ(above)
import "@balancer-labs/v2-solidity-utils/contracts/openzeppelin/ReentrancyGuard.sol";
import "./TimelockExecutionHelper.sol";

/**
 * @title Timelock Authorizer Management
 * @author Balancer Labs
 * @dev TimelockAuthorizerManagement is a parent class for TimelockAuthorizer introduced to bring more
 * clarity and readability into TimelockAuthorizer smart contract. It handles logic for handling a root change
 * (`setPendingRoot` and 'claimRoot'), scheduling and executing actions (`_scheduleWithDelay`, `execute`, and
 * `cancel`), and managing roles (`addRevoker`, `addGranter`, `addCanceler`).
 *
 * See `TimelockAuthorizer`
 */
abstract contract TimelockAuthorizerManagement is ITimelockAuthorizer, ReentrancyGuard {
    using Address for address;

    // solhint-disable-next-line const-name-snakecase
    address private constant _EVERYWHERE = address(-1);

    // solhint-disable-next-line const-name-snakecase
    uint256 internal constant _GLOBAL_CANCELER_SCHEDULED_EXECUTION_ID = type(uint256).max;

    TimelockExecutionHelper public immutable _executionHelper;     // HARNESS: removed immutable, private -> public
    IAuthentication internal immutable _vault;                       // HARNESS: removed immutable, private -> internal
    uint256 private immutable _rootTransferDelay;

    // Authorizer permissions
    address public _root;                   // HARNESS: private -> public
    address public _pendingRoot;            // HARNESS: private -> public

    // scheduled execution id => account => is executor
    mapping(uint256 => mapping(address => bool)) public _isExecutor;           // HARNESS: private -> public

    // action id => account => where => is granter
    mapping(bytes32 => mapping(address => mapping(address => bool))) public _isGranter;        // HARNESS: private -> public
    // account => where => is revoker
    mapping(address => mapping(address => bool)) public _isRevoker;            // HARNESS: private -> public
    // scheduled execution id => account => is canceler
    mapping(uint256 => mapping(address => bool)) public _isCanceler;           // HARNESS: private -> public

    ITimelockAuthorizer.ScheduledExecution[] public _scheduledExecutions;       // HARNESS: private -> public

    /**
     * @dev Prevents a TimelockAuthorizer function from being called directly, making it only possible to call it by
     * scheduling a delayed execution.
     *
     * Each function that has this modifier applied to it should have an associated function that performs proper
     * permission validation and then schedules a call.
     */
    modifier onlyScheduled() {
        // Checking that we're being called by the TimelockExecutionHelper is a sufficient check, given that:
        //
        //  1) The TimelockExecutionHelper can only make external calls (and cause this modifier to not revert) if
        //     called by the TimelockAuthorizer.
        //
        //  2) The TimelockAuthorizer only makes external non-view calls in a single place: when the `execute` function
        //    is called by an executor. This is the only possible time it could call the TimelockExecutionHelper.
        //
        //  3) `execute` can only be called after scheduling a delayed execution.
        //
        //  4) Scheduled delayed executions either target the TimelockAuthorizer directly (such as in
        //    `scheduleRootChange` or `scheduleDelayChange`), in which case this modifier will not revert (as intended,
        //    given those functions check proper permissions), or explictly forbid targeting the TimelockAuthorizer
        //    (in the `schedule` function), making it impossible for the TimelockExecutionHelper to call into it.
        require(msg.sender == address(_executionHelper), "CAN_ONLY_BE_SCHEDULED");
        _;
    }

    constructor(
        address initialRoot,
        address nextRoot,
        IAuthentication vault,
        uint256 rootTransferDelay
    ) {
        _setRoot(initialRoot);
        // By setting `nextRoot` as the pending root, it can immediately call `claimRoot` and replace `initialRoot`,
        // skipping the root transfer delay for the very first root transfer. This is very useful in schemes where a
        // migrator contract is the initial root and performs some initial setup, and then needs to transfer this
        // permission to some other account.
        _setPendingRoot(nextRoot);

        _vault = vault;
        _executionHelper = new TimelockExecutionHelper();
        _rootTransferDelay = rootTransferDelay;
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    // solhint-disable-next-line func-name-mixedcase
    function EVERYWHERE() public pure override returns (address) {
        return _EVERYWHERE;
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    // solhint-disable-next-line func-name-mixedcase
    function GLOBAL_CANCELER_SCHEDULED_EXECUTION_ID() public pure override returns (uint256) {
        return _GLOBAL_CANCELER_SCHEDULED_EXECUTION_ID;
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function isRoot(address account) public view override returns (bool) {
        return account == _root;
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function isPendingRoot(address account) public view override returns (bool) {
        return account == _pendingRoot;
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function getRootTransferDelay() public view override returns (uint256) {
        return _rootTransferDelay;
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function getVault() public view override returns (address) {
        return address(_vault);
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function getTimelockExecutionHelper() public view override returns (address) {
        return address(_executionHelper);
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function getRoot() external view override returns (address) {
        return _root;
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function getPendingRoot() external view override returns (address) {
        return _pendingRoot;
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function isGranter(
        bytes32 actionId,
        address account,
        address where
    ) public view override returns (bool) {
        return _isGranter[actionId][account][where] || _isGranter[actionId][account][EVERYWHERE()] || isRoot(account);
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function isRevoker(address account, address where) public view override returns (bool) {
        return _isRevoker[account][where] || _isRevoker[account][EVERYWHERE()] || isRoot(account);
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function getScheduledExecution(uint256 scheduledExecutionId)
        external
        view
        override
        returns (ITimelockAuthorizer.ScheduledExecution memory)
    {
        return _scheduledExecutions[scheduledExecutionId];
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function isExecutor(uint256 scheduledExecutionId, address account) public view override returns (bool) {
        return _isExecutor[scheduledExecutionId][account];
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function canExecute(uint256 scheduledExecutionId) external view override returns (bool) {
        require(scheduledExecutionId < _scheduledExecutions.length, "ACTION_DOES_NOT_EXIST");

        ITimelockAuthorizer.ScheduledExecution storage scheduledExecution = _scheduledExecutions[scheduledExecutionId];
        return
            !scheduledExecution.executed &&
            !scheduledExecution.cancelled &&
            block.timestamp >= scheduledExecution.executableAt;
        // solhint-disable-previous-line not-rely-on-time
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function isCanceler(uint256 scheduledExecutionId, address account) public view override returns (bool) {
        return
            _isCanceler[scheduledExecutionId][account] ||
            _isCanceler[GLOBAL_CANCELER_SCHEDULED_EXECUTION_ID()][account] ||
            isRoot(account);
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function scheduleRootChange(address newRoot, address[] memory executors) external override returns (uint256) {
        require(isRoot(msg.sender), "SENDER_IS_NOT_ROOT");
        bytes memory data = abi.encodeWithSelector(this.setPendingRoot.selector, newRoot);

        // Since this can only be called by root, which is always a canceler for all scheduled executions, we don't
        // bother creating any new cancelers.
        uint256 scheduledExecutionId = _scheduleWithDelay(address(this), data, getRootTransferDelay(), executors);

        emit RootChangeScheduled(newRoot, scheduledExecutionId);
        return scheduledExecutionId;
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function setPendingRoot(address pendingRoot) external override onlyScheduled {
        _setPendingRoot(pendingRoot);
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function claimRoot() external override {
        address pendingRoot = _pendingRoot;
        require(msg.sender == pendingRoot, "SENDER_IS_NOT_PENDING_ROOT");

        // Complete the root transfer and reset the pending root.
        _setRoot(pendingRoot);
        _setPendingRoot(address(0));
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function execute(uint256 scheduledExecutionId) external override nonReentrant returns (bytes memory result) {
        require(scheduledExecutionId < _scheduledExecutions.length, "ACTION_DOES_NOT_EXIST");

        ITimelockAuthorizer.ScheduledExecution storage scheduledExecution = _scheduledExecutions[scheduledExecutionId];
        require(!scheduledExecution.executed, "ACTION_ALREADY_EXECUTED");
        require(!scheduledExecution.cancelled, "ACTION_ALREADY_CANCELLED");

        // solhint-disable-next-line not-rely-on-time
        require(block.timestamp >= scheduledExecution.executableAt, "ACTION_NOT_YET_EXECUTABLE");

        if (scheduledExecution.protected) {
            // Protected scheduled executions can only be executed by a set of accounts designated by the original
            // scheduler.
            require(isExecutor(scheduledExecutionId, msg.sender), "SENDER_IS_NOT_EXECUTOR");
        }

        scheduledExecution.executed = true;

        // Note that this is the only place in the entire contract we perform a non-view call to an external contract,
        // i.e. this is the only context in which this contract can be re-entered, and by this point we've already
        // completed all state transitions.
        // This results in the scheduled execution being marked as 'executed' during its execution, but that should not
        // be an issue.
        result = _executionHelper.execute(scheduledExecution.where, scheduledExecution.data);
        emit ExecutionExecuted(scheduledExecutionId);
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function cancel(uint256 scheduledExecutionId) external override {
        require(scheduledExecutionId < _scheduledExecutions.length, "ACTION_DOES_NOT_EXIST");

        ITimelockAuthorizer.ScheduledExecution storage scheduledExecution = _scheduledExecutions[scheduledExecutionId];

        require(!scheduledExecution.executed, "ACTION_ALREADY_EXECUTED");
        require(!scheduledExecution.cancelled, "ACTION_ALREADY_CANCELLED");

        require(isCanceler(scheduledExecutionId, msg.sender), "SENDER_IS_NOT_CANCELER");

        scheduledExecution.cancelled = true;
        emit ExecutionCancelled(scheduledExecutionId);
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function addCanceler(uint256 scheduledExecutionId, address account) external override {
        require(isRoot(msg.sender), "SENDER_IS_NOT_ROOT");
        _addCanceler(scheduledExecutionId, account);
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function removeCanceler(uint256 scheduledExecutionId, address account) external override {
        require(isRoot(msg.sender), "SENDER_IS_NOT_ROOT");

        // The root account is always a canceler, and this cannot be revoked.
        require(!isRoot(account), "CANNOT_REMOVE_ROOT_CANCELER");

        if (_isCanceler[GLOBAL_CANCELER_SCHEDULED_EXECUTION_ID()][account]) {
            // If an account is a global canceler, then it must explicitly lose this global privilege. This prevents
            // scenarios where an account has their canceler status revoked over a specific scheduled execution id, but
            // they can still cancel it because they have global permission.
            // There's an edge case in which an account could have both specific and global cancel privilege, and still
            // be able to cancel some scheduled executions after losing global privilege. This is considered an unlikely
            // scenario, and would require manual removal of the specific canceler privileges even after removal
            // of the global one.
            require(scheduledExecutionId == GLOBAL_CANCELER_SCHEDULED_EXECUTION_ID(), "ACCOUNT_IS_GLOBAL_CANCELER");
        } else {
            // Alternatively, they must currently be a canceler in order to be revoked.
            require(_isCanceler[scheduledExecutionId][account], "ACCOUNT_IS_NOT_CANCELER");
        }

        _isCanceler[scheduledExecutionId][account] = false;
        emit CancelerRemoved(scheduledExecutionId, account);
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function addGranter(
        bytes32 actionId,
        address account,
        address where
    ) external override {
        require(isRoot(msg.sender), "SENDER_IS_NOT_ROOT");

        require(!isGranter(actionId, account, where), "ACCOUNT_IS_ALREADY_GRANTER");
        // Note that it is possible for `account` to be a granter for the same `actionId` in some specific `where`, and
        // then be granted permission over `EVERYWHERE`, resulting in 'duplicate' permissions. This is not an issue per
        // se, but removing this granter status will require undoing these actions in inverse order.
        // To avoid these issues, it is recommended to revoke any prior granter status over specific contracts before
        // making an account a global granter.

        _isGranter[actionId][account][where] = true;
        emit GranterAdded(actionId, account, where);
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function removeGranter(
        bytes32 actionId,
        address account,
        address where
    ) external override {
        require(isRoot(msg.sender), "SENDER_IS_NOT_ROOT");

        require(isGranter(actionId, account, where), "ACCOUNT_IS_NOT_GRANTER");

        require(!isRoot(account), "CANNOT_REMOVE_ROOT_GRANTER");

        // On top of requiring that the account is currently a granter, we prevent attempts to revoke permission over a
        // single contract from global granters. As mentioned in `addGranter`, it is possible for an account to have
        // both global and specific permissions over a given contract: in this case, the global permission must be
        // removed before the specific ones can be addressed.
        if (_isGranter[actionId][account][EVERYWHERE()]) {
            require(where == EVERYWHERE(), "GRANTER_IS_GLOBAL");
        }

        _isGranter[actionId][account][where] = false;
        emit GranterRemoved(actionId, account, where);
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function addRevoker(address account, address where) external override {
        require(isRoot(msg.sender), "SENDER_IS_NOT_ROOT");

        require(!isRevoker(account, where), "ACCOUNT_IS_ALREADY_REVOKER");
        // Note that it's possible for the `account` to be a revoker in a specific `where`, and
        // later receive permission over `EVERYWHERE()`, resulting in 'duplicate' permissions. While this isn't
        // necessarily an issue, removing the revoker status will require undoing the actions in reverse order.
        // To avoid these issues, it's recommended to remove any prior revoker status over specific contracts before
        // granting an account global revoker.

        _isRevoker[account][where] = true;
        emit RevokerAdded(account, where);
    }

    /**
     * @inheritdoc ITimelockAuthorizer
     */
    function removeRevoker(address account, address where) external override {
        require(isRoot(msg.sender), "SENDER_IS_NOT_ROOT");

        require(isRevoker(account, where), "ACCOUNT_IS_NOT_REVOKER");

        require(!isRoot(account), "CANNOT_REMOVE_ROOT_REVOKER");

        // On top of requiring that the account is currently a revoker, we prevent attempts to remove permission over a
        // single contract from global revokers. As mentioned in `addRevoker`, it is possible for an account to have
        // both global and specific permissions over a given contract: in this case, the global permission must be
        // removed before the specific ones can be addressed.
        if (_isRevoker[account][EVERYWHERE()]) {
            require(where == EVERYWHERE(), "REVOKER_IS_GLOBAL");
        }

        _isRevoker[account][where] = false;
        emit RevokerRemoved(account, where);
    }

    /**
     * @dev Schedules an execution of `data` at contract `where` with a `delay`
     * allowing only `executors` to invoke the action after the delay.
     *
     * This performs no permission checks on `msg.sender` of any kind. The caller of this function should perform
     * any appropriate checks.
     */
    function _scheduleWithDelay(
        address where,
        bytes memory data,
        uint256 delay,
        address[] memory executors
    ) internal returns (uint256 scheduledExecutionId) {
        scheduledExecutionId = _scheduledExecutions.length;

        // solhint-disable-next-line not-rely-on-time
        uint256 executableAt = block.timestamp + delay;
        bool protected = executors.length > 0;

        _scheduledExecutions.push(
            ITimelockAuthorizer.ScheduledExecution({
                where: where,
                data: data,
                executed: false,
                cancelled: false,
                protected: protected,
                executableAt: executableAt
            })
        );

        for (uint256 i = 0; i < executors.length; i++) {
            require(!_isExecutor[scheduledExecutionId][executors[i]], "DUPLICATE_EXECUTORS");
            // Note that we allow for repeated executors - this is not an issue
            _isExecutor[scheduledExecutionId][executors[i]] = true;
            emit ExecutorAdded(scheduledExecutionId, executors[i]);
        }
    }

    /**
     * @dev Sets the root address to `root`.
     */
    function _setRoot(address root) internal {
        _root = root;
        emit RootSet(root);
    }

    /**
     * @dev Does not check that caller is root
     *
     * See `addCanceler` comments.
     */
    function _addCanceler(uint256 scheduledExecutionId, address account) internal {
        require(!isCanceler(scheduledExecutionId, account), "ACCOUNT_IS_ALREADY_CANCELER");

        _isCanceler[scheduledExecutionId][account] = true;
        emit CancelerAdded(scheduledExecutionId, account);
    }

    /**
     * @dev Sets the pending root address to `pendingRoot`.
     */
    function _setPendingRoot(address pendingRoot) internal {
        _pendingRoot = pendingRoot;
        emit PendingRootSet(pendingRoot);
    }
}
