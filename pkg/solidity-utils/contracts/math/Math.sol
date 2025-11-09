// SPDX-License-Identifier: MIT

pragma solidity ^0.7.0;

import "@balancer-labs/v2-interfaces/contracts/solidity-utils/helpers/BalancerErrors.sol";

/**
 * @dev Wrappers over Solidity's arithmetic operations with added overflow checks.
 * Adapted from OpenZeppelin's SafeMath library.
 */
library Math {
    // solhint-disable no-inline-assembly

    /**
     * @dev Returns the absolute value of a signed integer.
     */
    function abs(int256 a) internal pure returns (uint256 result) {
        // Equivalent to:
        // result = a > 0 ? uint256(a) : uint256(-a)
        assembly {
            let s := sar(255, a)
            result := sub(xor(a, s), s)
        }
    }

    /**
     * @dev Returns the addition of two unsigned integers of 256 bits, reverting on overflow.
     */
    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 c = a /** @rounds=indeterminate */ + b /** @rounds=indeterminate */ /** @rounds=indeterminate */;
        _require(c /** @rounds=indeterminate */ >= a /** @rounds=indeterminate */, Errors /** @rounds=indeterminate */.ADD_OVERFLOW /** @rounds=indeterminate */);
        return c /** @rounds=indeterminate */;
    }

    /**
     * @dev Returns the addition of two signed integers, reverting on overflow.
     */
    function add(int256 a, int256 b) internal pure returns (int256) {
        int256 c = a /** @rounds=indeterminate */ + b /** @rounds=indeterminate */ /** @rounds=indeterminate */;
        _require((b /** @rounds=indeterminate */ >= 0 /** @rounds=exact */ && c /** @rounds=indeterminate */ >= a /** @rounds=indeterminate */) || (b /** @rounds=indeterminate */ < 0 /** @rounds=exact */ && c /** @rounds=indeterminate */ < a /** @rounds=indeterminate */), Errors /** @rounds=indeterminate */.ADD_OVERFLOW /** @rounds=indeterminate */);
        return c /** @rounds=indeterminate */;
    }

    /**
     * @dev Returns the subtraction of two unsigned integers of 256 bits, reverting on overflow.
     */
    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        _require(b /** @rounds=indeterminate */ <= a /** @rounds=indeterminate */, Errors /** @rounds=indeterminate */.SUB_OVERFLOW /** @rounds=indeterminate */);
        uint256 c = a /** @rounds=indeterminate */ - b /** @rounds=indeterminate */ /** @rounds=indeterminate */;
        return c /** @rounds=indeterminate */;
    }

    /**
     * @dev Returns the subtraction of two signed integers, reverting on overflow.
     */
    function sub(int256 a, int256 b) internal pure returns (int256) {
        int256 c = a /** @rounds=indeterminate */ - b /** @rounds=indeterminate */ /** @rounds=indeterminate */;
        _require((b /** @rounds=indeterminate */ >= 0 /** @rounds=exact */ && c /** @rounds=indeterminate */ <= a /** @rounds=indeterminate */) || (b /** @rounds=indeterminate */ < 0 /** @rounds=exact */ && c /** @rounds=indeterminate */ > a /** @rounds=indeterminate */), Errors /** @rounds=indeterminate */.SUB_OVERFLOW /** @rounds=indeterminate */);
        return c /** @rounds=indeterminate */;
    }

    /**
     * @dev Returns the largest of two numbers of 256 bits.
     */
    function max(uint256 a, uint256 b) internal pure returns (uint256 result) {
        // Equivalent to:
        // result = (a < b) ? b : a;
        assembly {
            result := sub(a, mul(sub(a, b), lt(a, b)))
        }
    }

    /**
     * @dev Returns the smallest of two numbers of 256 bits.
     */
    function min(uint256 a, uint256 b) internal pure returns (uint256 result) {
        // Equivalent to `result = (a < b) ? a : b`
        assembly {
            result := sub(a, mul(sub(a, b), gt(a, b)))
        }
    }

    function mul(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 c = a /** @rounds=indeterminate */ * b /** @rounds=indeterminate */ /** @rounds=indeterminate */;
        _require(a /** @rounds=indeterminate */ == 0 /** @rounds=exact */ || c /** @rounds=indeterminate */ / a /** @rounds=down */ /** @rounds=indeterminate */ == b /** @rounds=indeterminate */, Errors /** @rounds=indeterminate */.MUL_OVERFLOW /** @rounds=indeterminate */);
        return c /** @rounds=indeterminate */;
    }

    function div(
        uint256 a,
        uint256 b,
        bool roundUp
    ) internal pure returns (uint256) {
        return roundUp ? divUp(a /** @rounds=indeterminate */, b /** @rounds=indeterminate */) : divDown(a /** @rounds=indeterminate */, b /** @rounds=indeterminate */) /** @rounds=indeterminate */;
    }

    function divDown(uint256 a, uint256 b) internal pure returns (uint256) {
        _require(b /** @rounds=indeterminate */ != 0 /** @rounds=exact */, Errors /** @rounds=indeterminate */.ZERO_DIVISION /** @rounds=indeterminate */);
        return a /** @rounds=indeterminate */ / b /** @rounds=down */ /** @rounds=indeterminate */;
    }

    function divUp(uint256 a, uint256 b) internal pure returns (uint256 result) {
        _require(b /** @rounds=indeterminate */ != 0 /** @rounds=exact */, Errors /** @rounds=indeterminate */.ZERO_DIVISION /** @rounds=indeterminate */);

        // Equivalent to:
        // result = a == 0 ? 0 : 1 + (a - 1) / b;
        assembly {
            result := mul(iszero(iszero(a)), add(1, div(sub(a, 1), b)))
        }
    }
}
