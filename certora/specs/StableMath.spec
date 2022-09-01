/*
    This is a specification file for smart contract verification with the Certora prover.
    For more information, visit: https://www.certora.com/
*/

//import '../helpers/erc20.spec'

//using otherContractName as internalName


////////////////////////////////////////////////////////////////////////////
//                      Methods                                           //
////////////////////////////////////////////////////////////////////////////

methods {
	//// @dev stable math
    _calculateInvariant(uint256,uint256[]) returns (uint256) envfree
    _calcOutGivenIn(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) envfree
    _calcInGivenOut(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) envfree
    _calcBptOutGivenExactTokensIn(uint256,uint256[],uint256[],uint256,uint256) returns (uint256) envfree
    _calcTokenInGivenExactBptOut(uint256,uint256[],uint256,uint256,uint256,uint256)returns (uint256) envfree
    _calcBptInGivenExactTokensOut(uint256,uint256[],uint256[],uint256,uint256) returns (uint256) envfree
    _calcTokenOutGivenExactBptIn(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) envfree
	_calcTokensOutGivenExactBptIn(uint256[],uint256,uint256) returns (uint256[]) envfree
    _calcDueTokenProtocolSwapFeeAmount(uint256 ,uint256[],uint256,uint256,uint256) returns (uint256) envfree
    _getTokenBalanceGivenInvariantAndAllOtherBalances(uint256,uint256[],uint256,uint256) returns (uint256) envfree
    _getRate(uint256[],uint256,uint256) returns (uint256) envfree

    //// @dev variables
    _MIN_AMP() returns(uint256) envfree
    _MAX_AMP() returns(uint256) envfree
    _AMP_PRECISION() returns(uint256) envfree
    _MAX_STABLE_TOKENS() returns(uint256) envfree
    loopIt(uint256,uint256,uint256,uint256,uint256[]) returns (uint256,uint256) envfree
    loopIt1(uint256,uint256,uint256,uint256,uint256[]) returns (uint256) envfree

    //// @dev helpers
    getIndex(uint256[],uint256) returns(uint256) envfree
    getLength(uint256[]) returns(uint256) envfree
    getFloor(uint256[]) returns(uint256) envfree
    getSum(uint256,uint256[]) returns(uint256) envfree
    debug(uint256) returns(uint256) envfree
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

// want to prove invariant >= min * n
rule invariantGteMinBalTimesNumTokens {
    uint256 amp;
    uint256[] balances;

    require getLength(balances) == 1;
    require amp >= _MIN_AMP() && amp <= _MAX_AMP();

    uint256 floor = getFloor(balances);
    uint256 D = _calculateInvariant(amp, balances);

    assert D >= floor;
}

// initial loop call results in invariant > min * n
    // for invar (output) to be >= min * n we need output = numer/denom >= min * n
    // this is true if numer >= denom * min * n
    // not numer/denom < min*n
    // 
rule invariantGteMinBalTimesNumTokensPerLoopInit {
    uint256 ampTimesTotal; uint256[] balances;

    uint256 numTokens = getLength(balances);
    uint256 sum = getSum(numTokens, balances);
    uint256 floor = getFloor(balances);

    require numTokens > 1 && numTokens <= 5;

    uint256 D = loopIt1(sum, numTokens, ampTimesTotal, sum, balances); 

    assert D >= floor;
}

rule invariantGteMinBalTimesNumTokensPerLoopPreserve {
    uint256 invar; uint256 ampTimesTotal; uint256[] balances;

    uint256 numTokens = getLength(balances);
    uint256 sum = getSum(numTokens, balances);
    uint256 floor = getFloor(balances);

    require invar >= floor;
    require numTokens > 1 && numTokens <= 5;

    uint256 D = loopIt1(invar, numTokens, ampTimesTotal, sum, balances);

    assert D >= floor;
}

// _calculateInvariant
// Balances same => returns sum of balance (prop)
// Balances not same => lowest balance * amp? Other coifs


// Amp can’t equal 0, must be in range (1 to 5000)

////////////////////////////////////////////////////////////////////////////
//                       Helper Functions                                 //
////////////////////////////////////////////////////////////////////////////

// TODO: Any additional helper functions

