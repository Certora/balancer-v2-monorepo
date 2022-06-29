pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "../munged/pool-stable/contracts/StablePool.sol";

// This is the contract that is actually verified; it may contain some helper
// methods for the spec to access internal state, or may override some of the
// more complex methods in the original contract.
contract StablePoolHarness is StablePool {
    constructor(
        IVault vault,
        string memory name,
        string memory symbol,
        IERC20[] memory tokens, //@audit same token can be added twice in this array
        uint256 amplificationParameter,
        uint256 swapFeePercentage,
        uint256 pauseWindowDuration,
        uint256 bufferPeriodDuration,
        address owner
    ) StablePool(vault, name, symbol, tokens, amplificationParameter, 
    swapFeePercentage, pauseWindowDuration, bufferPeriodDuration, owner) {}
}

