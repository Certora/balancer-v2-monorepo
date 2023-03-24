pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "../munged/vault/contracts/authorizer/TimelockAuthorizer.sol";

contract TimelockAuthorizerHarness is TimelockAuthorizer {

    constructor(
        address admin,
        address nextRoot,
        IAuthorizerAdaptorEntrypoint authorizerAdaptorEntrypoint,
        uint256 rootTransferDelay
    ) TimelockAuthorizer(admin, nextRoot, authorizerAdaptorEntrypoint, rootTransferDelay) { }

    function getSchedExeWhere(uint256 index) external view returns (address) {
        return _scheduledExecutions.length <= index ? address(0) : _scheduledExecutions[index].where;
    }

    function getSchedExeData(uint256 index) external view returns (bytes memory) {
        return _scheduledExecutions.length <= index ? bytes("") : _scheduledExecutions[index].data;
    }

    function getSchedExeExecuted(uint256 index) external view returns (bool) {
        return _scheduledExecutions.length <= index ? false : _scheduledExecutions[index].executed;
    }

    function getSchedExeCancelled(uint256 index) external view returns (bool) {
        return _scheduledExecutions.length <= index ? false : _scheduledExecutions[index].cancelled;
    }

    function getSchedExeProtected(uint256 index) external view returns (bool) {
        return _scheduledExecutions.length <= index ? false : _scheduledExecutions[index].protected;
    }

    function getSchedExeExecutableAt(uint256 index) external view returns (uint256) {
        return _scheduledExecutions.length <= index ? 0 : _scheduledExecutions[index].executableAt;
    }

    function getSchedExeLength() external view returns (uint256) {
        return _scheduledExecutions.length;
    }

    // function getGrantActionId() external view returns (bytes4) {
    //     return TimelockAuthorizer.grantPermissions.selector;
    // }

    // function getRevokeActionId() external view returns (bytes4) {
    //     return TimelockAuthorizer.revokePermissions.selector;
    // }

    function getActionIdHelper(uint256 index) external returns(bytes32) {
        ScheduledExecution storage scheduledExecution = _scheduledExecutions[index];
        IAuthentication target = IAuthentication(scheduledExecution.where);
        bytes32 actionId = target.getActionId(_decodeSelector(scheduledExecution.data));
        return actionId;
    }

    function getActionIdFromDataAndWhere(bytes memory data, address where) external returns(bytes32){
        IAuthentication target = IAuthentication(where);
        bytes32 actionId = target.getActionId(_decodeSelector(data));
        return actionId;
    }

    // function returnGetActionIdOfSetPendingRoot() external returns(bytes32) {
    //     return getActionId(this.setPendingRoot.selector);
    // }

    // function getSetAuthorizerActionId() external view returns (bytes32) {
    //     return _vault.getActionId(IVault.setAuthorizer.selector);
    // }
}
