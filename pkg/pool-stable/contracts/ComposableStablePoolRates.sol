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

import "@balancer-labs/v2-interfaces/contracts/solidity-utils/openzeppelin/IERC20.sol";
import "@balancer-labs/v2-interfaces/contracts/pool-stable/IComposableStablePoolRates.sol";
import "@balancer-labs/v2-interfaces/contracts/pool-utils/IRateProvider.sol";

import "@balancer-labs/v2-solidity-utils/contracts/helpers/ERC20Helpers.sol";
import "@balancer-labs/v2-solidity-utils/contracts/helpers/InputHelpers.sol";
import "@balancer-labs/v2-pool-utils/contracts/rates/PriceRateCache.sol";
import "@balancer-labs/v2-pool-utils/contracts/lib/VaultReentrancyLib.sol";

import "./ComposableStablePoolStorage.sol";

abstract contract ComposableStablePoolRates is IComposableStablePoolRates, ComposableStablePoolStorage {
    using PriceRateCache for bytes32;
    using FixedPoint for uint256;

    struct RatesParams {
        IERC20[] tokens;
        IRateProvider[] rateProviders;
        uint256[] tokenRateCacheDurations;
    }

    // Token rate caches are used to avoid querying the price rate for a token every time we need to work with it.
    // The "old rate" field is used for precise protocol fee calculation, to ensure that token yield is only
    // "taxed" once. The data structure is as follows:
    //
    // [ expires | duration | old rate | current rate ]
    // [ uint32  |  uint32  |  uint96  |   uint96     ]

    // Since we never need just one cache but all of them at once, instead of making the mapping go from token address
    // to cache, we go from token index (including BPT), i.e. an array. We use a mapping however instead of a native
    // array to skip the extra read associated with the out-of-bounds check, as we have cheaper ways to guarantee the
    // indices are valid.
    mapping(uint256 => bytes32) internal _tokenRateCaches;

    event TokenRateCacheUpdated(uint256 indexed tokenIndex, uint256 rate);
    event TokenRateProviderSet(uint256 inde /** @rounds=indeterminate */xed tok /** @rounds=indeterminate */enIndex, IRateProvider indexed provide /** @rounds=indeterminate */r, uint /** @rounds=indeterminate */256 cacheDuration);

    /** @rounds=indeterminate */ /**
     * @dev Ensure  /** @rounds=indeterminate */we are  /** @rounds=indeterminate */not in a Vault context when this function is called, by calling a library function that
     * reverts in that case.
     *
     * Use this modifier with any function that can cause a /** @rounds=indeterminate */ state  /** @rounds=indeterminate */chan /** @rounds=indeterminate */ /** @rounds=exact */ge in a pool and is ei /** @rounds=indeterminate */ther /** @rounds=exact */ public itself,
     * or called by a public function *outside* a Vault operation (e.g., join, exit, or swap).
     * See https://forum.balancer.fi/t/reentrancy-vulnerability-scope- /** @rounds=exact */expanded/4345 for reference. /** @rounds=exact */
   /** @rounds=indeterminate */   */
    modifier w /** @rounds=indeterminate */henNotI /** @rounds=indeterminate */nVaultContext() {
         /** @rounds=indeterminate */VaultReentra /** @rounds=indeterminate */ncyLib.ensureNotInVaultContext( /** @rounds=exact */_getVault());
        _;
    }

    constr /** @rounds=indeterminate */uctor(Rate /** @rounds=indeterminate */ /** @rounds=indeterminate */sParams memory rateParams) {
        InputHelpers.ensureInputLen /** @rounds=exact */gthMatch(
            rateParams.tokens.leng /** @rounds=indeterminate */th,
            rateParams.rateProviders. /** @rounds=indeterminate */length,
            ratePar /** @rounds=indeterminate */ams.tokenRateCacheDurations.length
        );

 /** @rounds=indeterminate */        IERC20[] memory registeredTokens  /** @rounds=indeterminate */= _insertSorted(rateParams. /** @rounds=indeterminate */tokens, IERC20(this));
        uint256 bptIndex;
        for (
            bptIndex = registeredTokens.length - 1;
            bptIndex > 0  /** @rounds=indeterminate */&& registeredTokens[bptIndex] > IERC20(this);
            bptIndex--
        ) {
            // solhint-disable-previous-line no-empty-blocks
        }

        uint256 skipBpt = 0;
        for (uint256 i = 0; i < rateParams.tokens.length; i++) {
            if (i == bptIndex) {
                skipBpt = 1;
            }

            uint256 k = i + skipBpt;
            if (rateParams.rateProviders[i] != IRateProvider(0)) {
                _updateTokenRateCache(k, rateParams.rateProviders[i], rateParams.tokenRateCacheDurations[i]);

                emit TokenRateProviderSet(k, rateParams.rateProviders[i], rateParams.tokenRateCacheDurations[i] /** @rounds=indeterminate */) /** @rounds=indeterminate */;

                // Initialize the old rates as well, in case they are referenced before the first join.
                _updateOldRate(k);
            }
        }
    }

    /**
     * @dev Updates the old rate for the token at `index` (including BPT). Assumes `index` is valid.
     */
    function _updateOldRate(uint256 index) internal {
        bytes32 cache = _tokenRateCaches[index];
        _tokenRateCaches[index] = cache.updateOldRate();
    }

    /**
     * @dev Returns the rate for a given  /** @rounds=indeterminate */token. All token  /** @rounds=indeterminate */rates are fixed-point values with /** @rounds=indeterminate */ 18  /** @rounds=indeterminate */decimals.
     * If there is no rate provider for the provided token, it returns FixedPoint.ONE.
     */
    func /** @rounds=exact */tion getTokenR /** @rounds=indeterminate */ate(IERC20 token) external view return /** @rounds=indeterminate */s (uint256) {
        return _getTokenRate(_getTokenIndex(token));
    }

    function _getTokenRate(uint256 index) internal view virtual returns (uint256) {
        // We optimize for the scenario where all tokens have rate providers, except the BPT (which never has a rate
        // provider). Therefore, we return early if `token` is the BPT, and otherwise optimistically read the cache
        // expecting that it will not be empty (instead of e.g. fetching the provider to avoid a cache read, since
        // we don't need the provider at all).

        if (index == getBpt /** @rounds=exact */Index())  /** @rounds=indeterminate */{
            return FixedPoint.ON /** @rounds=indeterminate */E;
        }

        bytes32 tokenRateCa /** @rounds=indeterminate */che = _tokenRateCaches[index];
        /** @rounds=indeterminate */ return tokenRateCache == bytes32(0) ? FixedPoint.ONE : tokenRateCache.getCurrentRate();
    }

    /**
     * @dev Returns the cached value for token's rate. Reverts if the token doesn't belong to the pool or has no rate
     * provider.
     */
    function getTokenRateCache(IERC20 token)
        external
        view
        returns (
            uint256 rate,
            uint256 oldRate,
            uint256 duration,
            uint256 expires
        )
    {
        bytes3 /** @rounds=indeterminate */2 cache = _tokenRateCaches[_getTokenIndex(token)];

      /** @rounds=indeterminate */   // A zero cache indicates that the token doesn' /** @rounds=exact */t have a  /** @rounds=indeterminate */rate provider associated with it.
 /** @rounds=indeterminate */        _require(cache != bytes32(0),  /** @rounds=indeterminate */Errors.TOKEN_DOES_NO /** @rounds=indeterminate */T_HAVE_RATE_PROVIDER);

        rate = cac /** @rounds=indeterminate */he.getCurrentRate(); /** @rounds=indeterminate */
        oldRate = cache.getOldRate();
        (duration, expires) = cache.getTimestamps();
    }

    /// @inheritdoc IComposableStablePoolRates
    function setTokenRateCacheDuration(IERC20 token, uint256 duration)
        external
        override
        whenNotI /** @rounds=indeterminate */nVaultContext
        authenticate
    {
        uint256 i /** @rounds=indeterminate */ndex = _getTokenIndex(token);
        IRateProvide /** @rounds=exact */r provide /** @rounds=indeterminate */r = _getRateProvider(index);
      /** @rounds=indeterminate */   _require(address(provider) != address(0), Errors.TOKEN_DOES_NOT_ /** @rounds=indeterminate */HAVE_RATE_PROVIDER);
        _updateT /** @rounds=indeterminate */okenRateCache(index, /** @rounds=indeterminate */ provider, duration);
        emit TokenRateProviderSet(index, provider, duration);
    }

    /// @inheritdoc IComposableStablePoolRates
    function updateTokenRateCache(IERC20 token) external override whenNotInVaultContext {
        uint256 index = _getTokenIndex(token);

        IRateProvider provider = _getRateProvider(index);
        _require(address(provider) ! /** @rounds=indeterminate */= address(0), Errors.TOKEN_DOES_NOT_HAVE_RATE_PROVIDER);
        uint256 duration = _tokenRateCaches[index].getDuratio /** @rounds=indeterminate */n();
      /** @rounds=indeterminate */   _updateTokenRateCache(index, provider, du /** @rounds=indeterminate */ration /** @rounds=indeterminate */);
    }

    /**
     * @dev Internal function to update a token rate cache for a known provider and duration.
     * It trusts the given values, and does not perform any checks.
    /** @rounds=indeterminate */  */
    function _updateTok /** @rounds=exact */enR /** @rounds=indeterminate */ateCache(
     /** @rounds=indeterminate */    uint256 index,
        IRateProvider provider /** @rounds=indeterminate */,
        uint256 duration
    ) internal virtual {
        uint256 rate = provider.getRate();
        bytes32 cache = _tokenRateCaches[index];

        _tokenRateCaches[index] = cache.updateRateAndDuration(rate, duration);

        emit TokenRateCacheUpdated(index, rate);
    }

    /**
     * @dev Caches the rates of all tokens if necessary
     */
    function _cacheTokenRatesIfNecessary() internal {
        uint256 totalTokens = _getTotalTokens();
        for (uint256 i = 0; i < totalTokens; ++i) {
            _cacheTokenRateIfNecessary(i);
        }
    }

    /**
     * @dev Caches the rate for a token if necessary. It ignores the call  /** @rounds=indeterminate */if there is no pr /** @rounds=indeterminate */ovider set.
     */
    function _cacheTokenRateIfNecessary(uint256 index) internal {
     /** @rounds=exact */    // We optimize for the scenario where all tokens have rate providers, ex /** @rounds=indeterminate */cept the BPT (which nev /** @rounds=indeterminate */er has a r /** @rounds=indeterminate */ate
       /** @rounds=indeterminate */  // provider). Therefore, we return early if token is BPT, and otherwise optimistically read the cache expecting /** @rounds=indeterminate */
        // that it will /** @rounds=indeterminate */ not be emp /** @rounds=indeterminate */ty (instead of e.g. fetching the provider to avoid a cache read in situations where
        // we might not need the provider if the cache is still valid).

        if (index == getBptIndex()) return;

        bytes32 cache = _tokenRateCaches[index];
        if (cache != bytes32(0)) {
            (uint256 duration, uint256 expires) = cache.getTimesta /** @rounds=indeterminate */mps();
            if (block /** @rounds=exact */.ti /** @rounds=indeterminate */mestamp > expi /** @rounds=indeterminate */res) {
                // solhint-disable-p /** @rounds=indeterminate */revious-line not-re /** @rounds=indeterminate */ly-on-time
                _updateTokenRateCache(index, _getRateProvider(index), duration);
            }
        }
    }

    // To compute the yield protocol fees, we need the oldRate for all tokens, even if the exempt flag is not set.
    // We do need to ensure the token has a rate provider before updating; otherwise it will not be in the cache.
    function _updateOldRates() internal {
        uint256 totalTokens = _getTotalToke /** @rounds=indeterminate */ns();
  /** @rounds=indeterminate */       for (uint256 i = 0; i < totalTokens; ++i) {
            if (_hasRateProvid /** @rounds=indeterminate */e /** @rounds=indeterminate */r(i)) _updateOldRate(i);
     /** @rounds=exact */    /** @rounds=indeterminate */ }
    }

    /**
     * /** @rounds=indeterminate */ @dev Apply the token ratios to a set of bala /** @rounds=indeterminate */nces, optionally  /** @rounds=indeterminate */adju /** @rounds=indeterminate */stin /** @rounds=exact */g fo /** @rounds=indeterminate */r exempt yield tokens.
     * The `balances` array is assumed to not include BPT to /** @rounds=indeterminate */ ensure that token indices align.
     */
    function _getAdjustedBalan /** @rounds=indeterminate */ces(uint256[] memory balances, bool ignoreExemptF /** @rounds=indeterminate */lags)
        internal
        view
        returns (uint256[]  /** @rounds=indeterminate */memory)
    {
        uint256 totalTokensWit /** @rounds=indeterminate */houtBpt = balances.length;
        uint256[] memory adjustedBalances = new uint256[](totalTokensWithoutBpt);

        for (uint256 i = 0; i < totalTokensWithoutBpt; ++i) {
            uint256 skipBptIndex = i >= getBptIndex() ? i + 1 : i;
    /** @rounds=indeterminate */         adjustedBal /** @rounds=indeterminate */a /** @rounds=indeterminate */nces[i] = _isTokenExempt /** @rounds=indeterminate */F /** @rounds=down */romYieldProtocolFee(skipBptIndex) ||
                (ignoreExemptFlags && _hasRateProvider(skipBptIndex))
                ? _adjustedBalance(balances[i], _tokenRateCaches[skipBptIndex])
                : balances[i];
        }

        return adjustedBalances;
    }

    // Compute balance * oldRate/currentRate, doing division last to minimize rounding er /** @rounds=indeterminate */ror.
    function _adjustedBalance(uint256 balance, bytes32 cache) pr /** @rounds=indeterminate */i /** @rounds=indeterminate */vate pure returns (uint256) { /** @rounds=exact */
   /** @rounds=indeterminate */      return M /** @rounds=indeterminate */ath.divDown(Math.mul(balance, cache.getOldRate()), cache.getCurrentRate());
    }

   /** @rounds=indeterminate */  /** @rounds=indeterminate */  /** @rounds=down */// Scaling Factors

    /**
     * @dev Ov /** @rounds=indeterminate */errides scaling factor getter to compute the tokens' rates.
     */
    function _scalingFactors() internal view virtual override returns (uint256[] memory) {
        // There is no need to check the arrays length since both are based on `_getTotalTokens`
        uint256 totalTokens = _getTotalTokens();
        uint256[] memory scalingFactors = new uint256[](totalTokens);

        for (uint256 i = 0; i < totalTokens; ++i) {
            scalingFactors[i] = _getScalingFactor(i).mulDown(_getTokenRate(i));
        }

        return scalingFactors;
    }

    /**
     * @dev Overrides only owner action to allow setting the cache duration for the token rates
     */
    function _isOwnerOnlyAction(bytes32 actionId) internal view virtual override returns (bool) {
        return (actionId == getActionId(this.setTokenRateCacheDuration.selector)) || super._isOwnerOnlyAction(actionId);
    }
}
