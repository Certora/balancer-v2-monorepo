import "../helpers/erc20.spec"

//using VaultHarness as _vault

methods {
	// stable math
    _calculateInvariant(uint256,uint256[]) returns (uint256) => NONDET
    //_calcOutGivenIn(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) => NONDET
    //_calcInGivenOut(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) => NONDET
    //_calcBptOutGivenExactTokensIn(uint256,uint256[],uint256[],uint256,uint256,uint256) returns (uint256) => NONDET
    //_calcTokenInGivenExactBptOut(uint256,uint256[],uint256,uint256,uint256,uint256,uint256)returns (uint256) => NONDET
    //_calcBptInGivenExactTokensOut(uint256,uint256[],uint256[],uint256,uint256,uint256) returns (uint256) => NONDET
    //_calcTokenOutGivenExactBptIn(uint256,uint256[],uint256,uint256,uint256,uint256,uint256) returns (uint256) => NONDET
    _getTokenBalanceGivenInvariantAndAllOtherBalances(uint256,uint256[],uint256,uint256) returns (uint256) => NONDET
    //_getRate(uint256[],uint256,uint256) returns (uint256) => NONDET
	//getRate() returns (uint256) => NONDET

	//_onInitializePool(bytes32,address,address,uint256[],bytes) returns (uint256, uint256[]) => NONDET

	//_beforeJoinExit(uint256[]) returns (uint256,uint256[],uint256,uint256) => NONDET

	//// @dev fee collection functions, trying to fix timeouts
	//_getProtocolPoolOwnershipPercentage(uint256[]) returns (uint256) => NONDET
	///_getGrowthInvariants (called by above)

	//// @dev swap functions, trying to fix timeouts
	_swapWithBpt((uint8,address,address,uint256,bytes32,uint256,address,address,bytes),uint256[],uint256,uint256,uint256[]) returns (uint256) => NONDET
	//_doExitSwap(bool,uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256,uint256) => NONDET
	//_doJoinSwap(bool,uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256,uint256) => NONDET
	
	//// @dev join functions, trying to fix timeouts
	//_onJoinPool(bytes32,address,address,uint256[],uint256,uint256,uint256[],bytes) returns (uint256, uint256[]) => NONDET
	_doJoin(uint256[], uint256, uint256, uint256, uint256[], bytes) returns (uint256, uint256[]) => NONDET;
	//_joinExactTokensInForBPTOut(uint256, uint256, uint256, uint256[], uint256[], bytes) returns (uint256, uint256[]) => NONDET;
    //_joinTokenInForExactBPTOut(uint256, uint256, uint256, uint256[], bytes) returns (uint256, uint256[]) => NONDET;

	//// @dev exit functions, trying to fix timeouts
	//_onExitPool(bytes32,address,address,uint256[],uint256,uint256,uint256[],bytes) returns (uint256, uint256[]) => NONDET
	_doExit(uint256[], uint256, uint256, uint256, uint256[], bytes) returns (uint256, uint256[]) => NONDET;
    //_exitBPTInForExactTokensOut(uint256, uint256, uint256, uint256[], uint256[], bytes) returns (uint256, uint256[]) => NONDET;
    //_exitExactBPTInForTokenOut(uint256, uint256, uint256, uint256[], bytes) returns (uint256, uint256[]) => NONDET;

	//_mutateAmounts(uint256[],uint256[],bool) => NONDET

	//_updateInvariantAfterJoinExit(uint256,uint256[],uint256,uint256,uint256) => NONDET
    
	// scaling
	_upscaleArray(uint256[],uint256[]) => NONDET
	_downscaleUpArray(uint256[],uint256[]) => NONDET
	_downscaleDownArray(uint256[],uint256[]) => NONDET

	// mint/burn
	//_mintPoolTokens(address, uint256) => NONDET


	//// @dev "view" functions that call internal function with function pointers as input
    queryJoin(bytes32,address,address,uint256[],uint256,uint256,bytes) returns (uint256, uint256[]) => NONDET
    queryExit(bytes32,address,address,uint256[],uint256,uint256,bytes) returns (uint256, uint256[]) => NONDET
	
	//// @dev functions that take function pointers as inputs, can't handle
	//_mutateAmounts(uint256[],uint256[],function (uint256,uint256) pure returns (uint256))
	//_queryAction(bytes32,address,address,uint256[],uint256,uint256,bytes,function (bytes32,address,address,uint256[],uint256,uint256,uint256[],bytes) returns (uint256,uint256[]),function (uint256[],uint256[]) view)

	//// @dev envfree functions
	inRecoveryMode() returns (bool) envfree
}

rule sanity(method f) filtered { f ->
	f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector 
    ||
    f.selector == onExitPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector
	||
	f.selector == onSwap((uint8,address,address,uint256,bytes32,uint256,address,address,bytes),uint256[],uint256,uint256).selector
} {
	env e;
	calldataarg args;
	require !inRecoveryMode();
	require totalSupply() > 0;
	f(e,args);
	assert false;
}
