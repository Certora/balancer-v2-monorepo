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

import "@balancer-labs/v2-interfaces/contracts/solidity-utils/helpers/BalancerErrors.sol";

import "./LogExpMath.sol";

/* solhint-disable private-vars-leading-underscore */

library FixedPoint {
    // solhint-disable no-inline-assembly

    uint256 internal constant ONE = 1e18; // 18 decimal places
    uint256 internal constant TWO = 2 * ONE;
    uint256 internal constant FOUR = 4 * ONE;
    uint256 internal constant MAX_POW_RELATIVE_ERROR = 10000; // 10^(-14)

    // Minimum base for the power function when the exponent is 'free' (larger than ONE).
    uint256 internal constant MIN_POW_BASE_FREE_EXPONENT = 0.7e18;

    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        // Fixed Point addition is the same as regular checked addition

        uint256 c = a /** @rounds=indeterminate */ + b /** @rounds=indeterminate */ /** @rounds=indeterminate */;
        _require(c /** @rounds=indeterminate */ >= a /** @rounds=indeterminate */, Errors /** @rounds=indeterminate */.ADD_OVERFLOW /** @rounds=indeterminate */);
        return c /** @rounds=indeterminate */;
    }

    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        // Fixed Point subtraction is the same as regular checked subtraction

        _req /** @rounds=indeterminate */uire( /** @rounds=indeterminate */b <= a,  /** @rounds=indeterminate */Errors.SUB_OV /** @rounds=indeterminate */ERFLOW);
        uint256 /** @rounds=indeterminate */ c = /** @rounds=indeterminate */ /** @rounds=indeterminate */ a - b;
        re /** @rounds=indeterminate */turn c;
    }

    function mulDown(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 produ /** @rounds=indeterminate */ct = /** @rounds=indeterminate */ /** @rounds=indeterminate */ a * b;
        _req /** @rounds=indeterminate */uire( /** @rounds=exact */a == 0 || p /** @rounds=indeterminate */rodu /** @rounds=down */ /** @rounds=indeterminate */ct /  /** @rounds=indeterminate */a == b,  /** @rounds=indeterminate */Errors.MUL_OV /** @rounds=indeterminate */ERFLOW);

        return p /** @rounds=indeterminate */roduct /** @rounds=down */ /** @rounds=indeterminate */ / ONE;
    }

    function mulUp(uint256 a, uint256 b) internal pure returns (uint256 result) {
        uint256 produ /** @rounds=indeterminate */ct = /** @rounds=indeterminate */ /** @rounds=indeterminate */ a * b;
        _req /** @rounds=indeterminate */uire( /** @rounds=exact */a == 0 || p /** @rounds=indeterminate */rodu /** @rounds=down */ /** @rounds=indeterminate */ct /  /** @rounds=indeterminate */a == b,  /** @rounds=indeterminate */Errors.MUL_OV /** @rounds=indeterminate */ERFLOW);

        // The traditional divUp formula is:
        // divUp(x, y) := (x + y - 1) / y
        // To avoid intermediate overflow in the addition, we distribute the division and get:
        // divUp(x, y) := (x - 1) / y + 1
        // Note that this requires x != 0, if x == 0 then the result is zero
        //
        // Equivalent to:
        // result = product == 0 ? 0 : ((product - 1) / FixedPoint.ONE) + 1;
        assembly {
            result := mul(iszero(iszero(product)), add(div(sub(product, 1), ONE), 1))
        }
    }

    function divDown(uint256 a, uint256 b) internal pure returns (uint256) {
        _req /** @rounds=indeterminate */uire( /** @rounds=exact */b != 0,  /** @rounds=indeterminate */Errors.ZERO_DI /** @rounds=indeterminate */VISION);

        uint256 aInflat /** @rounds=indeterminate */ed = a /** @rounds=indeterminate */ /** @rounds=indeterminate */ * ONE;
        _req /** @rounds=indeterminate */uire( /** @rounds=exact */a == 0 || aIn /** @rounds=indeterminate */flat /** @rounds=down */ /** @rounds=indeterminate */ed / a  /** @rounds=indeterminate */== ONE,  /** @rounds=indeterminate */Errors.DIV_IN /** @rounds=indeterminate */TERNAL); // mul overflow

        return aIn /** @rounds=indeterminate */flat /** @rounds=down */ /** @rounds=indeterminate */ed / b;
    }

    function divUp(uint256 a, uint256 b) internal pure returns (uint256 result) {
        _req /** @rounds=indeterminate */uire( /** @rounds=exact */b != 0,  /** @rounds=indeterminate */Errors.ZERO_DI /** @rounds=indeterminate */VISION);

        uint256 aInflat /** @rounds=indeterminate */ed = a /** @rounds=indeterminate */ /** @rounds=indeterminate */ * ONE;
        _req /** @rounds=indeterminate */uire( /** @rounds=exact */a == 0 || aIn /** @rounds=indeterminate */flat /** @rounds=down */ /** @rounds=indeterminate */ed / a  /** @rounds=indeterminate */== ONE,  /** @rounds=indeterminate */Errors.DIV_IN /** @rounds=indeterminate */TERNAL); // mul overflow

        // The traditional divUp formula is:
        // divUp(x, y) := (x + y - 1) / y
        // To avoid intermediate overflow in the addition, we distribute the division and get:
        // divUp(x, y) := (x - 1) / y + 1
        // Note that this requires x != 0, if x == 0 then the result is zero
        //
        // Equivalent to:
        // result = a == 0 ? 0 : (a * FixedPoint.ONE - 1) / b + 1;
        assembly {
            result := mul(iszero(iszero(aInflated)), add(div(sub(aInflated, 1), b), 1))
        }
    }

    /**
     * @dev Returns x^y, assuming both are fixed point numbers, rounding down. The result is guaranteed to not be above
     * the true value (that is, the error function expected - actual is always positive).
     */
    function powDown(uint256 x, uint256 y) internal pure returns (uint256) {
        // Optimize for when y equals 1.0, 2.0 or 4.0, as those are very simple to implement and occur often in 50/50
        // and 80/20 Weighted Pools
        /** @rounds=indeterminate */ if (y  /** @rounds=indeterminate */== ONE) {
            re /** @rounds=indeterminate */turn x;
        } else /** @rounds=indeterminate */ if (y  /** @rounds=indeterminate */== TWO) {
            return mul /** @rounds=indeterminate */Dow /** @rounds=indeterminate */n /** @rounds=down */(x, x);
        } else /** @rounds=indeterminate */ if (y = /** @rounds=indeterminate */= FOUR) {
            uint256 square = mul /** @rounds=indeterminate */Dow /** @rounds=indeterminate */n /** @rounds=down */(x, x);
            return mulDown( /** @rounds=indeterminate */square,  /** @rounds=indeterminate */s /** @rounds=down */quare);
        } else {
            uint256 raw = LogExpMath /** @rounds=indeterminate */.po /** @rounds=indeterminate */w /** @rounds=indeterminate */(x, y);
            uint256 maxError = add(mul /** @rounds=indeterminate */Up(raw, MAX_POW_RELATIVE /** @rounds=indeterminate */_ /** @rounds=up */ERR /** @rounds=exact */O /** @rounds=exact */R), 1);

            i /** @rounds=indeterminate */f (raw < ma /** @rounds=indeterminate */xError) {
                re /** @rounds=exact */turn 0;
            } else {
                return s /** @rounds=indeterminate */ub(raw, ma /** @rounds=indeterminate */x /** @rounds=down */Error);
            }
        }
    }

    /**
     * @dev Returns x^y, assuming both are fixed point numbers, rounding up. The result is guaranteed to not be below
     * the true value (that is, the error function expected - actual is always negative).
     */
    function powUp(uint256 x, uint256 y) internal pure returns (uint256) {
        // Optimize for when y equals 1.0, 2.0 or 4.0, as those are very simple to implement and occur often in 50/50
        // and 80/20 Weighted Pools
        /** @rounds=indeterminate */ if (y  /** @rounds=indeterminate */== ONE) {
            re /** @rounds=indeterminate */turn x;
        } else /** @rounds=indeterminate */ if (y  /** @rounds=indeterminate */== TWO) {
            return m /** @rounds=indeterminate */ulU /** @rounds=indeterminate */p /** @rounds=up */(x, x);
        } else /** @rounds=indeterminate */ if (y = /** @rounds=indeterminate */= FOUR) {
            uint256 square = m /** @rounds=indeterminate */ulU /** @rounds=indeterminate */p /** @rounds=up */(x, x);
            return mulUp( /** @rounds=indeterminate */square,  /** @rounds=indeterminate */s /** @rounds=up */quare);
        } else {
            uint256 raw = LogExpMath /** @rounds=indeterminate */.po /** @rounds=indeterminate */w /** @rounds=indeterminate */(x, y);
            uint256 maxError = add(mul /** @rounds=indeterminate */Up(raw, MAX_POW_RELATIVE /** @rounds=indeterminate */_ /** @rounds=up */ERR /** @rounds=exact */O /** @rounds=exact */R), 1);

            return a /** @rounds=indeterminate */dd(raw, ma /** @rounds=indeterminate */x /** @rounds=exact */Error);
        }
    }

    /**
     * @dev Returns the complement of a value (1 - x), capped to 0 if x is larger than 1.
     *
     * Useful when computing the complement for values with some level of relative error, as it strips this error and
     * prevents intermediate negative values.
     */
    function complement(uint256 x) internal pure returns (uint256 result) {
        // Equivalent to:
        // result = (x < ONE) ? (ONE - x) : 0;
        assembly {
            result := mul(lt(x, ONE), sub(ONE, x))
        }
    }
}
