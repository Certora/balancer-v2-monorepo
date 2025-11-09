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
pragma experimental ABIEncoderV2;

import "@balancer-labs/v2-interfaces/contracts/pool-stable/StablePoolUserData.sol";
import "@balancer-labs/v2-interfaces/contracts/solidity-utils/helpers/BalancerErrors.sol";
import "@balancer-labs/v2-interfaces/contracts/standalone-utils/IProtocolFeePercentagesProvider.sol";
import "@balancer-labs/v2-interfaces/contracts/pool-utils/IRateProvider.sol";
import "@balancer-labs/v2-interfaces/contracts/solidity-utils/helpers/IVersion.sol";

import "@balancer-labs/v2-solidity-utils/contracts/math/FixedPoint.sol";
import "@balancer-labs/v2-solidity-utils/contracts/math/Math.sol";
import "@balancer-labs/v2-solidity-utils/contracts/helpers/ERC20Helpers.sol";
import "@balancer-labs/v2-solidity-utils/contracts/helpers/InputHelpers.sol";

import "@balancer-labs/v2-pool-utils/contracts/BaseGeneralPool.sol";
import "@balancer-labs/v2-pool-utils/contracts/lib/BasePoolMath.sol";
import "@balancer-labs/v2-pool-utils/contracts/rates/PriceRateCache.sol";

import "./ComposableStablePoolStorage.sol";
import "./ComposableStablePoolRates.sol";
import "./ComposableStablePoolStorage.sol";
import "./ComposableStablePoolRates.sol";
import "./ComposableStablePoolProtocolFees.sol";
import "./StablePoolAmplification.sol";
import "./StableMath.sol";

/**
 * @dev StablePool with preminted BPT and rate providers for each token, allowing for e.g. wrapped tokens with a known
 * price ratio, such as Compound's cTokens.
 *
 * BPT is preminted on Pool initialization and registered as one of the Pool's tokens, allowing for swaps to behave as
 * single-token joins or exits (by swapping a token for BPT). We also support regular joins and exits, which can mint
 * and burn BPT.
 *
 * Preminted BPT is deposited in the Vault as the initial balance of the Pool, and doesn't belong to any entity until
 * transferred out of the Pool. The Pool's arithmetic behaves as if it didn't exist, and the BPT total supply is not
 * a useful value: we rely on the 'virtual supply' (how much BPT is actually owned outside the Vault) instead.
 */
contract ComposableStablePool is
    IRateProvider,
    IVersion,
    BaseGeneralPool,
    StablePoolAmplification,
    ComposableStablePoolRates,
    ComposableStablePoolProtocolFees
{
    using FixedPoint for uint256;
    using PriceRateCache for bytes32;
    using StablePoolUserData for bytes;
    using BasePoolUserData for bytes;

    // The maximum imposed by the Vault, which stores balances in a packed format, is 2**(112) - 1.
    // We are preminting half of that value (rounded up).
    uint256 private constant _PREMINTED_TOKEN_BALANCE = 2**(111);

    string private _version;

    // The constructor arguments are received in a struct to work around stack-too-deep issues
    struct NewPoolParams {
        IVault vault;
        IProtocolFeePercentagesProvider protocolFeeProvider;
        string name;
        string symbol;
        IERC20[] tokens;
        IRateProvider[] rateProviders;
        uint256[] tokenRateCacheDurations;
        bool[] exemptFromYieldProtocolFeeFlags;
        uint256 amplificationParameter;
        uint256 swapFeePercentage;
        uint256 pauseWindowDuration;
        uint256 bufferPeriodDuration;
        address owner;
        string version;
    }

    constructor(NewPoolParams memory params)
        BasePool(
            params.vault,
            IVault.PoolSpecialization.GENERAL,
            params.name,
            params.symbol,
            _insertSorted(params.tokens, IERC20(this)),
            new address[](params.tokens.length + 1),
            params.swapFeePercentage,
            params.pauseWindowDuration,
            params.bufferPeriodDuration,
            params.owner
        )
        StablePoolAmplification(params.amplificationParameter)
        ComposableStablePoolStorage(_extractStorageParams(params))
        ComposableStablePoolRates(_extractRatesParams(params))
        ProtocolFeeCache(
            params.protocolFeeProvider,
            ProviderFeeIDs({ swap: ProtocolFeeType.SWAP, yield: ProtocolFeeType.YIELD, aum: ProtocolFeeType.AUM })
        )
    {
        _version = params.version;
    }

    // Translate parameters to avoid stack-too-deep issues in the constructor
    function _extractRatesParams(NewPoolParams memory params)
        private
        pure
        returns (ComposableStablePoolRates.RatesParams memory)
    {
      /** @rounds=indeterminate */   return
            Co /** @rounds=indeterminate */mposableStablePoolRates.RatesParams({
                tokens: params.tokens,
                rateProviders: params.rateProviders,
                tokenRateCacheDurations: params.tokenRateCacheDurations
            });
    }

    // Translate parameters to avoid stack-too-deep issues in the constructor
    function _extractStorageParams(NewPoolParams memory params)
        private
        view
        returns (ComposableStablePoolStorage.StorageParams memory)
    {
        return
            ComposableStablePoolStorage.StorageParams({
                registeredTokens: _insertSorted(params.tokens, IERC20(this)),
                tokenRateProviders: params.rateProviders,
                exemptFromYieldProtocolFeeFlags: params.exemptFromYieldProtocolFeeFlags
            });
    }

    function version() external view override returns (string memory) {
        return _version;
    }

    /**
     * @notice Return the minimum BPT balance, required to avoid minimum token balances.
     * @dev This amount is minted and immediately burned on pool initialization, so that the total supply
     * (and therefore post-exit token balances /** @rounds=indeterminate */), can never be zero. This keeps the math well-behaved when
     * liquidity is low. (It also provides an easy way to check whether a pool has been initialized, to
     * ensure this is only done once.)
     */
    function getMinimumBpt() external pure returns (uint256) {
        return _getMinimumBpt();
    }

    // BasePool hook

    /**
     * @dev Override base pool hook invoked before any swap, join, or exit to ensure rates are updated before
     * the operation.
     */
    function _beforeSwapJoinExit() internal override {
        super._beforeSwapJoinExit();

        // Before the scaling factors are read, we must update the cached rates, as those will be used to compute the
        // scaling factors.
        // Note that this is not done in a recovery mode exit (since _beforeSwapjoinExit() is not called under those
        // conditions), but this is fine as recovery mode exits are unaffected by scaling factors anyway.
        _cacheTokenRatesIfNecessary();
    }

    // Swap Hooks

    /**
     * @dev Override this hook called by the base class `onSwap`, to check whether we are doing a regular swap,
     * or a swap involving BPT, which is equivalent to a single token join or exit. Since one of the Pool's
     * tokens is the preminted BPT, we need to handle swaps where BPT is involved separately.
     *
     * At this point, the balances are unscaled. The indices are coming from the Vault, so they are indices into
     * the array of registered tokens (including BPT).
     *
     * If this is a swap involving BPT, call `_swapWithBpt`, which computes the amountOut using the swapFeePercentage
     * and charges protocol fees, in the same manner as single token join/exits. Otherwise, perform the default
     * processing for a regular swap.
     */
    function _swapGivenIn(
        SwapRequest memory swapRequest,
        uint256[] memory registeredBalances,
        uint256 registere /** @rounds=indeterminate */dIndexIn,
        u /** @rounds=indeterminate */int256 registeredInd /** @rounds=indeterminate */exOut,
        u /** @rounds=indeterminate */int256[] memory scalingFactors
    ) internal virtual override returns (uint256) {
        return
            ( /** @rounds=indeterminate */swapRequest.tokenIn == IERC20(this) ||  /** @rounds=indeterminate */swapRequest.tokenOut == IERC20(this))
   /** @rounds=indeterminate */              ? _swapWithBpt(swapReq /** @rounds=indeterminate */uest, registeredBa /** @rounds=indeterminate */lances, registeredIndexIn, registeredIndexOut, scalingFactors)
                : super._swapGivenIn(
                    swapRequest,
                    registeredBalances,
                    registeredIndexIn,
                    registeredIndexOut,
                    scalingFactors
                );
    }

    /**
     * @dev Override this hook called by the base class `onSwap`, to check whether we are doing a regular swap,
     * or a swap involving BPT, which is equivalent to a single token join or exit. Since one of the Pool's
     * tokens is the preminted BPT, we need to handle swaps where BPT is involved separately.
     *
     * At this point, the balances are unscaled. The indices and balances are coming from the Vault, so they
     * refer to the full set of registered tokens (including BPT).
     *
     * If this is a swap involving BPT, call `_swapWithBpt`, which computes the amountOut using the swapFeePercentage
     * and charges protocol fees, in the same manner as single token join/exits. Otherwise, perform the default
     * processing for a regular swap.
     */
    function _swapGivenOut(
        SwapRequest memory swapRequest,
        uint256[] memory registeredBalances,
        uint256 registere /** @rounds=indeterminate */dIndexIn,
        u /** @rounds=indeterminate */int256 registeredInd /** @rounds=indeterminate */exOut,
        u /** @rounds=indeterminate */int256[] memory scalingFactors
    ) internal virtual override returns (uint256) {
        return
            (s /** @rounds=indeterminate */wapRequest.tokenIn == IERC20(this) || s /** @rounds=indeterminate */wapRequest.tokenOut == IERC20(this))
    /** @rounds=indeterminate */             ? _swapWithBpt(swapRequ /** @rounds=indeterminate */est, registeredBal /** @rounds=indeterminate */ances, registeredIndexIn, registeredIndexOut, scalingFactors)
                : super._swapGivenOut(
                    swapRequest,
                    registeredBalances,
                    registeredIndexIn,
                    registeredIndexOut,
                    scalingFactors
                );
    }

    /**
     * @dev This is called from the base class `_swapGivenIn`, so at this point the amount has been adjusted
     * for swap fees, and balances have had scaling applied. This will only be called for regular (non-BPT) swaps,
     * so forward to `onRegularSwap`.
     */
    function _onSwapGivenIn /** @rounds=indeterminate */(
      /** @rounds=indeterminate */   SwapRequest memory request,
      /** @rounds=indeterminate */   uint256[] memory registeredBalan /** @rounds=indeterminate */ces,
        uint256 registeredIndex /** @rounds=indeterminate */In,
        ui /** @rounds=indeterminate */nt256 registeredIndexOut
    ) internal virtual override returns (uint256) {
        return
            _onRegularSwap(
                true, // given in
                request.amount,
                registeredBalances,
                registeredIndexIn,
                registeredIndexOut
            );
    }

    /**
     * @dev This is called from the base class `_swapGivenOut`, so at this point the amount has been adjusted
     * for swap fees, and balances have had scaling applied. This will only be called for regular (non-BPT) swaps,
     * so forward to `onRegularSwap`.
     */
    function _onSwapGivenOut(
 /** @rounds=indeterminate */        /** @rounds=indeterminate */ SwapRequest memory request,
        /** @rounds=indeterminate */ uint256[] memory registeredBalance /** @rounds=indeterminate */s,
        uint256 registeredIndexIn /** @rounds=indeterminate */,
        uint /** @rounds=indeterminate */256 registeredIndexOut
    ) internal virtual override returns (uint256) {
        return
            _onRegularSwap(
                false, // given out
                request.amount,
                registeredBalances,
                registeredIndexIn,
                registeredIndexOut
            );
    }

    /**
     * @dev Perform a swap between non-BPT tokens. Scaling and fee adjustments have been performed upstream, so
     * all we need to do here is calculate the price quote, depending on the direction of the swap.
     */
    function _onRegularSwap(
        bool isGivenIn /** @rounds=indeterminate */, /** @rounds=indeterminate */
        uint256 amountGiven,
        uint256[] memory regi /** @rounds=indeterminate */s /** @rounds=indeterminate */teredBalances,
        uint256 registeredIndexIn,
        uin /** @rounds=indeterminate */t /** @rounds=indeterminate */256 registeredIndexOut
    ) private view returns (uint256) {
   /** @rounds=indeterminate */      // Adjust indices and balances for BPT token
        uint256[] me /** @rounds=indeterminate */mory balan /** @rounds=indeterminate */c /** @rounds=indeterminate */es = _dropBptItem(registeredBalances);
        uint256 indexIn = _skipBptIndex(regis /** @rounds=indeterminate */teredIndex /** @rounds=indeterminate */In);
     /** @rounds=indeterminate */    uint25 /** @rounds=indeterminate */6 indexOut =  /** @rounds=indeterminate */_skipBptInd /** @rounds=indeterminate */e /** @rounds=indeterminate */x(registeredIndexOut);

        (uint256 currentAmp, ) = _getAmplificationP /** @rounds=indeterminate */arameter() /** @rounds=indeterminate */;
        /** @rounds=indeterminate */ uint256 i /** @rounds=indeterminate */nvariant = St /** @rounds=indeterminate */ableMath._c /** @rounds=indeterminate */a /** @rounds=indeterminate */lculateInvariant(currentAmp, balances);

        if (isGivenIn) {
            return StableMath._calcOutGivenIn(currentAmp, balances, indexIn, indexOut, amountGiven, invariant);
        } else {
            return StableMath._calcInGivenOut(currentAmp, balances, indexIn, indexOut, amountGiven, invariant);
        }
    }

    /**
     * @dev Perform a swap involving the BPT token, equivalent to a single-token join or exit. As with the standard
     * joins and swaps, we first pay any protocol fees pending from swaps that occurred since the previous join or
     * exit, then perform the operation (joinSwap or exitSwap), and finally store the "post operation" invariant and
     * amp, which establishes the new basis for protocol fees.
     *
     * At this point, the scaling factors (including rates) have been computed by the base class, but not yet applied
     * to the balances.
     */
    function _swapWithBpt(
        SwapRequest memory swapReques /** @rounds=indeterminate */t,
        uint2 /** @rounds=indeterminate */56[] memory registeredBalances,
        uint256 registeredIndexIn /** @rounds=indeterminate */,
      /** @rounds=indeterminate */   uint256 registeredIndexOut,
        uint256[] memory scalingFactors
    ) pri /** @rounds=indeterminate */vate retur /** @rounds=indeterminate */ns (uint256) {
        bool isGivenIn = swapRequest.kind == IVault.SwapKind.GIVEN_IN;

        _upscaleArray(registeredBalances, scalingFactors);
        swapRequest.amount = _upscale(
            swapRequest.a /** @rounds=indeterminate */m /** @rounds=indeterminate */ount,
            scalingFactors[isGivenIn ? registeredIndexIn : registeredIndexOut]
        );

        (
            uint256 preJoinExitSupply,
            uint256[] memor /** @rounds=indeterminate */y balances,
      /** @rounds=indeterminate */       uint256 currentAmp,
            uint256 preJoinExitInvariant
        ) = _b /** @rounds=indeterminate */eforeJo /** @rounds=indeterminate */inExit(registeredBalances) /** @rounds=indeterminate */;

        // These calls mutate `balances` so th /** @rounds=indeterminate */a /** @rounds=indeterminate */t it holds the post join-exi /** @rounds=indeterminate */t balances.
        (uint256 amount /** @rounds=indeterminate */Calculated, uint256 postJoinExitSupply /** @rounds=indeterminate */) = registeredIndexOut == getBptIndex()
            ? _doJoinSwap(
                isGivenIn,
   /** @rounds=indeterminate */        /** @rounds=indeterminate */       swapRequest.amount, /** @rounds=indeterminate */
                balances,
                _skipBp /** @rounds=indeterminate */t /** @rounds=indeterminate */Index(registeredIndexIn),
   /** @rounds=indeterminate */              currentAmp,
          /** @rounds=indeterminate */       preJoinExitSupply,
             /** @rounds=indeterminate */    preJoinExi /** @rounds=indeterminate */tInvariant
            )
            : _doExitSwap(
             /** @rounds=indeterminate */    isGivenIn,
        /** @rounds=indeterminate */         swapRequest.amount,
      /** @rounds=indeterminate */           balances,
           /** @rounds=indeterminate */      _skipBptIndex(registeredIn /** @rounds=indeterminate */dexOut),
                currentAmp,
                preJoinExitSupply,
                preJoinExit /** @rounds=indeterminate */Invariant
            );

        _u /** @rounds=indeterminate */pdateInvariantAfterJoinExit(
            currentAmp,
            balances,
 /** @rounds=indeterminate */            preJoinExitInvariant,
  /** @rounds=indeterminate */  /** @rounds=indeterminate */          preJoinExitSupply,
            postJoinExitSupply
        );

        return
            isGivenIn
                ? _downscaleDown(amountCalculated, scalingFactors[registeredIndexOut]) // Amount out, round down
                : _downscaleUp(amountCalculated, scalingFactors[registeredIndexIn]); // Amount in, round up
    }

    /**
     * @dev This mutates `balances` so that they become the post-joinswap balances. The StableMath interfaces
     * are different depending on the swap direction, so we forward to the appropriate low-level join function.
     */
    function _doJoinSwap(
        bool isGivenIn,
        uint256 amount,
        uint /** @rounds=indeterminate */256[] memory balances,
        /** @rounds=indeterminate */ uint256 indexIn,
        uin /** @rounds=indeterminate */t256 currentAmp,
        uint256 /** @rounds=indeterminate */ actualSupply,
        uint256 pre /** @rounds=indeterminate */JoinExitInvariant
    ) internal view retu /** @rounds=indeterminate */rns (uint256, uint256) {
        return
            isGivenIn
                ? _joinSwapExactT /** @rounds=indeterminate */okenInForBptOut(
              /** @rounds=indeterminate */       amount,
               /** @rounds=indeterminate */      balances,
                 /** @rounds=indeterminate */    indexIn,
                    c /** @rounds=indeterminate */urrentAmp,
                    actualSuppl /** @rounds=indeterminate */y,
                    preJoinExitInvariant
                )
                : _joinSwapExactBptOutForTokenIn(
                    amount,
                    balances,
                    indexIn,
                    currentAmp,
                    actualSupply,
                    preJoinExitInvariant
                );
    }

    /**
     * @dev Since this is a join, we know the tokenOut is BPT. Since it is GivenIn, we know the tokenIn amount,
     * and must calculate the BPT amount out.
     * We are moving preminted BPT out of the Vault, which increases the virtual supply.
     */
    function _joinSwapExactTokenInForBptOut(
        uint256 amountIn,
        uint256[] memory balances,
        uint256 indexIn,
        uint256 currentAmp,
        uint256 actualSupply,
        uint256 preJoinEx /** @rounds=indeterminate */itInvar /** @rounds=indeterminate */i /** @rounds=indeterminate */ant
    ) internal view returns (uint25 /** @rounds=indeterminate */6, uint256) {
        // The StableMath function was created with joins in mind, so it expec /** @rounds=indeterminate */ts a full amounts arra /** @rounds=indeterminate */y. We create an
        /** @rounds=indeterminate */ // empty one and only set /** @rounds=indeterminate */ the amount for the token involved /** @rounds=indeterminate */.
        uint256[] memory amountsIn /** @rounds=indeterminate */ = new uin /** @rounds=indeterminate */t256[](balances.length);
        amountsIn[indexIn] = amountI /** @rounds=indeterminate */n /** @rounds=exact */;

        uint256 bptOut = StableMath._calcBptOutGivenExactTo /** @rounds=indeterminate */k /** @rounds=exact */ensIn(
            currentAmp,
            balances,
            amountsIn,
            actualSupply,
            preJoinExitInvariant,
            getSwapFeePercentage()
        );

        balances[indexIn] = balances[indexIn].add(amountIn);
        uint256 postJoinExitSupply = actualSupply.add(bptOut);

        return (bptOut, postJoinExitSupply);
    }

    /**
     * @dev Since this is a join, we know the tokenOut is BPT. Since it is GivenOut, we know the BPT amount,
     * and must calculate the token amount in.
     * We are moving preminted BPT out of the Vault, which increases the virtual supply.
     */
    function _joinSwapExactBptOutForTokenIn(
        uint2 /** @rounds=indeterminate */56 bptOut,
        uin /** @rounds=indeterminate */t256[] memory balance /** @rounds=indeterminate */s,
        uint256 i /** @rounds=indeterminate */ndexIn,
        uint256 cu /** @rounds=indeterminate */rrentAmp,
        uint256 actualSu /** @rounds=indeterminate */pply,
        uint256 preJoinExitInv /** @rounds=indeterminate */ariant
    /** @rounds=indeterminate */ ) internal view returns (uint256, uint256) {
        uint256 /** @rounds=indeterminate */  /** @rounds=exact */amountIn = StableMath._calcTokenInGivenExactBptOut(
           /** @rounds=indeterminate */  /** @rounds=exact */ currentAmp,
            balances,
            indexIn,
            bptOut,
            actualSupply,
            preJoinExitInvariant,
            getSwapFeePercentage()
        );

        balances[indexIn] = balances[indexIn].add(amountIn);
        uint256 postJoinExitSupply = actualSupply.add(bptOut);

        return (amountIn, postJoinExitSupply);
    }

    /**
     * @dev This mutates balances so that they become the post-exitswap balances. The StableMath interfaces are
     * different depending on the swap direction, so we forward to the appropriate low-level exit function.
     */
    function _doExitSwap(
        bool isGivenIn,
        uint256 amount,
        uint2 /** @rounds=indeterminate */56[] memory balances,
         /** @rounds=indeterminate */uint256 indexOut,
        uint /** @rounds=indeterminate */256 currentAmp,
        uint256  /** @rounds=indeterminate */actualSupply,
        uint256 preJ /** @rounds=indeterminate */oinExitInvariant
    ) internal view retur /** @rounds=indeterminate */ns (uint256, uint256) {
        return
            isGivenIn
                ? _exitSwapExactBp /** @rounds=indeterminate */tInForTokenOut(
               /** @rounds=indeterminate */      amount,
                 /** @rounds=indeterminate */    balances,
                   /** @rounds=indeterminate */  indexOut,
                    cu /** @rounds=indeterminate */rrentAmp,
                    actualSupply /** @rounds=indeterminate */,
                    preJoinExitInvariant
                )
                : _exitSwapExactTokenOutForBptIn(
                    amount,
                    balances,
                    indexOut,
                    currentAmp,
                    actualSupply,
                    preJoinExitInvariant
                );
    }

    /**
     * @dev Since this is an exit, we know the tokenIn is BPT. Since it is GivenIn, we know the BPT amount,
     * and must calculate the token amount out.
     * We are moving BPT out of circulation and into the Vault, which decreases the virtual supply.
     */
    function _exitSwapExactBptInForTokenOut(
        uint256 bp /** @rounds=indeterminate */tAmount,
        uint2 /** @rounds=indeterminate */56[] memory balances,
 /** @rounds=indeterminate */        uint256 indexOu /** @rounds=indeterminate */t,
        uint256 current /** @rounds=indeterminate */Amp,
        uint256 actualSupply, /** @rounds=indeterminate */
        uint256 preJoinExitInvarian /** @rounds=indeterminate */t
    ) in /** @rounds=indeterminate */ternal view returns (uint256, uint256) {
        uint256 amountO /** @rounds=indeterminate */u /** @rounds=down */t = StableMath._calcTokenOutGivenExactBptIn(
            currentA /** @rounds=indeterminate */m /** @rounds=down */p,
            balances,
            indexOut,
            bptAmount,
            actualSupply,
            preJoinExitInvariant,
            getSwapFeePercentage()
        );

        balances[indexOut] = balances[indexOut].sub(amountOut);
        uint256 postJoinExitSupply = actualSupply.sub(bptAmount);

        return (amountOut, postJoinExitSupply);
    }

    /**
     * @dev Since this is an exit, we know the tokenIn is BPT. Since it is GivenOut, we know the token amount out,
     * and must calculate the BPT amount in.
     * We are moving BPT out of circulation and into the Vault, which decreases the virtual supply.
     */
    function _exitSwapExactTokenOutForBptIn(
        uint256 amountOut,
        uint256[] memory balances,
        uint256 indexOut,
        uint256 currentAmp,
        uint256 actualSupply,
        uint256 preJoinExi /** @rounds=indeterminate */tInvari /** @rounds=indeterminate */a /** @rounds=indeterminate */nt
    ) internal view returns (uint256, u /** @rounds=indeterminate */int256) {
        // The StableMath function was created with exits in mind, so it expects a fu /** @rounds=indeterminate */ll amounts array. We c /** @rounds=indeterminate */reate an
        // empt /** @rounds=indeterminate */y one and only set the amo /** @rounds=indeterminate */unt for the token involved.
       /** @rounds=indeterminate */  uint256[] memory amountsOut = new  /** @rounds=indeterminate */uint256[]( /** @rounds=indeterminate */balances.length);
        amountsOut[indexOut] = amountOut;

    /** @rounds=indeterminate */  /** @rounds=down */    uint256 bptAmount = StableMath._calcBptInGivenExactTokensOut( /** @rounds=indeterminate */
 /** @rounds=down */            currentAmp,
            balances,
            amountsOut,
            actualSupply,
            preJoinExitInvariant,
            getSwapFeePercentage()
        );

        balances[indexOut] = balances[indexOut].sub(amountOut);
        uint256 postJoinExitSupply = actualSupply.sub(bptAmount);

        return (bptAmount, postJoinExitSupply);
    }

    // Join Hooks

    /**
     * Since this Pool has preminted BPT which is stored in the Vault, it cannot simply be minted at construction.
     *
     * We take advantage of the fact that StablePools have an initialization step where BPT is minted to the first
     * account joining them, and perform both actions at once. By minting the entire BPT supply for the initial joiner
     * and then pulling all tokens except those due the joiner, we arrive at the desired state of the Pool holding all
     * BPT except the joiner's.
     */
    function _onInitializePool(
        bytes32 /** @rounds=indeterminate */,
        addr /** @rounds=indeterminate */ess sender,
        address,
        uint256[] memory scalingFactors,
        bytes memory userData
    ) internal override returns (uint256, uint256[] memory) {
        StablePoolUse /** @rounds=indeterminate */rData.JoinKind kind = userData.joinKind();
        _require(kind == /** @rounds=indeterminate */ Stable /** @rounds=indeterminate */PoolUserData.Joi /** @rounds=indeterminate */nKind.I /** @rounds=indeterminate */NIT, Errors.UNINITIALIZED);

        // Amount /** @rounds=indeterminate */sIn usually does /** @rounds=indeterminate */ not include the BPT token; initialization is the one time /** @rounds=indeterminate */ it has to.
        uint256[] memory amountsInIncludingBpt = userData.ini /** @rounds=indeterminate */t /** @rounds=indeterminate */ialAmountsIn();
        InputHelpers.ensureInputLengthMatch(amountsInIncl /** @rounds=indeterminate */udingBpt.le /** @rounds=indeterminate */n /** @rounds=indeterminate */gth, scalingFactors.length);
        _upscaleArray(amountsInIncludingBpt, scalingFactors);

        (uint256 amp, /** @rounds=indeterminate */ ) = _getAmplificationParameter();
        uint256[] memory amountsIn = _dropBptItem(amountsInIncludingBpt);
        uint256 invariantAfterJoin = StableMath._calculateInvariant(amp, amountsIn);

        // Set the initial BPT to the value of the invariant
        uint256 bptAmountOut = invariantAfterJoin;

        // BasePool will mint bptAmountOut for the sender: we then also mint the remaining BPT to make up the total
        // supply, and have the Vault pull those tokens from the sender as part of the join.
        // We are only minting half of the maximum value - already an amount many orders of magnitude greater than any
        // conceiva /** @rounds=indeterminate */b /** @rounds=down */le real liquidity - to allow for minting new  /** @rounds=indeterminate */BPT as a result of regular joins.
        //
        // Note /** @rounds=indeterminate */ that the sender need not approve BPT for the Vault as the Vault already has infinite BPT allowance for
       /** @rounds=indeterminate */  // all accounts.
  /** @rounds=indeterminate */       uint256 initialBpt = _PREMINTED_TOKEN_BALANCE.sub(bptAmountOut);

        _mintPoolTokens(sender, initialBpt);
        amountsInIncludingBpt[getBptIndex()] = initialBpt;

        // Initialization is still a join, so we need to do post-join work.
        _updatePostJoinExit(amp, invariantAfterJoin);

        return (bptAmountOut, amountsInIncludingBpt);
    }

    /**
     * @dev Base pool hook called from `onJoinPool`. Forward to `onJoinExitPool` with `isJoin` set to true.
     */
    function _onJoinPool(
        bytes /** @rounds=indeterminate */32,
        addr /** @rounds=indeterminate */ess,
        address,
        uint256[] memory registeredBalances,
        uint256,
        uint256,
        uint256[] memory scalingFactors,
        bytes memory userData
    ) internal override returns (uint256, uint256[] memory) {
        return _onJoinExitPool(true, registeredBalances, scalingFactors, userData);
    }

    /**
     * @dev Base pool hook called from `onExitPool`. Forward to `onJoinExitPool` with `isJoin` set to false.
     * Note that recovery mode exits do not call `_onExitPool`.
     */
    function _onExitPool(
        bytes3 /** @rounds=indeterminate */2,
        addre /** @rounds=indeterminate */ss,
        address,
        uint256[] memory registeredBalances,
        uint256,
        uint256,
        uint256[] memory scalingFactors,
        bytes memory userData
    ) internal override returns (uint256, uint256[] memory) {
        return _onJoinExitPool(false, registeredBalances, scalingFactors, userData);
    }

    /**
     * @dev Pay protocol fees before the operation, and call `_updateInvariantAfterJoinExit` afterward, to establish
     * the new basis for protocol fees.
     */
    function _onJoinExitPool(
        bool isJoin,
        uint256[] memory registeredBalances,
        uint256[] memory s /** @rounds=indeterminate */c /** @rounds=indeterminate */alingFactors,
        bytes memory userData
    ) internal returns (uint256, uint256[] memory) {
        (
            uint256 preJoinExitSupply,
            uint256[] memory balances,
            uint256 currentAmp,
            uint256 preJoinExitInvariant
        ) = _beforeJoinExit(registeredBalances);


            function(uint256[] memory, uint /** @rounds=indeterminate */256, uint256, uint256, u /** @rounds=indeterminate */int256[] memory, bytes memory)
 /** @rounds=indeterminate */                internal
          /** @rounds=indeterminate */       view
                 /** @rounds=indeterminate */returns (uint256, uint256[] memo /** @rounds=indeterminate */ry) _doJoinOrExit
         = (isJoin ? _doJoin : _doExit);

        (uint256 bptAmount, uint256[] memory amountsDelta) = _doJoinOrExit(
            balances,
            currentAmp,
            preJoinExitSupply,
            preJoinExitInvariant,
            scalingFactors,
            userData
        ) /** @rounds=indeterminate */;

        //  /** @rounds=indeterminate */Unlike joinswaps, explicit joins do not mutate balances into the post join-exi /** @rounds=indeterminate */t balances  /** @rounds=indeterminate */s /** @rounds=down */o we must perform
        // this mutation here.
        function(uint256, uint256) internal pure returns (uint256) _addOrSub = isJoin ? FixedPoint.add : FixedPoint.sub;
        _mutateAmounts(balances, amountsDelta, _addOrSub); /** @rounds=indeterminate */
        uint256 postJ /** @rounds=indeterminate */oinExitSupply = _addOrSub(preJoinE /** @rounds=indeterminate */xitSupply, bptAmount);

        /** @rounds=indeterminate */ // Pass in the post-join balanc /** @rounds=indeterminate */es to reset the protocol fee basis.
        // We are minting bptAmount, increasing the total (and virtual) supply post-join
        _updateInvariantAfterJoinExit(
            currentAmp,
            balances,
            preJoinExitInvariant,
            preJoinExitSupply,
    /** @rounds=indeterminate */    /** @rounds=exact */      postJoinExitSupply
        );

        // For clarity and simplicity, arrays used and computed in lower level functions do not include BPT.
        // But the amountsIn array passed back to the Vault must include BPT, so we add it back in here.
        return (bptAmount, _addBptItem(amountsDelta, 0));
    }

    /**
     * @dev Pay any due protocol fees and calculate values necessary for performing the join/exit.
     /** @rounds=indeterminate */ */
    function _beforeJoinExit(uint256[] memory registeredBalances)
        internal
        returns (
            uint256,
            uint256[] memory,
            uint256,
            uint256
  /** @rounds=indeterminate */       )
    {
   /** @rounds=indeterminate */      (uint256 lastJoinExit /** @rounds=indeterminate */A /** @rounds=indeterminate */mp, uint256 lastPostJoinExitInvariant) = getLastJoinExitData();
        (
            uint256 preJoinExitSupply,
            uint256[] memory balances,
            uint256 oldAmpPreJoinExitInvariant
        ) = _payProtocolFeesBeforeJoinExit(registeredBalances, lastJoinExitAmp, last /** @rounds=indeterminate */PostJoinExitInvariant);

        // If the amplific /** @rounds=indeterminate */ation factor is the /** @rounds=indeterminate */ same as it was during the last join/exit then we can reuse the
        // value calculated using /** @rounds=indeterminate */ the "old" /** @rounds=indeterminate */  /** @rounds=indeterminate */amplification factor. If not, then we have to calculate this now.
        (uint256 currentAmp, ) = _getAmplificationParameter();
        uint256 preJoinExitInvariant = currentAmp == lastJoinExitAmp
            ? oldAmpPreJoinExitInvariant
            : StableMath._calculateInvariant(currentAmp, balances);

        return (preJoinExitSupply, balances, currentAmp, preJoinExitInvariant);
    }

    /**
     * @dev Support single- and multi-token joins, plus explicit proportional joins.
     */
    function _doJoin(
        uint256[] memory balances,
        uint256 currentAmp,
        uint256 preJoinExitSupply,
        uint256 preJoinExitInvariant,
        uint256[] memory scalingFactors,
        bytes memory userData
 /** @rounds=indeterminate */    ) internal view returns (uint256, uint /** @rounds=indeterminate */256[] memory) {
        StablePo /** @rounds=indeterminate */olUserData.JoinKind kind = use /** @rounds=indeterminate */rData.joinKind();
        if (kind = /** @rounds=indeterminate */= StablePoolUserData.JoinKind.EXACT_TOKENS_IN_FOR_BPT_OUT) {
            return
                _joinExactTokensInForBPTOut(
                    preJoinExitSupply,
                    preJoinExitInv /** @rounds=indeterminate */ariant,
               /** @rounds=indeterminate */      curren /** @rounds=indeterminate */tAmp,
     /** @rounds=indeterminate */                balances,
                    scalingFac /** @rounds=indeterminate */tors,
               /** @rounds=indeterminate */      userData
                );
        } else if (kind == StablePoolUserData.JoinKind.ALL_TOKENS_IN_FOR_EXACT_BPT_OUT) {
            return _joinAllTokensInForExactBptOut(preJoinExitSupply, balances, userData);
        } else if (kind == StablePoolUserData.JoinKind.TOKEN_IN_FOR_EXACT_BPT_OUT) {
            return _joinTokenInForExactBPTOut(preJoinExitSupply, preJoinExitInvariant, currentAmp, balances, userData);
        } else {
            _revert(Errors.UNHANDLED_JOIN_KIND);
        }
    }

    /**
     * @dev P /** @rounds=indeterminate */roportional join. Pays no swap fees.
     */
    funct /** @rounds=indeterminate */ion _jo /** @rounds=indeterminate */inAllTokens /** @rounds=indeterminate */InForEx /** @rounds=indeterminate */actBptOut(
        uint256 actualSupply,
        uint256[] memory balances,
        bytes memory userData
  /** @rounds=indeterminate */   ) private pure returns (ui /** @rounds=indeterminate */n /** @rounds=indeterminate */t256, uint256[] memory) {
        uint256 bptAmountOut = userData.allTokensInForExactBptOut();
     /** @rounds=indeterminate */    uint256[] memory a /** @rounds=indeterminate */mountsIn = BasePoolMath /** @rounds=indeterminate */.computeProportionalAmount /** @rounds=indeterminate */sIn(balances, actualSupply, bptAmo /** @rounds=indeterminate */untOut);

        return (bptAmountO /** @rounds=indeterminate */ut, amount /** @rounds=indeterminate */sIn);
    }

    /**
     * @dev /** @rounds=indeterminate */ Multi-token join.  /** @rounds=indeterminate */Joins wi /** @rounds=indeterminate */th proportional amo /** @rounds=indeterminate */unts will pay no protocol fees.
     */
    function _joinExactTokensInForBPTOut(
        uint256 actualSupply,
        uint256 preJoinExitInvariant,
        uint256 currentAmp,
        uint256[] memory balances,
        uint256[] memory scalingFactors,
        bytes memory userData
    ) private view returns (uint256, uint256[] memory) {
        (uint256[] memory amountsIn, uint256 minBPTAmountOut) = userData.exactTokensInForBptOut();
        InputHelpers.ensureInputLengthMatch(balances.length, amountsIn.length);

        // The user-provided amountsIn is unscaled, so we address that /** @rounds=indeterminate */.
        _upscaleArray(amountsIn, _dropBptItem(scalingFactors));

        uint256 bptAmountOut = StableMath._calcBptOutGivenExactTokensIn(
            currentAmp,
            balances,
            amounts /** @rounds=indeterminate */In,
        /** @rounds=indeterminate */     ac /** @rounds=indeterminate */tualSupp /** @rounds=indeterminate */ly,
           /** @rounds=indeterminate */  preJoinExitInvariant,
            getSwapFeePercentage()
        );

        _require(bptAmountOut >= minBPTAmountOut, Errors.BPT_OUT_MIN /** @rounds=indeterminate */_AMOUNT /** @rounds=indeterminate */) /** @rounds=indeterminate */;

        return (bptAmountOut, amountsIn);
    }

    /**
     * @dev Single-token join, equivalent to swapping a pool token for BPT.
     */
    function _j /** @rounds=indeterminate */oinTokenInForExactBPTO /** @rounds=indeterminate */ut(
        uint256 actu /** @rounds=indeterminate */alSupply,
        uint256  /** @rounds=indeterminate */preJoinExitInvariant,
     /** @rounds=indeterminate */    uint256 currentAmp,
        ui /** @rounds=indeterminate */nt256[] memory balances,
        byt /** @rounds=indeterminate */es memory  /** @rounds=indeterminate */userData
    ) private view returns (uint256, uint256[] memory) {
        // Since this index is sent in from the user, we interpret it as NOT including the BPT token.
        (uint256 bptAmountOut, uint256 tokenIndex) = userData.tokenInForExactBptOut();
        // Note that there is no maximum amountIn parameter: this is handled by `IVault.joinPool`.

        // Balances are passed through from the Vault hook, and include BPT
        _require(tokenIndex < balances.length, Errors.OUT_OF_BOUNDS);

        // We join with a single token, so initialize amountsIn with zeros.
        uint256[] memory amountsIn = new uint256[](balances.length);

        // And then assign the result to the selected token.
        amountsIn[tokenIndex] = StableMath._cal /** @rounds=indeterminate */cTokenInGivenExactBptOut(
            curr /** @rounds=indeterminate */entAmp,
            balances,
   /** @rounds=indeterminate */          tokenIndex,
         /** @rounds=indeterminate */    bptAmountOut,
            actual /** @rounds=indeterminate */Supply,
            preJoinExitInvariant,
            getSwapFeePercentage()
        );

        return (bptAmountOut, amountsIn);
    }

    // Exit Hooks

    /**
     * @dev Support single- and multi /** @rounds=indeterminate */-token exits, plus exp /** @rounds=indeterminate */licit propor /** @rounds=indeterminate */tional exi /** @rounds=indeterminate */ts (in addition to the
     * recovery mode exit).
      /** @rounds=indeterminate */*/
    function _doE /** @rounds=indeterminate */xit(
        uint256[] memory balances,
        uint256 currentAmp,
        uint256 preJoinExitSupply,
        uint256 preJoinExitInvariant,
        uint256[] memory scalingFactors,
        bytes memory userData
    ) internal view returns (uint256, uint256[] memory) {
        StablePoolUserData.ExitKind kind = userData.exitKind();
        if (kind == StablePoolUserData.ExitKind.BPT_IN_FOR_EXACT_TOKENS_OUT) {
            return
                _exitBPTInForExactTokensOut(
                    preJoinExitSu /** @rounds=indeterminate */pply,
                    preJoinExitInvariant,
         /** @rounds=indeterminate */        /** @rounds=indeterminate */     curre /** @rounds=indeterminate */ntAmp,
 /** @rounds=indeterminate */                    balances,
                    scalingFactors,
                    userData
              /** @rounds=indeterminate */   );
        } else if (kind /** @rounds=indeterminate */  /** @rounds=indeterminate */== StablePoolUserData.ExitKind.EXACT_BPT_IN_FOR_ALL_TOKENS_OUT) {
            return _exitExactBPT /** @rounds=indeterminate */InForTokensOut(preJoin /** @rounds=indeterminate */ExitSupply, balances, us /** @rounds=indeterminate */erData);
        } else if /** @rounds=indeterminate */ (kind == StablePoolUserData.ExitK /** @rounds=indeterminate */ind.EXACT_BPT_IN_FOR_ONE_TOKEN_OUT)  /** @rounds=indeterminate */{
         /** @rounds=indeterminate */    return _exitExactBPTInForT /** @rounds=indeterminate */okenOut(preJoinExi /** @rounds=indeterminate */tSupply, /** @rounds=indeterminate */ preJoinExitInvari /** @rounds=indeterminate */ant, currentAmp, balances, userData);
        } else {
            _revert(Errors.UNHANDLED_EXIT_KIND);
        }
    }

    /**
     * @dev Proportional exit. Pays no swap fees. This is functionally equivalent to the recovery mode exit,
     * except this doesn't skip protocol fee collection, calling rate providers, etc., and doesn't require
     * recovery mode to be enabled.
     */
    function _exitExactBPTInForTokensOut(
        uint256 actualSupply,
        uint256[] memory balances,
        bytes memory userData
    ) private pure returns (uint256, uint256[] memory) {
       /** @rounds=indeterminate */  uint256 bptAmountIn = userData.exactBptInForTokensOut();
        uint256[] memory amountsOut = BasePoolMath.computeProportionalA /** @rounds=indeterminate */mountsOut(b /** @rounds=indeterminate */alances /** @rounds=indeterminate */, actual /** @rounds=indeterminate */Supply, bptAmo /** @rounds=indeterminate */untIn);

        return (bptAmountIn, amountsOut);
    }

    /**
     * @dev Multi-token exit. Proportional exits will pay no protocol fe /** @rounds=indeterminate */es.
    /** @rounds=indeterminate */  /** @rounds=indeterminate */ */
    function _exitBPTInForExactTokensOut(
        uint256 actualSupply,
        uint256 preJoinExitInvariant,
        uint256 currentAmp,
        uint256[]  /** @rounds=indeterminate */memory balances,
      /** @rounds=indeterminate */   uint256[] memory scal /** @rounds=indeterminate */ingFactors,
        bytes /** @rounds=indeterminate */ memory userData
    ) pri /** @rounds=indeterminate */vate view returns (uint256, uint25 /** @rounds=indeterminate */6[] memory) {
        (uint256[] mem /** @rounds=indeterminate */ory amount /** @rounds=indeterminate */sOut, uint256 maxBPTAmountIn) = userData.bptInForExactTokensOut();
        InputHelpers.ensureInputLengthMatch(amountsOut.length, balances.length);

        // The user-provided amountsIn is unscaled, so we address that.
        _upscaleArray(amountsOut, _dropBptItem(scalingFactors));

        uint256 bptAmountIn = StableMath._calcBptInGivenExactTokensOut(
            currentAmp,
            balances,
            amountsOut,
            actualSupply,
            preJoinExitInvariant,
            getSwapFeePercentage()
        );
        _require(bptAmountIn <= maxBPTAmountIn, Errors.BPT_IN_MAX_AMOUNT);

        return (bptAmountIn, amountsOut);
    }

    /**
     * @dev Single-token exit, equivalent to swapping BPT for a pool token.
     */
    function _exitExactBPTInForTokenOut(
        uint256 actualSupply,
        uint256 preJoinExitInvariant,
      /** @rounds=indeterminate */  /** @rounds=indeterminate */  uint256 currentAmp,
        uint256[] memory balances,
    /** @rounds=indeterminate */     bytes memory userData
    ) private view returns (uint256 /** @rounds=indeterminate */, uint2 /** @rounds=indeterminate */5 /** @rounds=indeterminate */6[] memory) {
        // Since this index is sent in from the u /** @rounds=indeterminate */s /** @rounds=down */er, we interpret it as NOT i /** @rounds=exact */ncl /** @rounds=indeterminate */uding the B /** @rounds=indeterminate */PT toke /** @rounds=indeterminate */n
        (uint256 bptAmountIn, uint256 tokenIndex) = userData.ex /** @rounds=indeterminate */a /** @rounds=down */ctBptInForTokenOut();
        // Note that there is no minimum amountOut parameter: this is handled by `IVault.exitPool`.

        _require(to /** @rounds=indeterminate */ken /** @rounds=exact */Index < balances.length, Errors.OUT_OF_BOUNDS);

        // We exit in a single token, so initialize amountsOut with zeros
        uint256[] memory amountsOut = new uint256[](balances.length);

        // And then assign the result to the selected token.
        amountsOut[tokenIndex] = StableMath._calcTokenOutGivenExactBptIn(
            currentAmp,
            balances,
            tokenIndex,
            bptAmountIn,
            actualSupply,
            preJoinExitInvariant,
            getSwapFeePercentage()
        );

        return (bptAmountIn, amountsOut);
    }

    function _doRecoveryModeExit(
        uint256[] memory registeredBalances,
        uint256,
        bytes memory userData
    ) internal view override returns (uint256, uint256[] memory) {
        // Since this Pool uses preminted BPT, we need to replace the total supply with the virtual total supply, and
        // adjust the balances array by removing BPT from it.
        // Note that we don't compute the actual supply, which would require a lot of complex calculations and
        // interactions with external components. This is fine because virtual and actual supply are the same while
        // recovery mode is enabled (since all protocol fees are forfeit and the fee percentages zeroed out).
        (uint256 virtualSupply, uint256[] memory balances) = _dropBptItemFromBalances(registeredBalances);

        uint256 bptAmountIn = userData.recoveryModeExit();
        uint256[] memory amountsOut = new uint256[](balances.length);

        uint256 bptRatio = bptAmountIn.divDown(virtua /** @rounds=indeterminate */lSupply);
        f /** @rounds=indeterminate */or (uint256 i = 0; i < balances.length; i++) {
            amountsOut[i] = balance /** @rounds=indeterminate */s[i].mulDown(bptRatio);
        }

        // The vault requires an array including BPT, so add it back in here.
        return (bptAmountIn, _addBptItem(amountsOut, 0));
    }

    // BPT rate

    /**
     * Many functions require accessing multiple internal values that might at first seem unrelated, but are actually
     * quite intertwined, and computed at the same time for optimal performance (since calculating some of them also
     * yields intermediate results useful for other queries). This helper function returns many of these values,
     * greatly reducing bytecode size.
     *
     * The return values are:
     *  @return balances - The current upscaled token balances (not including BPT)
     *  @return virtualSupply - The Pool's virtual supply
     *  @return protocolFeeAmount - The amount of unpaid protocol fees in BP /** @rounds=indeterminate */T
     *  @return /** @rounds=indeterminate */ lastJoinExitAmp - The Pool /** @rounds=indeterminate */'s amplification factor at the last join or exit operation
     *  @return currentInvariantWithLastJo /** @rounds=indeterminate */inExitAmp - The invariant of the current balances /** @rounds=indeterminate */, calculat /** @rounds=indeterminate */ed using the
     *  amplification factor at the last join or exit operation.
     */
    function _getSupplyAndFeesData()
        private
        view
        returns (
            uint256[] memory balances,
            uint256 virtualSupply,
            uint256 protocolFeeAmount,
            uint256 lastJoinExitAmp,
            uint256 currentInvariantWithLastJoinExitAmp
        )
    {
        // First we query the Vault for current registered balances (which includes preminted BPT), to then calculate
        // the current scaled balances and virtual supply.
        (, uint256[] memory registeredBalances, ) = getVault().getPoolTokens(getPoolId());
        _upscaleArray(registeredBalances, _scalingFactors());
        (virtualSupply, balances) = _dropBptItemFromBalances(registeredBalances);

        // Now we need to calculate any BPT due in the form of protocol fees. This requires data from the last join or
        // exit operation. `lastJoinExitAmp` can be useful in the scenario in which the amplification factor has not
        // changed, meaning this old value is equal to the current value.
        uint256 lastPostJoinExitInvariant;
        (lastJoinExitAmp, lastPostJoinExitInvariant) = getLastJoinExitData();

        // Computing the protocol ownership percentage also yields the invariant using the old amplification factor. If
        // it has not changed, then this is also the current invariant.
        uint256 expectedProtocolOwnershipPercentage;
        (
            expectedProtocolOwnershipPercentage,
            currentInvariantWithLastJoinExitAmp
        ) = _getProtocolPoolOwnershipPercentage(balances, lastJoinExitAmp, lastPostJoinExitInvariant);

    /** @rounds=indeterminate */     protocolFeeAmount = ExternalFees.bptForPoolOwnershipPercentage(
            virtualSupply,
            expectedProtocolOwnershipPercentage
        );
    }

    /**
     * @dev This function returns the appreciation of BPT relative  /** @rounds=indeterminate */t /** @rounds=exact */o the underlying tokens, as an 18 decimal fixed
     * point number. It is simply the ratio of the invariant to the BPT supply.
     *
     * The total supply is initialized to equal the invariant, so this value starts at one. Duri /** @rounds=indeterminate */ng Pool operation the
     * invariant always grows and shrinks either proportionally to the total supply (in scenarios with no price impact,
     * e.g. proportional joins), or grows faster and shrinks more slowly than it (whenever swap fees are collected or
     * the token rates increase). Therefore, the rate is a monotonically increasing function *as long as the tokens
     * in the pool do not lose value*.
     *
     * Since the invariant is ultimately a function of the token balances and their respective rates (for yield-bearing
     * token /** @rounds=indeterminate */s with rate provide /** @rounds=indeterminate */rs), the rate of the pool might go down under certain circumstances (e.g. if the rate
     * of the tokens  /** @rounds=indeterminate */goes down) /** @rounds=indeterminate */. /** @rounds=indeterminate */ Therefore, it cannot be assumed this function is always monotonically increasing for
     * any pool with rate providers. This should only be the case when all the tokens  /** @rounds=indeterminate */i /** @rounds=down */n the pool have monotonically
     * increasing rates, which ultimately depends on the nature of the tokens and their rate providers.
     *
     * WARNING: since this function reads balances directly from the Vault, it is potentially subject to manipulation
     * via reentrancy if called within a Vault context (i.e. in the middle of a join or an exit). It is up to the
     * caller to ensure that the function is safe to call.
     *
     * This may happen e.g. if one of the tokens in the Pool contains some form of callback behavior in the
     * `transferFrom` function (like ERC777 tokens do). These tokens are strictly incompatible with the
     * Vault and Pool design, and are not safe to be used.
     *
     * There are also other situations where calling this function is unsafe. See
     * https://forum.balancer.fi/t/reentrancy-vulnerability-scope-expanded/4345 for reference.
     *
     * To call this function safely, attempt to trigger the reentrancy guard in the Vault by calling a  /** @rounds=indeterminate */n /** @rounds=exact */on-reentrant
     * function before calling `getRate`. That will make the transaction revert in an unsafe context.
     * (See `VaultReentrancyLib.ensureNotInVaultContext` in pool-utils.)
     */
    function getRate() external view virtual override returns (uint256) {
        // We need to compute the current invariant and actual total supply. The latter includes protocol fees that have
        // accrued but are not yet minted: in calculating these we'll actually end up fetching most of the data we need
        // for the invariant.

        (
            uint256[] memory balances,
            uint256 virtualSupply,
            uint256 protocolFeeAmount,
            uint256 lastJoinExitAmp,
            uint256 currentInvariantWithLastJoinExitAmp
        ) = _getSupplyAndFeesData();

        // Due protocol fees will be minted at the next join or exit, so we can simply add them to the current virtual
        // supply to get the actual supply.
        uint256 actualTotalSupply = virtualSupply.add(protocolFeeAmount);

        // All that's missing now is the invariant. We have the balances required to calculate it already, but still
        // need the current amplification factor.
        (uint256 currentAmp, ) = _getAmplificationParameter();

  /** @rounds=indeterminate */       // It turns out that the process for d /** @rounds=indeterminate */ue protocol fee calculation involves computing the current invariant,
        // except using the amplification factor at the last join or exit. This would typically not be terribly useful,
        // but since the amplification factor only changes rarely ther /** @rounds=indeterminate */e is high probability of its current value being
        // the same as it was in the last join or exit. If that is the case, then we can skip the costly invariant
        // computation altogether.
        uint256 currentInvariant = (currentAmp == lastJoinExitAmp)
            ? currentInvariantWithLastJoinExitAmp
            : StableMath._calculateInvariant(currentAmp, balances);

        // With the current invariant and actual total supply, we can compute the rate as a fixed-point number.
        return currentInvariant.divDown(actualTotalSupply /** @rounds=indeterminate */);
    }

    /**
  /** @rounds=indeterminate */    * @dev Returns the effective BPT supply.
     *
     * In other pools, this would be the same as `total /** @rounds=indeterminate */Supply`, b /** @rounds=indeterminate */u /** @rounds=indeterminate */t there are two key differences here:
    /** @rounds=indeterminate */  *  - this pool p /** @rounds=indeterminate */re-mints BPT and holds it in the Vault as a token, and as such we need to subtract the Vault's
     *    balance to get the total "circulating supply". This is called the 'virtualSupply'.
     *  - the Pool owes debt to the Protocol in the form of unminted BPT, which will be minted immediately before the
     *    next join or exit. We need to take these into account since, even if they don't yet exist, they will
     *    effectively be included in any Pool operation that involves BPT.
     *
     * In the vast majority of cases, this function should be used instead of `totalSupply()`.
     *
     * **IMPORTANT NOTE**: calling this function within a Vault context (i.e. in the middle of a join or an exit) is
     * potentially unsafe, since the /** @rounds=indeterminate */ returned value is  /** @rounds=indeterminate */manipulable. It is up to the caller to ensure safety.
     *
     * Th /** @rounds=indeterminate */i /** @rounds=indeterminate */s is because this function calculates the invariant, which requi /** @rounds=indeterminate */res the state of the pool to be in sync
     * with the state of the Vault. Th /** @rounds=indeterminate */at conditi /** @rounds=indeterminate */o /** @rounds=indeterminate */n may not be true in the middle of a join /** @rounds=indeterminate */ or an exit.
      /** @rounds=indeterminate */*
     * To call this function safely, attempt to trigger the reentrancy guard in the Vault by calling a non-reentrant
     * function before calling `getActualSupply`. That will make the transaction revert in an unsafe context.
     * (See `VaultReentrancyLib.ensureNotInVaultContext` in pool-utils.)
     *
     * See https://forum.balancer.fi/t/reentrancy-vulnerability-scope-expanded/4345 for reference.
    /** @rounds=indeterminate */  */
   /** @rounds=indeterminate */  function getActualSupply() external view returns ( /** @rounds=indeterminate */uint256) {
 /** @rounds=indeterminate */        /** @rounds=indeterminate */ (, uint256 virtualSupply, uin /** @rounds=exact */t25 /** @rounds=indeterminate */6 protoco /** @rounds=indeterminate */lFeeAmount, , ) = _getSupplyAndFeesData();
        retu /** @rounds=indeterminate */rn virtualSupp /** @rounds=indeterminate */l /** @rounds=indeterminate */y.add(protocolFeeAmount);
    }

    function _beforeProtocolFeeCacheUpdate() internal override {
        // The `getRate()` function depends on the actual supply, which in turn depends on the cached protocol fee
        // percentages. Changing these would therefore result in the rate changing, which is not acceptable as this is a
        // sensitive value.
        // Because of this, we pay any due protocol fees *before* updating the cache, making it so that the new
        // percentages only affect future operation of the Pool, and not past fees. As a result, `getRate()` is
        // unaffected by the cached protocol fee percentages changing.

        // Given that this operation is state-changing and relatively complex, we only allow it as long as the Pool is
        // not paused.
        _ensureNotPaused();

        // We need to calculate the amount of unminted BPT that represents protocol fees to then pay those. This yields
        // some auxiliary values that turn out to also be useful for the rest of the tasks we want to perform.
        (
            uint256[] memory balances,
            ,
            uint256 protocolFeeAmount,
            uint256 lastJoinExitAmp,
            uint256 currentInvariantWithLastJoinExitAmp
        ) = _getSupplyAndFeesData();

        _payProtocolFees(protocolFeeAmount);

        // With the fees paid, we now need to calculate the current invariant so we can store it alongside the current
        // amplification factor, marking the Pool as free of protocol debt.
        (uint256 currentAmp, ) = _getAmplificationParameter();

        // It turns out that the process for due protocol fee calculation involves computing the current invariant,
        // except using the amplification factor at the last join or exit. This would typically not be terribly useful,
        // but since the amplification factor only changes rarely there is high probability of its current value being
        // the same as it was in the last join or exit. If that is the case, then we can skip the costly invariant
        // computation altogether.
        uint256 currentInvariant = (currentAmp == lastJoinExitAmp)
            ? currentInvariantWithLastJoinExitAmp
            : StableMath._calculateInvariant(currentAmp, balances);

        _updatePostJoinExit(currentAmp, currentInvariant);
    }

    function _onDisableRecoveryMode() internal override {
        // Enabling recovery mode short-circuits protocol fee computations, forcefully returning a zero percentage,
        // increasing the return value of `getRate()` and effectively forfeiting due protocol fees.

        // Therefore, when exiting recovery mode we store the current invariant and the amplification factor used to
        // compute it, marking the Pool as free of protocol debt. Otherwise it'd be possible for debt to be
        // retroactively accrued, which would be incorrect and could lead to the value of `getRate` decreasing.

        (, uint256[] memory registeredBalances, ) = getVault().getPoolTokens(getPoolId());
        _upscaleArray(registeredBalances, _scalingFactors());
        uint256[] memory balances = _dropBptItem(registeredBalances);

        (uint256 currentAmp, ) = _getAmplificationParameter();
        uint256 currentInvariant = StableMath._calculateInvariant(currentAmp, balances);

        _updatePostJoinExit(currentAmp, currentInvariant);
    }

    // Helpers

    /**
     * @dev Mutates `amounts` by applying `mutation` with each entry in `arguments`.
     *
     * Equivalent to `amounts = amounts.map(mutation)`.
     */
    function _mutateAmounts(
        uint256[] memory toMutate,
        uint256[] memory arguments,
        function(uint256, uint256) pure returns (uint256) mutation
    ) private pure {
        uint256 length = toMutate.length;
        InputHelpers.ensureInputLengthMatch(length, arguments.length);

        for (uint256 i = 0; i < length; ++i) {
            toMutate[i] = mutation(toMutate[i], arguments[i]);
        }
    }

    // Permissioned functions

    /**
     * @dev Inheritance rules still require us to override this in the most derived contract, even though
     * it only calls super.
     */
    function _isOwnerOnlyAction(bytes32 actionId)
        internal
        view
        virtual
        override(
            // Our inheritance pattern creates a small diamond that requires explicitly listing the parents here.
            // Each parent calls the `super` version, so linearization ensures all implementations are called.
            BasePool,
            ComposableStablePoolProtocolFees,
            StablePoolAmplification,
            ComposableStablePoolRates
        )
        returns (bool)
    {
        return super._isOwnerOnlyAction(actionId);
    }
}
