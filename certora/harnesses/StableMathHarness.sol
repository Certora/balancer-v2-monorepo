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

import "../munged/solidity-utils/contracts/math/FixedPoint.sol";
import "../munged/solidity-utils/contracts/math/Math.sol";

// These functions start with an underscore, as if they were part of a contract and not a library. At some point this
// should be fixed. Additionally, some variables have non mixed case names (e.g. P_D) that relate to the mathematical
// derivations.
// solhint-disable private-vars-leading-underscore, var-name-mixedcase

contract StableMath {
    using FixedPoint for uint256;

    uint256 public constant _MIN_AMP = 1;
    uint256 public constant _MAX_AMP = 5000;
    uint256 public constant _AMP_PRECISION = 1e3;

    uint256 public constant _MAX_STABLE_TOKENS = 5;

    bool public beenCalled; 

    constructor() {
        beenCalled = false;
    }

    function _calculateInvariant(uint256 amplificationParameter, uint256[] memory balances)
        public
        returns (uint256)
    {
        beenCalled = true;
        require (amplificationParameter>0 && amplificationParameter<5000); 
        return amplificationParameter * 2;
    }

    
    function _calcOutGivenIn(
        uint256 amplificationParameter,
        uint256[] memory balances,
        uint256 tokenIndexIn,
        uint256 tokenIndexOut,
        uint256 tokenAmountIn,
        uint256 invariant
    ) public returns (uint256) {
        beenCalled = true;
        return tokenAmountIn * 2;
    }

    function _calcInGivenOut(
        uint256 amplificationParameter,
        uint256[] memory balances,
        uint256 tokenIndexIn,
        uint256 tokenIndexOut,
        uint256 tokenAmountOut,
        uint256 invariant
    ) public returns (uint256) {
        beenCalled = true;
        return tokenAmountOut * 2;    
    }

    function _calcBptOutGivenExactTokensIn(
        uint256 amp,
        uint256[] memory balances,
        uint256[] memory amountsIn,
        uint256 bptTotalSupply,
        uint256 currentInvariant,
        uint256 swapFeePercentage
    ) public returns (uint256) {
        beenCalled = true;
        // uint256 input;
        // for (uint256 i; i< amountsIn.length; ++i) {
        //     input += amountsIn[i];
        //     if (input>0)
        //         return input*2;
        // }
        // return 0;
        uint256 input = amountsIn[0];
        input += amountsIn[1];
        if (amountsIn.length>2)
            input += amountsIn[2];
        return input*2;
    }

    function _calcTokenInGivenExactBptOut(
        uint256 amp,
        uint256[] memory balances,
        uint256 tokenIndex,
        uint256 bptAmountOut,
        uint256 bptTotalSupply,
        uint256 currentInvariant,        
        uint256 swapFeePercentage
    ) public returns (uint256) {
        beenCalled = true;
        return bptAmountOut * 2;
    }

    function _calcBptInGivenExactTokensOut(
        uint256 amp,
        uint256[] memory balances,
        uint256[] memory amountsOut,
        uint256 bptTotalSupply,
        uint256 currentInvariant,
        uint256 swapFeePercentage
    ) public returns (uint256) {
        beenCalled = true;
        // uint256 input;
        // for (uint256 i; i< amountsOut.length; ++i) {
        //     input += amountsOut[i];
        //     if (input>0)
        //         return input*2;
        // }
        // return 0;
        uint256 input = amountsOut[0];
        input += amountsOut[1];
        if (amountsOut.length>2)
            input += amountsOut[2];
        return input * 2;
    }

    function _calcTokenOutGivenExactBptIn(
        uint256 amp,
        uint256[] memory balances,
        uint256 tokenIndex,
        uint256 bptAmountIn,
        uint256 bptTotalSupply,
        uint256 currentInvariant,
        uint256 swapFeePercentage
    ) public returns (uint256) {
        beenCalled = true;
        return bptAmountIn * 2;
    }

    function _getTokenBalanceGivenInvariantAndAllOtherBalances(
        uint256 amplificationParameter,
        uint256[] memory balances,
        uint256 invariant,
        uint256 tokenIndex
    ) public returns (uint256) {
        beenCalled = true;
        return invariant * 2;
    }

    function _getRate(
        uint256[] memory balances,
        uint256 amp,
        uint256 supply
    ) public returns (uint256) {
        beenCalled = true;
        require (amp>0 && amp<5000); 
        return amp * 2;
    }
}
