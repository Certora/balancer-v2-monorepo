// import "../helpers/errequireOrderc20.spec"

// using DummyERC20A as _token0
// using DummyERC20B as _token1
// using ComposableStablePoolHarness as _token2
// using DummyERC20D as _token3
// using DummyERC20E as _token4
// using DummyERC20F as _token5

////////////////////////////////////////////////////////////////////////////
//                      Methods                                           //
////////////////////////////////////////////////////////////////////////////

methods {
    // getters
    totalTokensBalance(address u) returns (uint256) envfree
    totalTokensBalance() returns (uint256) envfree
    inRecoveryMode() returns (bool) envfree
    _getTotalTokens() envfree
    requireOrder(address) envfree
    totalSupply() envfree
    balanceOf(address) returns (uint256) envfree
    getJoinKind(bytes) returns (uint8) envfree
    _MAX_AMP_UPDATE_DAILY_RATE() returns (uint256) envfree
    _MIN_UPDATE_TIME() returns (uint256) envfree
    _AMP_PRECISION() returns (uint256) envfree
    maxAmp() returns (uint256) envfree
    minAmp() returns (uint256) envfree
	// stable math
    // _calculateInvariant(uint256,uint256[]) returns (uint256) => DISPATCHER(true)
    // _calcOutGivenIn(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) => DISPATCHER(true)
    // _calcInGivenOut(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) => DISPATCHER(true)
    // _calcBptOutGivenExactTokensIn(uint256,uint256[],uint256[],uint256,uint256,uint256) returns (uint256) => DISPATCHER(true)
    // _calcTokenInGivenExactBptOut(uint256,uint256[],uint256,uint256,uint256,uint256,uint256)returns (uint256) => DISPATCHER(true)
    // _calcBptInGivenExactTokensOut(uint256,uint256[],uint256[],uint256,uint256,uint256) returns (uint256) => DISPATCHER(true)
    // _calcTokenOutGivenExactBptIn(uint256,uint256[],uint256,uint256,uint256,uint256,uint256) returns (uint256) => DISPATCHER(true)
    // _getTokenBalanceGivenInvariantAndAllOtherBalances(uint256,uint256[],uint256,uint256) returns (uint256) => DISPATCHER(true)
    // _getRate(uint256[],uint256,uint256) returns (uint256) => DISPATCHER(true)

    // _calcOutGivenIn(uint256 amplificationParameter, uint256[] balances,
    //     uint256 tokenIndexIn,
    //     uint256 tokenIndexOut,
    //     uint256 tokenAmountIn,
    //     uint256 invariant) returns (uint256) 
    //     => ghost_calcOutGivenIn(amplificationParameter, balances, tokenIndexIn, tokenIndexOut, tokenAmountIn, invariant);
	// stable pool
    getBptIndex() returns (uint256) envfree
	_getAmplificationParameter() returns (uint256,bool)

    // _calcTokenInGivenExactBptOut(
    //     uint256 amp,
    //     uint256[] balances,
    //     uint256 tokenIndex,
    //     uint256 bptAmountOut,
    //     uint256 bptTotalSupply,
    //     uint256 swapFeePercentage) returns (uint256)
    //     => ghost_calcTokenInGivenExactBptOut(amp, balances, tokenIndex, bptAmountOut, bptTotalSupply, swapFeePercentage);

    // vault 
    // getPoolTokens(bytes32) returns (address[], uint256[]) => NONDET
    // getPoolTokenInfo(bytes32,address) returns (uint256,uint256,uint256,address) => NONDET
    getVault() returns address envfree;
    getAuthorizor() returns(address)=> NONDET
    registerPool(uint8 specialization) returns (bytes32) => NONDET
    registerTokens(bytes32, address[], address[]) => NONDET
    getPoolTokenInfo(bytes32, address) returns (int256, uint256, uint256, address) => NONDET;
    getPoolTokens(bytes32) returns (address[], uint256[], uint256) => NONDET;
    getProtocolFeesCollector() returns (address) => NONDET;

    // onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes) returns (uint256[], uint256[]) => NONDET;
    // _onInitializePool(bytes32,address,address,uint256[],bytes) returns (uint256, uint256[]) => NONDET;

    // _onJoinPool(bytes32,address,address,uint256[],uint256,uint256,uint256[],bytes) returns (uint256, uint256[]) => NONDET;
    // _mintPoolTokens(address, uint256) => NONDET;
    _upscaleArray(uint256[], uint256[]) => NONDET;
    _downscaleUp(uint256, uint256) => NONDET;
    _downscaleUpArray(uint256[], uint256[]) => NONDET;
    _downscaleDownArray(uint256[], uint256[]) => NONDET;

    // _payProtocolFeesBeforeJoinExit(uint256[]) returns (uint256, uint256[]) => NONDET;
    // _getAmplificationParameter() returns (uint256, bool) => NONDET; 
    // _doJoin(uint256[], uint256, uint256, uint256, uint256[], bytes) returns (uint256, uint256[]) => NONDET;

    _joinExactTokensInForBPTOut(uint256, uint256, uint256, uint256[], uint256[], bytes) returns (uint256, uint256[]) => NONDET;
    _joinTokenInForExactBPTOut(uint256, uint256, uint256, uint256[], bytes) returns (uint256, uint256[]) => NONDET;

    // onExitPool(bytes32,address,address,uint256[],uint256,uint256,bytes) returns (uint256[], uint256[]) => NONDET;
    // _doRecoveryModeExit(uint256[],uint256,bytes) returns (uint256, uint256[]) => NONDET;

    // _beforeSwapJoinExit() => NONDET;
    // _scalingFactors() returns (uint256[]) => NONDET;
    // _onExitPool(bytes32,address,address,uint256[],uint256,uint256,uint256[],bytes) returns (uint256, uint256[]) => NONDET;
    // _downscaleDownArray(uint256[], uint256[]) => NONDET;
    // _burnPoolTokens(address, uint256) => NONDET;

    // _doExit(uint256[], uint256, uint256, uint256, uint256[], bytes) returns (uint256, uint256[]) => NONDET;
    _exitBPTInForExactTokensOut(uint256, uint256, uint256, uint256[], uint256[], bytes) returns (uint256, uint256[]) => NONDET;
    _exitExactBPTInForTokenOut(uint256, uint256, uint256, uint256[], bytes) returns (uint256, uint256[]) => NONDET;


    _updateInvariantAfterJoinExit(int256, uint256[], uint256,uint256, uint256) => NONDET;

    // IRateProvider
    getRate() returns (uint256) => NONDET
    // _getAuthorizor() returns address => DISPATCHER(true)
    // _canPerform(bytes32, address) returns (bool) => NONDET
    // canPerform(bytes32, address, address) returns (bool) => NONDET
    // // harness functions
    // setRecoveryMode(bool)

    // balanceOf(address) returns(uint256) envfree => DISPATCHER(true)
    // _token0.balanceOf(address) returns(uint256) envfree
    // _token1.balanceOf(address) returns(uint256) envfree
    // // _token2.balanceOf(address) returns(uint256) envfree
    // _token3.balanceOf(address) returns(uint256) envfree
    // _token4.balanceOf(address) returns(uint256) envfree
    // _token5.balanceOf(address) returns(uint256) envfree

    getToken(uint256 num) returns(address) envfree
    getTotalTokens() returns (uint256) envfree

    // mul(uint256 x, uint256 y) => ghost_multiplication(x, y);
    // mulUp(uint256 x, uint256 y) => ghost_multiplication_round(x, y);
    // mulDown(uint256 x, uint256 y) => ghost_multiplication_round(x, y);
    // div(uint256 x, uint256 y) => ghost_division(x, y);
    // divUp(uint256 x, uint256 y) => ghost_division_round(x, y);
    // divDown(uint256 x, uint256 y) => ghost_division_round(x, y);

    insertUint(bytes32,uint256,uint256,uint256) returns (bytes32) => NONDET;
    insertInt(bytes32,int256,uint256,uint256) returns (bytes32) => NONDET;
    encodeUint(uint256,uint256,uint256) returns (bytes32) => NONDET;
    encodeInt(int256,uint256,uint256) returns (bytes32) => NONDET;
    decodeUint(bytes32,uint256,uint256) returns (uint256) => NONDET;
    decodeInt(bytes32,uint256,uint256) returns (int256) => NONDET;
    decodeBool(bytes32, uint256) returns (bool) => NONDET;
    insertBits192(bytes32,bytes32,uint256) returns (bytes32) => NONDET;
    insertBool(bytes32,bool,uint256) returns (bytes32) => NONDET;
}


////////////////////////////////////////////////////////////////////////////
//                    Ghosts, hooks and definitions                       //
////////////////////////////////////////////////////////////////////////////

/// A ghost tracking values for an invariant given two token balances;
///
/// @dev we assume only 2 tokens in a pool and that a bounded arbitrary value for the invariant
ghost mapping(uint256 => mapping(uint256 => uint256)) determineInvariant;

// assume sum of all balances initially equals 0
ghost sum_all_users_BPT() returns uint256 {
    init_state axiom sum_all_users_BPT() == 0;
}

// everytime `balances` is called, update `sum_all_users_BPT` by adding the new value and subtracting the old value
hook Sstore _balances[KEY address user] uint256 balance (uint256 old_balance) STORAGE {
  havoc sum_all_users_BPT assuming sum_all_users_BPT@new() == sum_all_users_BPT@old() + balance - old_balance;
}

ghost ghost_multiplication(uint256,uint256) returns uint256 {
    axiom forall uint256 y1. forall uint256 y2. forall uint256 x1. forall uint256 x2. 
        (x1 > x2 => ghost_multiplication(x1, y1) > ghost_multiplication(x2, y1)) &&
        (y1 > y2 => ghost_multiplication(x1, y1) > ghost_multiplication(x1, y2)) &&
        ((x1 == 0 || y1 == 0) => ghost_multiplication(x1,y1) == 0);
}

ghost ghost_multiplication_round(uint256,uint256) returns uint256 {
    axiom forall uint256 y1. forall uint256 y2. forall uint256 x1. forall uint256 x2. 
        (x1 > x2 => ghost_multiplication_round(x1, y1) >= ghost_multiplication_round(x2, y1)) &&
        (y1 > y2 => ghost_multiplication_round(x1, y1) >= ghost_multiplication_round(x1, y2)) &&
        ((x1 == 0 || y1 == 0) => ghost_multiplication_round(x1,y1) == 0);
}

ghost ghost_division(uint256,uint256) returns uint256 {
    axiom forall uint256 x1. forall uint256 x2. forall uint256 y1. forall uint256 y2.         
        (x1 == 0 => ghost_division(x1, y1) == 0 &&
        x1 > x2 => ghost_division(x1, y1) > ghost_division(x2, y1) &&
        y1 > y2 => ghost_division(x1, y1) < ghost_division(x1, y2)) ||
        y1 == 1 => ghost_division(x1, y1) == x1;
}

ghost ghost_division_round(uint256,uint256) returns uint256 {
    axiom forall uint256 x1. forall uint256 x2. forall uint256 y1. forall uint256 y2.         
        (x1 == 0 => ghost_division_round(x1, y1) == 0 &&
        x1 > x2 => ghost_division_round(x1, y1) >= ghost_division_round(x2, y1) &&
        y1 > y2 => ghost_division_round(x1, y1) <= ghost_division_round(x1, y2)) ||
        y1 == 1 => ghost_division_round(x1, y1) == x1;
}

////////////////////////////////////////////////////////////////////////////
//                            Invariants                                  //
////////////////////////////////////////////////////////////////////////////

/// @title Sum of all users' BPT balance must be less than or equal to BPT's `totalSupply`
invariant solvency()
    totalSupply() >= sum_all_users_BPT()

////////////////////////////////////////////////////////////////////////////
//                               Rule                                     //
////////////////////////////////////////////////////////////////////////////

/// @title `totalSupply` must be non-zero if and only if `onJoinPool` is successfully called. Additionally, the balance of the zero adress must be non-zero if `onJoinPool` was successfully called.
/// @dev Calling `onJoinPool` for the first time initializes the pool, minting some BPT to the zero address.
// @status? passing with rule_sanity advanced
rule onlyOnJoinPoolCanAndMustInitialize(method f) {
    env e; calldataarg args; address zero;
    require totalSupply() == 0;
    require zero == 0;
    
    f(e, args);
    
    assert totalSupply() > 0  <=> f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector, "onJoinPool must be the only function that can initialize a pool and must initialize if called";
    assert f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector => balanceOf(zero) > 0, "zero address must be minted some tokens on initialization";
}

// @title The zero address's BPT balance can never go from non-zero to zero.
// @status? passing with rule_sanity advanced
rule cantBurnZerosBPT(method f) {
    address  zero = 0;
    require balanceOf(zero) > 0;
    env e; calldataarg args;
    f(e, args); // vacuous for onSwap since ERC20 transfer revert when transferring to 0 address
    assert balanceOf(zero) > 0, "zero address must always have non-zero balance";
}

// balances == 0 && totalSupply == 0 => no mint
// everything zero or all nonzero
// assumption about invariant
// assumption 2: balances increase if invariant increased
// assumption 3: _joinTokenInForExactBPTOut type join (only nontimeout, also makes sense)
rule noFreeMinting(method f) {

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

    env e;
    bytes32 poolId; address sender; address recipient; uint256[] balances; 
    uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;

    if f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        require sender != currentContract; // times out if I remove this 
        require getJoinKind(userData) == 2;
        onJoinPool(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData);
    } else {
        calldataarg args;
        f(e, args);

    }
    uint256 totalBpt_ = totalSupply();
    uint256 totalTokens_ = totalTokensBalance();

    assert totalBpt_>_totalBpt => totalTokens_>_totalTokens, "an increase in total BPT must lead to an increase in pool's total tokens";
}

////////////////////////////////////////////////////////////////////////////
//                            Helper Functions                            //
////////////////////////////////////////////////////////////////////////////

function setup(env e) { 
    // require _token0<_token1 && _token1<_token2 && _token2<_token3 && _token3<_token4 && _token4<_token5;
    // require currentContract == getToken(getBptIndex());
    // require e.msg.sender < _token0;
    //require getTotalTokens()>2 && getTotalTokens()<7;
    // require getBptIndex() < getTotalTokens();
    //requireOrder(e.msg.sender);
}

// invariant must be greater than the sum of pool's token balances and less than the product 
function newCalcInvar(uint256 balance1, uint256 balance2) returns uint256 {
    uint256 invar;
    require invar >= balance1 + balance2;
    require invar <= balance1 * balance2;
    //require determineInvariant[balance1][balance2] == invar;
    return invar;
}

// if invariant increases, the new balance should be greater than the previous balance.
function newGetTokenBalance(uint256 balance1, uint256 balance2, uint256 newInvariant, uint256 index) returns uint256 {
    uint256 newBalance;
    uint256 oldInvariant = determineInvariant[balance1][balance2];
    if (index == 0) {
        require newInvariant > oldInvariant => newBalance > balance1;
    } else {
        require newInvariant > oldInvariant => newBalance > balance2;
    }
    return newBalance;
}

//////********** AMPLIFICATION FACTOR AND RECOVERY/PAUSE RULES ***********//////////////
// should be moved to seperate file or deleted if they are already in a new file

// Amplification factor

// returns value encoded in solidity for 1 day
definition DAY() returns uint256 = 1531409238;


// /// @rule amplfiicationFactorFollowsEndTime
// /// @description: After starting an amplification factor increase and calling an artbirary function, for some e later than initial increase
// /// amplification factor must be less than value set
// rule amplificationFactorFollowsEndTime(method f) {
//     env e; calldataarg args;
//     uint256 endValue; uint256 endTime;
//     uint256 startValue; bool isUpdating;
//     startValue, isUpdating = _getAmplificationParameter(e);

//     assert !inRecoveryMode();
//     startAmplificationParameterUpdate(e, endValue, endTime);
//     f(e, args); // call some arbitrary function

//     env e_post;
//     require e_post.block.timestamp > e.block.timestamp;
//     require e_post.block.timestamp < endTime;
//     uint256 currentParam;
//     currentParam, isUpdating = _getAmplificationParameter(e_post);

//     if (endValue > startValue) {
//         assert currentParam < endValue, "getter: parameter increased too fast";
//         assert currentParam > startValue, "amplification did not increase";
//     } else {
//         assert currentParam > endValue, "getter: parameter decreased too fast";
//         assert currentParam < startValue, "amplification did not decrease";
//     }
// }

// /// @rule: amplificationFactorTwoDayWait
// /// @description: start the amplification factor changing. Wait 2 days. Check the value at that timestamp, and then assert the value doesn't change after
// rule amplificationFactorTwoDayWait(method f) {
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

// /// @rule: amplificationFactorNoMoreThanDouble
// /// @descrption: the amplification factor may not increase by more than a factor of two in a given day
// rule amplificationFactorNoMoreThanDouble(method f) {
//     env e; 
//     uint256 endValue; uint256 endTime;
//     uint256 startValue; bool isUpdating;
//     startValue, isUpdating = _getAmplificationParameter(e);
//     startAmplificationParameterUpdate(e, endValue, endTime);

//     calldataarg args; env e_f;
//     f(e_f, args);

//     env e_incr;
//     require e_incr.block.timestamp <= e.block.timestamp + (2 * DAY());
//     uint256 actualEndValue;
//     actualEndValue, isUpdating = _getAmplificationParameter(e_incr);

//     assert actualEndValue <= startValue * 2, "amplification factor more than doubled";
// }

function getAmplificationFactor(env e) returns uint256 {
    uint256 param; bool updating;
    param, updating = _getAmplificationParameter(e);
    return param;
}

invariant amplificationFactorBounded(env e)
    getAmplificationFactor(e) <= maxAmp() && getAmplificationFactor(e) >= minAmp()
{ preserved {
    // require !initialized() => getAmplificationFactor(e) == 0; // amplification factor is 0 before initialization
    require _MAX_AMP_UPDATE_DAILY_RATE() == 2;
    require _MIN_UPDATE_TIME() == DAY();
    require _AMP_PRECISION() == 1000;
} }


/// @rule amplfiicationFactorFollowsEndTime
/// @description: After starting an amplification factor increase and calling an artbirary function, for some e later than initial increase
/// amplification factor must be less than value set
/// @notice: passes
rule amplificationFactorFollowsEndTime(method f) {
    require _MAX_AMP_UPDATE_DAILY_RATE() == 2;
    require _MIN_UPDATE_TIME() == DAY();
    require _AMP_PRECISION() == 1000; 

    env e; calldataarg args;
    uint256 endValue; uint256 endTime;
    uint256 startValue; bool isUpdating;
    startValue, isUpdating = _getAmplificationParameter(e);

    assert !inRecoveryMode();
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

/// @rule: amplificationFactorNoMoreThanDouble
/// @descrption: the amplification factor may not increase by more than a factor of two in a given day
/// @notice: passes
rule amplificationFactorNoMoreThanDouble(method f) {
    require _MAX_AMP_UPDATE_DAILY_RATE() == 2;
    require _MIN_UPDATE_TIME() == DAY();
    require _AMP_PRECISION() == 1000;

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
    require _AMP_PRECISION() == 1000;

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
