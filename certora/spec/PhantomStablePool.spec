/*
    This is a specification file for smart contract verification with the Certora prover.
    For more information, visit: https://www.certora.com/
*/

import "../helpers/erc20.spec"

////////////////////////////////////////////////////////////////////////////
//                      Methods                                           //
////////////////////////////////////////////////////////////////////////////

methods {
	// stable math
    _calculateInvariant(uint256,uint256[]) returns (uint256) => NONDET
    //_calcOutGivenIn(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) => NONDET
    //_calcInGivenOut(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) => NONDET
    //_calcBptOutGivenExactTokensIn(uint256,uint256[],uint256[],uint256,uint256) returns (uint256) => NONDET
    //_calcTokenInGivenExactBptOut(uint256,uint256[],uint256,uint256,uint256,uint256)returns (uint256) => NONDET
    //_calcBptInGivenExactTokensOut(uint256,uint256[],uint256[],uint256,uint256) returns (uint256) => NONDET
    //_calcTokenOutGivenExactBptIn(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) => NONDET
	//_calcTokensOutGivenExactBptIn(uint256[],uint256,uint256) returns (uint256[]) => NONDET
    //_calcDueTokenProtocolSwapFeeAmount(uint256 ,uint256[],uint256,uint256,uint256) returns (uint256) => NONDET
    _getTokenBalanceGivenInvariantAndAllOtherBalances(uint256,uint256[],uint256,uint256)returns (uint256) => NONDET
    //_getRate(uint256[],uint256,uint256) returns (uint256) => NONDET

	// stable pool
	//_getAmplificationParameter() returns (uint256,bool) => NONDET

	// phantom pool
	//_trackDueProtocolFeeByInvariantIncrement(uint256,uint256,uint256[],uint256,uint256) => HAVOC_ECF
	//_trackDueProtocolFeeByBpt(uint256,uint256) => HAVOC_ECF
	//_onSwapTokenGivenBptIn(uint256,uint256,uint256,uint256[]) returns (uint256) => NONDET
    //_onSwapTokenGivenBptOut(uint256,uint256,uint256,uint256[]) returns (uint256) => NONDET
	//_skipBptIndex should be very easy...
	//getProtocolSwapFeePercentageCache easy
	//_cacheTokenRatesIfNecessary() => AUTO

    //_onSwapBptGivenTokenOut(uint256,uint256,uint256,uint256[]) returns (uint256) => NONDET
    //_onSwapBptGivenTokenIn(uint256,uint256,uint256,uint256[]) returns (uint256) => NONDET
	//_dropBptItem(uint256[]) returns (uint256,uint256[]) => NONDET
}


////////////////////////////////////////////////////////////////////////////
//                       Ghosts and definitions                           //
////////////////////////////////////////////////////////////////////////////

// TODO: add ghosts as necessary

////////////////////////////////////////////////////////////////////////////
//                       Invariants                                       //
////////////////////////////////////////////////////////////////////////////

// TODO: Add invariants; document them in reports/ExampleReport.md

////////////////////////////////////////////////////////////////////////////
//                       Rules                                            //
////////////////////////////////////////////////////////////////////////////

// onSwap((uint8,address,address,uint256,bytes32,uint256,address,address,bytes),uint256[],uint256,uint256)
// onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes)
rule sanity(method f) 
//filtered {f -> f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector}
//filtered {f -> f.selector == onSwap((uint8,address,address,uint256,bytes32,uint256,address,address,bytes),uint256[],uint256,uint256).selector}
{
	env e;
	calldataarg args;
	f(e,args);
	assert false;
}

////////////////////////////////////////////////////////////////////////////
//                       Helper Functions                                 //
////////////////////////////////////////////////////////////////////////////

// TODO: Any additional helper functions

