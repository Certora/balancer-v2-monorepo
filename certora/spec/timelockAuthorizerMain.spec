import "erc20.spec"

// using MockVault as MockVault
using Vault as Vault

methods {
    // Summarization
    execute(address, bytes) returns(bytes) => DISPATCHER(true)
    getActionId(bytes4) returns(bytes32) => DISPATCHER(true)        // what is the "target/where" in cancel()? "where" in schedule?   setDelay()
    sendTo() returns(bool, bytes) => DISPATCHER(true)

    // TimelockAuthorizerHarness.sol
    getSchedExeWhere(uint256) returns(address) envfree
    getSchedExeData(uint256) returns(bytes) envfree
    getSchedExeExecuted(uint256) returns(bool) envfree
    getSchedExeCancelled(uint256) returns(bool) envfree
    getSchedExeProtected(uint256) returns(bool) envfree
    getSchedExeExecutableAt(uint256) returns(uint256) envfree
    getSchedExeLength() returns(uint256) envfree
    getGrantActionId() returns(bytes4) envfree
    getRevokeActionId() returns(bytes4) envfree
    getActionIdHelper(uint256) returns (bytes32) envfree
    getActionIdFromDataAndWhere(bytes, address) returns(bytes32) envfree
    returnGetActionIdOfSetPendingRoot() returns(bytes32) envfree

    returnDataForScheduleGrantPermission(bytes32, address, address) returns(bytes) envfree

    // TimelockAuthorizer.sol constants
    EVERYWHERE() returns(address) envfree
    MIN_DELAY() returns(uint256) envfree
    MAX_DELAY() returns(uint256) envfree
    GENERAL_PERMISSION_SPECIFIER() returns(bytes32) envfree
    GRANT_ACTION_ID() returns(bytes32) envfree
    _GENERAL_GRANT_ACTION_ID() returns(bytes32) envfree
    _GENERAL_REVOKE_ACTION_ID() returns(bytes32) envfree

    // TimelockAuthorizer.sol
    getActionIdDelay(bytes32) returns(uint256) envfree
    getActionId(bytes4) returns (bytes32) envfree
    _isPermissionGranted(bytes32) returns(bool) envfree
    getPermissionId(bytes32, address, address) returns(bytes32) envfree
    _root() returns(address) envfree
    _pendingRoot() returns(address) envfree
    _executor() returns(address) envfree
    getExecuteExecutionActionId(uint256) returns(bytes32) envfree
    getExtendedActionId(bytes32, bytes32) returns(bytes32) envfree
    getPendingRoot() returns(address) envfree
    hasPermission(bytes32, address, address) returns (bool) envfree
    isRoot(address) returns (bool) envfree
    _authorizerAdaptorEntrypoint() returns (address) envfree
    _authorizerAdaptor() returns (address) envfree
    _delaysPerActionId(bytes32) returns(uint256) envfree
    getExecutor() returns(address) envfree
}

definition limitArrayLength() returns bool = getSchedExeLength() < max_uint / 4;

rule sanity(env e, method f) {
    calldataarg args;
    f(e, args);
    assert false;
}
