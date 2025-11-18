
pragma solidity ^0.7.0;

import "@balancer-labs/v2-solidity-utils/contracts/math/FixedPoint.sol";

contract InvCalculator {
    using FixedPoint for uint256;

    function cvl_calculateInvariant(uint256 amplificationParameter, uint256[] memory balances)
        external
        pure
        returns (uint256)
    {
        uint256 sum = 0; // S in the Curve version
        uint256 numTokens = balances.length;
        for (uint256 i = 0; i < numTokens; i++) {
            sum = sum.add(balances[i]);
        }
        return sum;
    }
}