import "../helpers/erc20.spec"

////////////////////////////////////////////////////////////////////////////
//                      Methods                                           //
////////////////////////////////////////////////////////////////////////////

methods {
	_callPoolBalanceChange(uint8,bytes32,address,address,(address[],uint256[],bytes,bool),bytes32[]) returns (bytes32[], uint256[], uint256[]) => CONSTANT
	//_processJoinPoolTransfers(address, (address[],uint256[],bytes,bool), bytes32[], uint256[], uint256[]) returns (bytes32[]) => CONSTANT not summarizable yet
	//_processExitPoolTransfers(address, (address[],uint256[],bytes,bool), bytes32[], uint256[], uint256[]) returns (bytes32[]) => CONSTANT not summarizable yet (might work if we munge priv to internal)

	// all functions called by joinPool
    //_joinOrExit(kind, poolId, sender, recipient, change);
    //   _callPoolBalanceChange
    //        _processJoinPoolTransfers
    //                or
    //        _processExitPoolTransfers

    //   _getPoolSpecialization
    //           or
    //   _setMinimalSwapInfoPoolBalances
    //           or
    //   _setGeneralPoolBalances
}

// // Summarizable methods for swap 
// _authenticateFor(address)
// _translateToIERC20(address)
// _isETH(address)
// _WETH()
// _translateToIERC20(address)
// _isETH(address)
// _asIERC20(address)
// _swapWithPool(struct IPoolSwapStructs.SwapRequest)
// _getPoolAddress(bytes32)
// _getPoolSpecialization(bytes32)
// _processTwoTokenPoolSwapRequest(struct IPoolSwapStructs.SwapRequest,address)
// _getTwoTokenPoolSharedBalances(bytes32,address,address)
// _sortTwoTokens(address,address)
// _getTwoTokenPairHash(address,address)
// _twoTokenPoolTokens[*].balances[*].sharedCash
// _twoTokenPoolTokens[*].balances[*].sharedManaged
// fromSharedToBalanceA(bytes32,bytes32)
// _decodeBalanceA(bytes32)
// _decodeBalanceA(bytes32)
// toBalance(uint256,uint256,uint256)
// _pack(uint256,uint256,uint256)
// fromSharedToBalanceB(bytes32,bytes32)
// _decodeBalanceB(bytes32)
// _decodeBalanceB(bytes32)
// toBalance(uint256,uint256,uint256)
// _pack(uint256,uint256,uint256)
// _callMinimalSwapInfoPoolOnSwapHook(struct IPoolSwapStructs.SwapRequest,address,bytes32,bytes32)
// _getAmounts(uint8,uint256,uint256)
// toBalance(uint256,uint256,uint256)
// _pack(uint256,uint256,uint256)
// toBalance(uint256,uint256,uint256)
// _pack(uint256,uint256,uint256)
// toSharedCash(bytes32,bytes32)
// _pack(uint256,uint256,uint256)
// _getAmounts(uint8,uint256,uint256)
// _receiveAsset(address,uint256,address,bool)
// _isETH(address)
// _WETH()
// _sendAsset(address,uint256,address,bool)
// _isETH(address)
// _handleRemainingEth(uint256)

// // Summarizable methods for joinPool
// _joinOrExit(uint8,bytes32,address,address,struct PoolBalances.PoolBalanceChange)
// _ensureRegisteredPool(bytes32)
// _isPoolRegistered[*]
// _authenticateFor(address)
// _translateToIERC20(address[])
// _translateToIERC20(address)
// _isETH(address)
// _WETH()
// _validateTokensAndGetBalances(bytes32,address[])
// _getPoolTokens(bytes32)
// _getPoolSpecialization(bytes32)
// _getGeneralPoolTokens(bytes32)
// _generalPoolsBalances[*]._length
// _generalPoolsBalances[*]._entries[*]._key
// _generalPoolsBalances[*]._entries[*]._value
// _callPoolBalanceChange(uint8,bytes32,address,address,struct PoolBalances.PoolBalanceChange,bytes32[])
// totalsAndLastChangeBlock(bytes32[])
// _getPoolAddress(bytes32)
// _getProtocolSwapFeePercentage()
// getProtocolFeesCollector()
// _getPoolSpecialization(bytes32)
// _setGeneralPoolBalances(bytes32,bytes32[])
// _unsafeCastToInt256(uint256[],bool)

// // Summarizable methods for exitPool
// _joinOrExit(uint8,bytes32,address,address,struct PoolBalances.PoolBalanceChange)
// _ensureRegisteredPool(bytes32)
// _isPoolRegistered[*]
// _authenticateFor(address)
// _translateToIERC20(address[])
// _translateToIERC20(address)
// _isETH(address)
// _WETH()
// _validateTokensAndGetBalances(bytes32,address[])
// _getPoolTokens(bytes32)
// _getPoolSpecialization(bytes32)
// _getGeneralPoolTokens(bytes32)
// _generalPoolsBalances[*]._length
// _generalPoolsBalances[*]._entries[*]._key
// _generalPoolsBalances[*]._entries[*]._value
// _callPoolBalanceChange(uint8,bytes32,address,address,struct PoolBalances.PoolBalanceChange,bytes32[])
// totalsAndLastChangeBlock(bytes32[])
// _getPoolAddress(bytes32)
// _getProtocolSwapFeePercentage()
// getProtocolFeesCollector()
// _getPoolSpecialization(bytes32)
// _setGeneralPoolBalances(bytes32,bytes32[])
// _unsafeCastToInt256(uint256[],bool)


////////////////////////////////////////////////////////////////////////////
//                    Ghosts, hooks and definitions                       //
////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////
//                            Invariants                                  //
////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////
//                               Rule                                     //
////////////////////////////////////////////////////////////////////////////

rule sanity(method f) 
filtered {
	f -> f.selector == exitPool(bytes32,address,address,(address[],uint256[],bytes,bool)).selector ||
	//f -> f.selector == Harness_doubleExitPool(bytes32, address, address, address, address, uint256, uint256, bool).selector ||
	//f.selector == Harness_doubleJoinPool(bytes32, address, address, address, address, uint256, uint256, bool).selector ||
	f.selector == joinPool(bytes32,address,address,(address[],uint256[],bytes,bool)).selector ||
	f.selector == swap((bytes32,uint8,address,address,uint256,bytes),(address,bool,address,bool),uint256,uint256).selector
}
{
	env e;
	calldataarg args;
	f(e,args);
	assert false;
}




////////////////////////////////////////////////////////////////////////////
//                            Helper Functions                            //
////////////////////////////////////////////////////////////////////////////

// TODO: Any additional helper functions

