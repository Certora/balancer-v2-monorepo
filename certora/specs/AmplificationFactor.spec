import "../helpers/erc20.spec"

using DummyERC20A as _token0
using DummyERC20B as _token1
using DummyERC20C as _token2
using DummyERC20D as _token3
using DummyERC20E as _token4

////////////////////////////////////////////////////////////////////////////
//                      Methods                                           //
////////////////////////////////////////////////////////////////////////////


// we can nondet more heavily for amplification factor, a lot of the main functions shouldn't affect it
// ^ the above could be a very good rule
methods {
    //// @dev envfree functions
    totalTokensBalance() returns (uint256) envfree
    totalTokensBalanceUser(address) returns (uint256) envfree
    totalFees() returns (uint256) envfree
    inRecoveryMode() returns (bool) envfree
    _MIN_UPDATE_TIME() returns (uint256) envfree
    _MAX_AMP_UPDATE_DAILY_RATE() returns (uint256) envfree
    //// @dev heavy but important function, want to fix timeout
    //_doExit(uint256[],uint256[],bytes) returns (uint256, uint256[]) => NONDET


	//// @dev stable math
    _calculateInvariant(uint256,uint256[]) returns (uint256) => NONDET
    // _calcOutGivenIn(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) => NONDET
    // _calcInGivenOut(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) => NONDET
    // _calcBptOutGivenExactTokensIn(uint256,uint256[],uint256[],uint256,uint256) returns (uint256) => NONDET
    // _calcTokenInGivenExactBptOut(uint256,uint256[],uint256,uint256,uint256,uint256)returns (uint256) => NONDET
    // _calcBptInGivenExactTokensOut(uint256,uint256[],uint256[],uint256,uint256) returns (uint256) => NONDET
    // _calcTokenOutGivenExactBptIn(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) => NONDET
	// _calcTokensOutGivenExactBptIn(uint256[],uint256,uint256) returns (uint256[]) => NONDET
    // _calcDueTokenProtocolSwapFeeAmount(uint256 ,uint256[],uint256,uint256,uint256) returns (uint256) => NONDET
    _getTokenBalanceGivenInvariantAndAllOtherBalances(uint256,uint256[],uint256,uint256) returns (uint256) => NONDET
    // _getRate(uint256[],uint256,uint256) returns (uint256) => NONDET

    //// @dev "view" functions that call internal function with function pointers as input
    queryJoin(bytes32,address,address,uint256[],uint256,uint256,bytes) returns (uint256, uint256[]) => NONDET
    queryExit(bytes32,address,address,uint256[],uint256,uint256,bytes) returns (uint256, uint256[]) => NONDET
    //// @dev vault 
    getPoolTokens(bytes32) returns (address[], uint256[]) => NONDET
    getPoolTokenInfo(bytes32,address) returns (uint256,uint256,uint256,address) => NONDET
    getVault() returns address envfree;
    // authorizor functions
    getAuthorizor() returns address => NONDET
    _getAuthorizor() returns address => NONDET
    _canPerform(bytes32, address) returns (bool) => DISPATCHER(true)
    canPerform(bytes32, address, address) returns (bool) => DISPATCHER(true)
    // harness functions
    setRecoveryMode(bool)
    minAmp() returns (uint256) envfree
    maxAmp() returns (uint256) envfree
    initialized() returns (bool) envfree
    AMP_PRECISION() returns (uint256) envfree

    _token0.balanceOf(address) returns(uint256) envfree
    _token1.balanceOf(address) returns(uint256) envfree
    _token2.balanceOf(address) returns(uint256) envfree
    _token3.balanceOf(address) returns(uint256) envfree
    _token4.balanceOf(address) returns(uint256) envfree

    getToken0() returns(address) envfree
    getToken1() returns(address) envfree
    getToken2() returns(address) envfree
    getToken3() returns(address) envfree
    getToken4() returns(address) envfree
    getTotalTokens() returns (uint256) envfree

}

// Amplification factor

// returns value encoded in solidity for 1 day
definition DAY() returns uint256 = 1531409238;

function getAmplificationFactor(env e) returns uint256 {
    uint256 param; bool updating;
    param, updating = _getAmplificationParameter(e);
    return param;
}

/// @invariant: amplifcationFactorBounded
/// @description: the amplificationFactor must stay between the minimum and maximum values hard coded as minAmp and maxAmp
/// @notice: this fails on the instate because there are no checks on the initial value of the amplfication factor
/// @notice: passes on the preserved 
invariant amplificationFactorBounded(env e)
    getAmplificationFactor(e) <= maxAmp() * AMP_PRECISION() && getAmplificationFactor(e) >= minAmp()
{ preserved {
    require !initialized() => getAmplificationFactor(e) == 0; // amplification factor is 0 before initialization
    require _MAX_AMP_UPDATE_DAILY_RATE() == 2;
    require _MIN_UPDATE_TIME() == DAY();
    require AMP_PRECISION() == 1000;
    require e.block.timestamp < 10000000; // large number but less than maxint
} }


/// @rule amplfiicationFactorFollowsEndTime
/// @description: After starting an amplification factor increase and calling an artbirary function, for some e later than initial increase
/// amplification factor must be less than value set
/// @notice: passes
rule amplificationFactorFollowsEndTime(method f) {
    require _MAX_AMP_UPDATE_DAILY_RATE() == 2;
    require _MIN_UPDATE_TIME() == DAY();
    require AMP_PRECISION() == 1000;

    env e; calldataarg args;
    uint256 endValue; uint256 endTime;
    uint256 startValue; bool isUpdating;
    startValue, isUpdating = _getAmplificationParameter(e);

    require !inRecoveryMode();
    startAmplificationParameterUpdate(e, endValue, endTime);
    f(e, args); // call some arbitrary function

    env e_post;
    require e_post.block.timestamp > e.block.timestamp;
    require e_post.block.timestamp < endTime;
    uint256 currentParam;
    currentParam, isUpdating = _getAmplificationParameter(e_post);

    if (endValue > startValue) {
        assert currentParam < endValue, "getter: parameter increased too fast";
        assert currentParam > startValue, "amplification did not increase";
    } else {
        assert currentParam > endValue, "getter: parameter decreased too fast";
        assert currentParam < startValue, "amplification did not decrease";
    }
}

// /// @rule: amplificationFactorTwoDayWait
// /// @description: start the amplification factor changing. Wait 2 days. Assert value is what we set to after that period
// /// @notice: don't think the code actually follows this
// rule amplificationFactorTwoDayWait(method f) filtered {f -> (f.selector != startAmplificationParameterUpdate(uint256, uint256).selector}
// {
//     require _MAX_AMP_UPDATE_DAILY_RATE() == 2;
//     require _MIN_UPDATE_TIME() == DAY();
//     // require AMP_PRECISION() == 1000;

//     env e; 
//     uint256 endValue; uint256 endTime;
//     uint256 startValue; bool isUpdating;
//     startValue, isUpdating = _getAmplificationParameter(e);
//     startAmplificationParameterUpdate(e, endValue, endTime);

//     env e_f; calldataarg args;
//     f(e_f, args);

//     env e_2days;
//     require e_2days.block.timestamp == e.block.timestamp + (2 * DAY());
//     uint256 actualEndValue;
//     actualEndValue, isUpdating = _getAmplificationParameter(e_2days);

//     env e_post;
//     require e_post.block.timestamp > e_2days.block.timestamp;
//     uint256 endValuePost;
//     endValuePost, isUpdating = _getAmplificationParameter(e_post);
//     assert endValuePost == actualEndValue, "amplfication factor still changing after 2 days";
// }

/// @rule: amplificationFactorNoMoreThanDouble
/// @descrption: the amplification factor may not increase by more than a factor of two in a given day
/// @notice: passes
rule amplificationFactorNoMoreThanDouble(method f) {
    require _MAX_AMP_UPDATE_DAILY_RATE() == 2;
    require _MIN_UPDATE_TIME() == DAY();
    require AMP_PRECISION() == 1000;

    env e; 
    uint256 endValue; uint256 endTime;
    uint256 startValue; bool isUpdating;

    startValue, isUpdating = _getAmplificationParameter(e);
    startAmplificationParameterUpdate(e, endValue, endTime);

    calldataarg args; env e_f;
    f(e_f, args);

    env e_incr;
    require e_incr.block.timestamp <= e.block.timestamp + (2 * DAY());
    uint256 actualEndValue;
    actualEndValue, isUpdating = _getAmplificationParameter(e_incr);

    assert actualEndValue <= startValue * 2, "amplification factor more than doubled";
}

/// @rule: amplificationFactorUpdatingOneDay
/// @descrption: if the amplification factor starts updating, then it must continue so for one day
/// @notice: passes
rule amplificationFactorUpdatingOneDay(method f) {
    require _MIN_UPDATE_TIME() == DAY();
    require _MAX_AMP_UPDATE_DAILY_RATE() == 2;
    require AMP_PRECISION() == 1000;

    env e_pre;
    uint256 endValue; uint256 endTime;
    
    // require endValue >= minAmp();
    // require endValue <= maxAmp();

    uint256 startValue; bool isUpdating;
    startValue, isUpdating = _getAmplificationParameter(e_pre);
    require endValue != startValue;
    require !isUpdating; // can't already be updating
    startAmplificationParameterUpdate(e_pre, endValue, endTime);

    env e_post;
    require (e_post.block.timestamp >= e_pre.block.timestamp) && (e_post.block.timestamp < e_pre.block.timestamp + DAY());
    uint256 actualEndValue; bool isUpdating_;
    actualEndValue, isUpdating_ = _getAmplificationParameter(e_post);
    assert isUpdating_, "must still be updating";
}