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

import "@balancer-labs/v2-solidity-utils/contracts/math/FixedPoint.sol";
import "@balancer-labs/v2-solidity-utils/contracts/math/Math.sol";

// These functions start with an underscore, as if they were part of a contract and not a library. At some point this
// should be fixed. Additionally, some variables have non mixed case names (e.g. P_D) that relate to the mathematical
// derivations.
// solhint-disable private-vars-leading-underscore, var-name-mixedcase

library StableMath {
    using FixedPoint for uint256;

    uint256 internal constant _MIN_AMP = 1;
    uint256 internal constant _MAX_AMP = 5000;
    uint256 internal constant _AMP_PRECISION = 1e3;

    uint256 internal constant _MAX_STABLE_TOKENS = 5;

    // Note on unchecked arithmetic:
    // This contract performs a large number of additions, subtractions, multiplications and divisions, often inside
    // loops. Since many of these operations are gas-sensitive (as they happen e.g. during a swap), it is important to
    // not make any unnecessary checks. We rely on a set of invariants to avoid having to use checked arithmetic (the
    // Math library), including:
    //  - the number of tokens is bounded by _MAX_STABLE_TOKENS
    //  - the amplification parameter is bounded by _MAX_AMP * _AMP_PRECISION, which fits in 23 bits
    //  - the token balances are bounded by 2^112 (guaranteed by the Vault) times 1e18 (the maximum scaling factor),
    //    which fits in 172 bits
    //
    // This means e.g. we can safely multiply a balance by the amplification parameter without worrying about overflow.

    // About swap fees on joins and exits:
    // Any join or exit that is not perfectly balanced (e.g. all single token joins or exits) is mathematically
    // equivalent to a perfectly balanced join or  exit followed by a series of swaps. Since these swaps would charge
    // swap fees, it follows that (some) joins and exits should as well.
    // On these operations, we split the token amounts in 'taxable' and 'non-taxable' portions, where the 'taxable' part
    // is the one to which swap fees are applied.

    // Computes the invariant given the current balances, using the Newton-Raphson approximation.
    // The amplification parameter equals: A n^(n-1)
    // See: https://github.com/curvefi/curve-contract/blob/b0bbf77f8f93c9c5f4e415bce9cd71f0cdee960e/contracts/pool-templates/base/SwapTemplateBase.vy#L206
    // solhint-disable-previous-line max-line-length
    function _calculateInvariant(uint256 amplificationParameter, uint256[] memory balances)
        internal
        pure
        returns (uint256)
    {
        /**********************************************************************************************
        // invariant                                                                                 //
        // D = invariant                                                  D^(n+1)                    //
        // A = amplification coefficient      A  n^n S + D = A D n^n + -----------                   //
        // S = sum of balances                                             n^n P                     //
        // P = product of balances                                                                   //
        // n = number of tokens                                                                      //
        **********************************************************************************************/

        // Always round down, to match Vyper's arithmetic (which always truncates).

        uint256 sum = 0 /** @rounds=exact */; // S in the Curve version
        uint256 numTokens = balances /** @rounds=indeterminate */.length /** @rounds=indeterminate */;
        for (uint256 i = 0 /** @rounds=exact */; i /** @rounds=indeterminate */ < numTokens /** @rounds=indeterminate */; i++) {
            sum = sum.add(balances[i] /** @rounds=indeterminate */) /** @rounds=exact */;
        }
        if (sum /** @rounds=indeterminate */ == 0 /** @rounds=exact */) {
            return 0 /** @rounds=exact */;
        }

        uint256 prevInvariant; // Dprev in the Curve version
        uint256 invariant = sum /** @rounds=indeterminate */; // D in the Curve version
        uint256 ampTimesTotal = amplificationParameter /** @rounds=indeterminate */ * numTokens /** @rounds=indeterminate */ /** @rounds=indeterminate */; // Ann in the Curve version

        for (uint256 i = 0 /** @rounds=exact */; i /** @rounds=indeterminate */ < 255 /** @rounds=exact */; i++) {
            uint256 D_P = invariant /** @rounds=indeterminate */;

            for (uint256 j = 0 /** @rounds=exact */; j /** @rounds=indeterminate */ < numTokens /** @rounds=indeterminate */; j++) {
                // (D_P * invariant) / (balances[j] * numTokens)
                D_P = Math.divDown(Math.mul(D_P /** @rounds=indeterminate */, invariant /** @rounds=indeterminate */) /** @rounds=indeterminate */, Math.mul(balances[j] /** @rounds=indeterminate */, numTokens /** @rounds=indeterminate */) /** @rounds=indeterminate */) /** @rounds=down */;
            }

            prevInvariant = invariant /** @rounds=indeterminate */;

            invariant = Math.divDown(
                Math.mul(
                    // (ampTimesTotal * sum) / AMP_PRECISION + D_P * numTokens
                    (Math.divDown(Math.mul(ampTimesTotal, sum), _AMP_PRECISION).add(Math.mul(D_P /** @rounds=indeterminate */, numTokens /** @rounds=indeterminate */) /** @rounds=indeterminate */)) /** @rounds=indeterminate */,
                    invariant /** @rounds=indeterminate */
                ) /** @rounds=indeterminate */,
                // ((ampTimesTotal - _AMP_PRECISION) * invariant) / _AMP_PRECISION + (numTokens + 1) * D_P
                (
                    Math.divDown(Math.mul((ampTimesTotal - _AMP_PRECISION), invariant), _AMP_PRECISION).add(
                        Math.mul((numTokens /** @rounds=indeterminate */ + 1 /** @rounds=exact */) /** @rounds=indeterminate */, D_P /** @rounds=indeterminate */) /** @rounds=indeterminate */
                    )
                ) /** @rounds=indeterminate */
            ) /** @rounds=down */;

            if (invariant /** @rounds=indeterminate */ > prevInvariant /** @rounds=indeterminate */) {
                if (invariant /** @rounds=indeterminate */ - prevInvariant /** @rounds=indeterminate */ /** @rounds=indeterminate */ <= 1 /** @rounds=exact */) {
                    return invariant /** @rounds=indeterminate */;
                }
            } else if (prevInvariant /** @rounds=indeterminate */ - invariant /** @rounds=indeterminate */ /** @rounds=indeterminate */ <= 1 /** @rounds=exact */) {
                return invariant /** @rounds=indeterminate */;
            }
        }

        _revert(Errors /** @rounds=indeterminate */.STABLE_INVARIANT_DIDNT_CONVERGE /** @rounds=indeterminate */);
    }

    // Computes how many tokens can be taken out of a pool if `tokenAmountIn` are sent, given the current balances.
    // The amplification parameter equals: A n^(n-1)
    function _calcOutGivenIn(
        uint256 amplificationParameter,
        uint256[] memory balances,
        uint256 tokenIndexIn,
        uint256 tokenIndexOut,
        uint256 tokenAmountIn,
        uint256 invariant
    ) internal pure returns (uint256) {
        /**************************************************************************************************************
        // outGivenIn token x for y - polynomial equation to solve                                                   //
        // ay = amount out to calculate                                                                              //
        // by = balance token out                                                                                    //
        // y = by - ay (finalBalanceOut)                                                                             //
        // D = invariant                                               D                     D^(n+1)                 //
        // A = amplification coefficient               y^2 + ( S + ----------  - D) * y -  ------------- = 0         //
        // n = number of tokens                                    (A * n^n)               A * n^2n * P              //
        // S = sum of final balances but y                                                                           //
        // P = product of final balances but y                                                                       //
        **************************************************************************************************************/

        // Amount out, so we round down overall.
        balances[tokenIndexIn] = balances[tokenIndexIn].add(tokenAmountIn /** @rounds=indeterminate */) /** @rounds=exact */;

        uint256 finalBalanceOut = _getTokenBalanceGivenInvariantAndAllOtherBalances(
            amplificationParameter /** @rounds=indeterminate */,
            balances /** @rounds=indeterminate */,
            invariant /** @rounds=indeterminate */,
            tokenIndexOut /** @rounds=indeterminate */
        ) /** @rounds=indeterminate */;

        // No need to use checked arithmetic since `tokenAmountIn` was actually added to the same balance right before
        // calling `_getTokenBalanceGivenInvariantAndAllOtherBalances` which doesn't alter the balances array.
        balances[tokenIndexIn] = balances[tokenIndexIn] /** @rounds=indeterminate */ - tokenAmountIn /** @rounds=indeterminate */ /** @rounds=indeterminate */;

        return balances[tokenIndexOut].sub(finalBalanceOut).sub(1 /** @rounds=exact */) /** @rounds=down */;
    }

    // Computes how many tokens must be sent to a pool if `tokenAmountOut` are sent given the
    // current balances, using the Newton-Raphson approximation.
    // The amplification parameter equals: A n^(n-1)
    function _calcInGivenOut(
        uint256 amplificationParameter,
        uint256[] memory balances,
        uint256 tokenIndexIn,
        uint256 tokenIndexOut,
        uint256 tokenAmountOut,
        uint256 invariant
    ) internal pure returns (uint256) {
        /**************************************************************************************************************
        // inGivenOut token x for y - polynomial equation to solve                                                   //
        // ax = amount in to calculate                                                                               //
        // bx = balance token in                                                                                     //
        // x = bx + ax (finalBalanceIn)                                                                              //
        // D = invariant                                                D                     D^(n+1)                //
        // A = amplification coefficient               x^2 + ( S + ----------  - D) * x -  ------------- = 0         //
        // n = number of tokens                                     (A * n^n)               A * n^2n * P             //
        // S = sum of final balances but x                                                                           //
        // P = product of final balances but x                                                                       //
        **************************************************************************************************************/

        // Amount in, so we round up overall.
        balances[tokenIndexOut] = balances[tokenIndexOut].sub(tokenAmountOut /** @rounds=indeterminate */) /** @rounds=down */;

        uint256 finalBalanceIn = _getTokenBalanceGivenInvariantAndAllOtherBalances(
            amplificationParameter /** @rounds=indeterminate */,
            balances /** @rounds=indeterminate */,
            invariant /** @rounds=indeterminate */,
            tokenIndexIn /** @rounds=indeterminate */
        ) /** @rounds=indeterminate */;  /// GOAL: MAKE THIS @rounds=up

        // No need to use checked arithmetic since `tokenAmountOut` was actually subtracted from the same balance right
        // before calling `_getTokenBalanceGivenInvariantAndAllOtherBalances` which doesn't alter the balances array.
        balances[tokenIndexOut] = balances[tokenIndexOut] /** @rounds=indeterminate */ + tokenAmountOut /** @rounds=indeterminate */ /** @rounds=indeterminate */;

        return finalBalanceIn.sub(balances[tokenIndexIn]).add(1 /** @rounds=exact */) /** @rounds=exact */;
    }

    function _calcBptOutGivenExactTokensIn(
        uint256 amp,
        uint256[] memory balances,
        uint256[] memory amountsIn,
        uint256 bptTotalSupply,
        uint256 currentInvariant,
        uint256 swapFeePercentage
    ) internal pure returns (uint256) {
        // BPT out, so we round down overall.

        // First loop calculates the sum of all token balances, which will be used to calculate
        // the current weights of each token, relative to this sum
        uint256 sumBalances = 0 /** @rounds=exact */;
        for (uint256 i = 0 /** @rounds=exact */; i /** @rounds=indeterminate */ < balances /** @rounds=indeterminate */.length /** @rounds=indeterminate */; i++) {
            sumBalances = sumBalances.add(balances[i] /** @rounds=indeterminate */) /** @rounds=exact */;
        }

        // Calculate the weighted balance ratio without considering fees
        uint256[] memory balanceRatiosWithFee = new uint256[](amountsIn /** @rounds=indeterminate */.length /** @rounds=indeterminate */) /** @rounds=indeterminate */;
        // The weighted sum of token balance ratios with fee
        uint256 invariantRatioWithFees = 0 /** @rounds=exact */;
        for (uint256 i = 0 /** @rounds=exact */; i /** @rounds=indeterminate */ < balances /** @rounds=indeterminate */.length /** @rounds=indeterminate */; i++) {
            uint256 currentWeight = balances[i].divDown(sumBalances /** @rounds=indeterminate */) /** @rounds=down */;
            balanceRatiosWithFee[i] = balances[i].add(amountsIn[i]).divDown(balances[i] /** @rounds=indeterminate */) /** @rounds=down */;
            invariantRatioWithFees = invariantRatioWithFees.add(balanceRatiosWithFee[i].mulDown(currentWeight /** @rounds=indeterminate */) /** @rounds=down */) /** @rounds=exact */;
        }

        // Second loop calculates new amounts in, taking into account the fee on the percentage excess
        uint256[] memory newBalances = new uint256[](balances /** @rounds=indeterminate */.length /** @rounds=indeterminate */) /** @rounds=indeterminate */;
        for (uint256 i = 0 /** @rounds=exact */; i /** @rounds=indeterminate */ < balances /** @rounds=indeterminate */.length /** @rounds=indeterminate */; i++) {
            uint256 amountInWithoutFee;

            // Check if the balance ratio is greater than the ideal ratio to charge fees or not
            if (balanceRatiosWithFee[i] /** @rounds=indeterminate */ > invariantRatioWithFees /** @rounds=indeterminate */) {
                uint256 nonTaxableAmount = balances[i].mulDown(invariantRatioWithFees.sub(FixedPoint /** @rounds=indeterminate */.ONE /** @rounds=indeterminate */) /** @rounds=down */) /** @rounds=down */;
                uint256 taxableAmount = amountsIn[i].sub(nonTaxableAmount /** @rounds=indeterminate */) /** @rounds=down */;
                // No need to use checked arithmetic for the swap fee, it is guaranteed to be lower than 50%
                amountInWithoutFee = nonTaxableAmount.add(taxableAmount.mulDown(FixedPoint /** @rounds=indeterminate */.ONE /** @rounds=indeterminate */ - swapFeePercentage /** @rounds=indeterminate */ /** @rounds=indeterminate */) /** @rounds=down */) /** @rounds=exact */;
            } else {
                amountInWithoutFee = amountsIn[i] /** @rounds=indeterminate */;
            }

            newBalances[i] = balances[i].add(amountInWithoutFee /** @rounds=indeterminate */) /** @rounds=exact */;
        }

        uint256 newInvariant = _calculateInvariant(amp /** @rounds=indeterminate */, newBalances /** @rounds=indeterminate */) /** @rounds=indeterminate */;
        uint256 invariantRatio = newInvariant.divDown(currentInvariant /** @rounds=indeterminate */) /** @rounds=down */;

        // If the invariant didn't increase for any reason, we simply don't mint BPT
        if (invariantRatio /** @rounds=indeterminate */ > FixedPoint /** @rounds=indeterminate */.ONE /** @rounds=indeterminate */) {
            return bptTotalSupply.mulDown(invariantRatio /** @rounds=indeterminate */ - FixedPoint /** @rounds=indeterminate */.ONE /** @rounds=indeterminate */ /** @rounds=indeterminate */) /** @rounds=down */;
        } else {
            return 0 /** @rounds=exact */;
        }
    }

    function _calcTokenInGivenExactBptOut(
        uint256 amp,
        uint256[] memory balances,
        uint256 tokenIndex,
        uint256 bptAmountOut,
        uint256 bptTotalSupply,
        uint256 currentInvariant,
        uint256 swapFeePercentage
    ) internal pure returns (uint256) {
        // Token in, so we round up overall.

        uint256 newInvariant = bptTotalSupply.add(bptAmountOut).divUp(bptTotalSupply).mulUp(currentInvariant /** @rounds=indeterminate */) /** @rounds=up */;

        // Calculate amount in without fee.
        uint256 newBalanceTokenIndex = _getTokenBalanceGivenInvariantAndAllOtherBalances(
            amp /** @rounds=indeterminate */,
            balances /** @rounds=indeterminate */,
            newInvariant /** @rounds=indeterminate */,
            tokenIndex /** @rounds=indeterminate */
        ) /** @rounds=indeterminate */;
        uint256 amountInWithoutFee = newBalanceTokenIndex.sub(balances[tokenIndex] /** @rounds=indeterminate */) /** @rounds=down */;

        // First calculate the sum of all token balances, which will be used to calculate
        // the current weight of each token
        uint256 sumBalances = 0 /** @rounds=exact */;
        for (uint256 i = 0 /** @rounds=exact */; i /** @rounds=indeterminate */ < balances /** @rounds=indeterminate */.length /** @rounds=indeterminate */; i++) {
            sumBalances = sumBalances.add(balances[i] /** @rounds=indeterminate */) /** @rounds=exact */;
        }

        // We can now compute how much extra balance is being deposited and used in virtual swaps, and charge swap fees
        // accordingly.
        uint256 currentWeight = balances[tokenIndex].divDown(sumBalances /** @rounds=indeterminate */) /** @rounds=down */;
        uint256 taxablePercentage = currentWeight.complement() /** @rounds=up */;
        uint256 taxableAmount = amountInWithoutFee.mulUp(taxablePercentage /** @rounds=indeterminate */) /** @rounds=up */;
        uint256 nonTaxableAmount = amountInWithoutFee.sub(taxableAmount /** @rounds=indeterminate */) /** @rounds=down */;

        // No need to use checked arithmetic for the swap fee, it is guaranteed to be lower than 50%
        return nonTaxableAmount.add(taxableAmount.divUp(FixedPoint /** @rounds=indeterminate */.ONE /** @rounds=indeterminate */ - swapFeePercentage /** @rounds=indeterminate */ /** @rounds=indeterminate */) /** @rounds=up */) /** @rounds=exact */;
    }

    /*
    Flow of calculations:
    amountsTokenOut -> amountsOutProportional ->
    amountOutPercentageExcess -> amountOutBeforeFee -> newInvariant -> amountBPTIn
    */
    function _calcBptInGivenExactTokensOut(
        uint256 amp,
        uint256[] memory balances,
        uint256[] memory amountsOut,
        uint256 bptTotalSupply,
        uint256 currentInvariant,
        uint256 swapFeePercentage
    ) internal pure returns (uint256) {
        // BPT in, so we round up overall.

        // First loop calculates the sum of all token balances, which will be used to calculate
        // the current weights of each token relative to this sum
        uint256 sumBalances = 0 /** @rounds=exact */;
        for (uint256 i = 0 /** @rounds=exact */; i /** @rounds=indeterminate */ < balances /** @rounds=indeterminate */.length /** @rounds=indeterminate */; i++) {
            sumBalances = sumBalances.add(balances[i] /** @rounds=indeterminate */) /** @rounds=exact */;
        }

        // Calculate the weighted balance ratio without considering fees
        uint256[] memory balanceRatiosWithoutFee = new uint256[](amountsOut /** @rounds=indeterminate */.length /** @rounds=indeterminate */) /** @rounds=indeterminate */;
        uint256 invariantRatioWithoutFees = 0 /** @rounds=exact */;
        for (uint256 i = 0 /** @rounds=exact */; i /** @rounds=indeterminate */ < balances /** @rounds=indeterminate */.length /** @rounds=indeterminate */; i++) {
            uint256 currentWeight = balances[i].divUp(sumBalances /** @rounds=indeterminate */) /** @rounds=up */;
            balanceRatiosWithoutFee[i] = balances[i].sub(amountsOut[i]).divUp(balances[i] /** @rounds=indeterminate */) /** @rounds=up */;
            invariantRatioWithoutFees = invariantRatioWithoutFees.add(balanceRatiosWithoutFee[i].mulUp(currentWeight /** @rounds=indeterminate */) /** @rounds=up */) /** @rounds=exact */;
        }

        // Second loop calculates new amounts in, taking into account the fee on the percentage excess
        uint256[] memory newBalances = new uint256[](balances /** @rounds=indeterminate */.length /** @rounds=indeterminate */) /** @rounds=indeterminate */;
        for (uint256 i = 0 /** @rounds=exact */; i /** @rounds=indeterminate */ < balances /** @rounds=indeterminate */.length /** @rounds=indeterminate */; i++) {
            // Swap fees are typically charged on 'token in', but there is no 'token in' here, so we apply it to
            // 'token out'. This results in slightly larger price impact.

            uint256 amountOutWithFee;
            if (invariantRatioWithoutFees /** @rounds=indeterminate */ > balanceRatiosWithoutFee[i] /** @rounds=indeterminate */) {
                uint256 nonTaxableAmount = balances[i].mulDown(invariantRatioWithoutFees.complement() /** @rounds=up */) /** @rounds=down */;
                uint256 taxableAmount = amountsOut[i].sub(nonTaxableAmount /** @rounds=indeterminate */) /** @rounds=down */;
                // No need to use checked arithmetic for the swap fee, it is guaranteed to be lower than 50%
                amountOutWithFee = nonTaxableAmount.add(taxableAmount.divUp(FixedPoint /** @rounds=indeterminate */.ONE /** @rounds=indeterminate */ - swapFeePercentage /** @rounds=indeterminate */ /** @rounds=indeterminate */) /** @rounds=up */) /** @rounds=exact */;
            } else {
                amountOutWithFee = amountsOut[i] /** @rounds=indeterminate */;
            }

            newBalances[i] = balances[i].sub(amountOutWithFee /** @rounds=indeterminate */) /** @rounds=down */;
        }

        uint256 newInvariant = _calculateInvariant(amp /** @rounds=indeterminate */, newBalances /** @rounds=indeterminate */) /** @rounds=indeterminate */;
        uint256 invariantRatio = newInvariant.divDown(currentInvariant /** @rounds=indeterminate */) /** @rounds=down */;

        // return amountBPTIn
        return bptTotalSupply.mulUp(invariantRatio.complement() /** @rounds=up */) /** @rounds=up */;
    }

    function _calcTokenOutGivenExactBptIn(
        uint256 amp,
        uint256[] memory balances,
        uint256 tokenIndex,
        uint256 bptAmountIn,
        uint256 bptTotalSupply,
        uint256 currentInvariant,
        uint256 swapFeePercentage
    ) internal pure returns (uint256) {
        // Token out, so we round down overall.

        uint256 newInvariant = bptTotalSupply.sub(bptAmountIn).divUp(bptTotalSupply).mulUp(currentInvariant /** @rounds=indeterminate */) /** @rounds=up */;

        // Calculate amount out without fee
        uint256 newBalanceTokenIndex = _getTokenBalanceGivenInvariantAndAllOtherBalances(
            amp /** @rounds=indeterminate */,
            balances /** @rounds=indeterminate */,
            newInvariant /** @rounds=indeterminate */,
            tokenIndex /** @rounds=indeterminate */
        ) /** @rounds=indeterminate */;
        uint256 amountOutWithoutFee = balances[tokenIndex].sub(newBalanceTokenIndex /** @rounds=indeterminate */) /** @rounds=down */;

        // First calculate the sum of all token balances, which will be used to calculate
        // the current weight of each token
        uint256 sumBalances = 0 /** @rounds=exact */;
        for (uint256 i = 0 /** @rounds=exact */; i /** @rounds=indeterminate */ < balances /** @rounds=indeterminate */.length /** @rounds=indeterminate */; i++) {
            sumBalances = sumBalances.add(balances[i] /** @rounds=indeterminate */) /** @rounds=exact */;
        }

        // We can now compute how much excess balance is being withdrawn as a result of the virtual swaps, which result
        // in swap fees.
        uint256 currentWeight = balances[tokenIndex].divDown(sumBalances /** @rounds=indeterminate */) /** @rounds=down */;
        uint256 taxablePercentage = currentWeight.complement() /** @rounds=up */;

        // Swap fees are typically charged on 'token in', but there is no 'token in' here, so we apply it
        // to 'token out'. This results in slightly larger price impact. Fees are rounded up.
        uint256 taxableAmount = amountOutWithoutFee.mulUp(taxablePercentage /** @rounds=indeterminate */) /** @rounds=up */;
        uint256 nonTaxableAmount = amountOutWithoutFee.sub(taxableAmount /** @rounds=indeterminate */) /** @rounds=down */;

        // No need to use checked arithmetic for the swap fee, it is guaranteed to be lower than 50%
        return nonTaxableAmount.add(taxableAmount.mulDown(FixedPoint /** @rounds=indeterminate */.ONE /** @rounds=indeterminate */ - swapFeePercentage /** @rounds=indeterminate */ /** @rounds=indeterminate */) /** @rounds=down */) /** @rounds=exact */;
    }

    // This function calculates the balance of a given token (tokenIndex)
    // given all the other balances and the invariant
    function _getTokenBalanceGivenInvariantAndAllOtherBalances(
        uint256 amplificationParameter,
        uint256[] memory balances,
        uint256 invariant,
        uint256 tokenIndex
    ) internal pure returns (uint256) {
        // Rounds result up overall

        uint256 ampTimesTotal = amplificationParameter /** @rounds=indeterminate */ * balances /** @rounds=indeterminate */.length /** @rounds=indeterminate */ /** @rounds=indeterminate */;
        uint256 sum = balances[0] /** @rounds=indeterminate */;
        uint256 P_D = balances[0] /** @rounds=indeterminate */ * balances /** @rounds=indeterminate */.length /** @rounds=indeterminate */ /** @rounds=indeterminate */;
        for (uint256 j = 1 /** @rounds=exact */; j /** @rounds=indeterminate */ < balances /** @rounds=indeterminate */.length /** @rounds=indeterminate */; j++) {
            P_D = Math.divDown(Math.mul(Math.mul(P_D /** @rounds=indeterminate */, balances[j] /** @rounds=indeterminate */) /** @rounds=indeterminate */, balances /** @rounds=indeterminate */.length /** @rounds=indeterminate */) /** @rounds=indeterminate */, invariant /** @rounds=indeterminate */) /** @rounds=down */;
            sum = sum.add(balances[j] /** @rounds=indeterminate */) /** @rounds=exact */;
        }
        // No need to use safe math, based on the loop above `sum` is greater than or equal to `balances[tokenIndex]`
        sum = sum /** @rounds=indeterminate */ - balances[tokenIndex] /** @rounds=indeterminate */ /** @rounds=indeterminate */;

        uint256 inv2 = Math.mul(invariant /** @rounds=indeterminate */, invariant /** @rounds=indeterminate */) /** @rounds=indeterminate */;
        // We remove the balance from c by multiplying it
        uint256 c = Math.mul(
            Math.mul(Math.divUp(inv2 /** @rounds=indeterminate */, Math.mul(ampTimesTotal /** @rounds=indeterminate */, P_D /** @rounds=indeterminate */) /** @rounds=indeterminate */) /** @rounds=up */, _AMP_PRECISION /** @rounds=indeterminate */) /** @rounds=indeterminate */,
            balances[tokenIndex] /** @rounds=indeterminate */
        ) /** @rounds=indeterminate */;
        uint256 b = sum.add(Math.mul(Math.divDown(invariant /** @rounds=indeterminate */, ampTimesTotal /** @rounds=indeterminate */) /** @rounds=down */, _AMP_PRECISION /** @rounds=indeterminate */) /** @rounds=indeterminate */) /** @rounds=exact */;

        // We iterate to find the balance
        uint256 prevTokenBalance = 0 /** @rounds=exact */;
        // We multiply the first iteration outside the loop with the invariant to set the value of the
        // initial approximation.
        uint256 tokenBalance = Math.divUp(inv2.add(c /** @rounds=indeterminate */) /** @rounds=exact */, invariant.add(b /** @rounds=indeterminate */) /** @rounds=exact */) /** @rounds=up */;

        for (uint256 i = 0 /** @rounds=exact */; i /** @rounds=indeterminate */ < 255 /** @rounds=exact */; i++) {
            prevTokenBalance = tokenBalance /** @rounds=indeterminate */;

            tokenBalance = Math.divUp(
                Math.mul(tokenBalance, tokenBalance).add(c /** @rounds=indeterminate */) /** @rounds=exact */,
                Math.mul(tokenBalance, 2).add(b).sub(invariant /** @rounds=indeterminate */) /** @rounds=down */
            ) /** @rounds=up */;

            if (tokenBalance /** @rounds=indeterminate */ > prevTokenBalance /** @rounds=indeterminate */) {
                if (tokenBalance /** @rounds=indeterminate */ - prevTokenBalance /** @rounds=indeterminate */ /** @rounds=indeterminate */ <= 1 /** @rounds=exact */) {
                    return tokenBalance /** @rounds=indeterminate */;
                }
            } else if (prevTokenBalance /** @rounds=indeterminate */ - tokenBalance /** @rounds=indeterminate */ /** @rounds=indeterminate */ <= 1 /** @rounds=exact */) {
                return tokenBalance /** @rounds=indeterminate */;
            }
        }

        _revert(Errors /** @rounds=indeterminate */.STABLE_GET_BALANCE_DIDNT_CONVERGE /** @rounds=indeterminate */);
    }
}
