/*
    This is a specification file for smart contract verification with the Certora prover.
    For more information, visit: https://www.certora.com/
*/

import "../helpers/erc20.spec"

// nondet all,				onSwap			|  onJoinPool

// nondet 		1st, 		onSwap 	timeout |  onJoinPool
// nondet 		2nd, 		onSwap		 	|  onJoinPool 	timeout
// nondet 		3rd, 		onSwap		 	|  onJoinPool 	timeout
// nondet 		4th, 		onSwap 	timeout |  onJoinPool 	timeout
// nondet 		5th, 		onSwap 	timeout |  onJoinPool 	timeout
// nondet 		6th, 		onSwap 	timeout |  onJoinPool 	timeout
// nondet 		7th, 		onSwap 	timeout |  onJoinPool 	timeout
// nondet 		8th, 		onSwap 	timeout |  onJoinPool 	timeout
// nondet 		9th, 		onSwap 	timeout |  onJoinPool 	timeout
// nondet 		10th,	 	onSwap 			|  onJoinPool 	timeout
// nondet 		11th,	 	onSwap 	timeout |  onJoinPool 	timeout

// nondet 1st and 10th, 	onSwap 			|  onJoinPool 	

/// Functions that matter
// _calculateInvariant matters for onJoinPool
// _calcOutGivenIn matters for onSwap
// _calcInGivenOut matters for onSwap
// _getTokenBalanceGivenInvariantAndAllOtherBalances matters for onSwap

// want properties of math functions which we can require

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

    // authorizor functions
    _getAuthorizor() => DISPATCHER(true)
    _canPreform(bytes32, address) returns (bool) => DISPATCHER(true)
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

