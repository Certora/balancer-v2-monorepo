pragma solidity ^0.7.0;

import "../munged/solidity-utils/contracts/helpers/Authentication.sol";


contract AuthenticationHarness is Authentication {
    constructor(bytes32 actionIdDisambiguator) Authentication(actionIdDisambiguator) {}

    bool canPerform;

    function _canPerform(bytes32 actionId, address user) internal view override returns (bool) {
        return canPerform;
    }
}
