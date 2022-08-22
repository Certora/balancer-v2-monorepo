import "../helpers/erc20.spec"

methods {
	// stable math
    _calculateInvariant(uint256,uint256[]) returns (uint256) => NONDET
    _calcOutGivenIn(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) => NONDET
    _calcInGivenOut(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) => NONDET
    _calcBptOutGivenExactTokensIn(uint256,uint256[],uint256[],uint256,uint256,uint256) returns (uint256) => NONDET
    _calcTokenInGivenExactBptOut(uint256,uint256[],uint256,uint256,uint256,uint256,uint256)returns (uint256) => NONDET
    _calcBptInGivenExactTokensOut(uint256,uint256[],uint256[],uint256,uint256,uint256) returns (uint256) => NONDET
    _calcTokenOutGivenExactBptIn(uint256,uint256[],uint256,uint256,uint256,uint256,uint256) returns (uint256) => NONDET
    _getTokenBalanceGivenInvariantAndAllOtherBalances(uint256,uint256[],uint256,uint256) returns (uint256) => NONDET
    _getRate(uint256[],uint256,uint256) returns (uint256) => NONDET

	_doJoin(uint256[], uint256, uint256, uint256, uint256[], bytes) returns (uint256, uint256[]) => NONDET;
	_doExit(uint256[], uint256, uint256, uint256, uint256[], bytes) returns (uint256, uint256[]) => NONDET;
}

rule sanity(method f)
{
	env e;
	calldataarg args;
	f(e,args);
	assert false;
}
