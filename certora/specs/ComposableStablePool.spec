/***
## Assumptions and Simplifications
ComposableStablePool contract handles up to 6 tokens including its native BPT token. However, in order to avoid prover timing out, we need to limit totalTokens and loop iterations to 3, and, at times, even to 2, while fixing the non-bpt token to 1.

For rules regarding the amplification factor we make the following assumptions about the state variables of the system:
* The minimum update time is between 0 and 1 day (`_MIN_UPDATE_TIME`)
* The amplification factor may not increase or decrease by a factor of 2 over a two day period (`_MAX_AMP_UPDATE_DAILY_RATE`)
* The minimum amplification factor is greater than 0 (`_MIN_AMP`)
* The maximum amplifcation factor is between the minimum amplification factor and 100000 (normally this is set to 5000) (`_MAX_AMP`)
Note that many of these variables are hard coded as immutable constants, however the tool will assume any possible values for those constants unless otherwise constrained.    // require _MIN_UPDATE_TIME() <= DAY();
    
#### Harnessing
We harnessed StableMath functions such as _calculateInvariant and _getTokenBalanceGivenInvariantAndAllOtherBalances to return arbitrary but deterministic value given fixed inputs. We also harnessed certain ComposableStablePool functions to expose certain variables that are otherwise non-accessible.
    
#### Munging
To avoid timeouts, we munged certain functions in ComposableStablePool. For example, _getGrowthInvariants() may calculate invariants in different ways given specified inputs, balances or adjustedBalances. However, loops in _getAdjustedBalances() will timeout in most circumstances. We, therefore, munged the inputs to all use balances instead of adjustedBalances. We, then, prove the equivalence of balances and adjustedBalances in relevant conditions.

#### Definitions

*/

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
    initialized() returns (bool) envfree
    _AMP_START_VALUE_OFFSET() returns (uint256) envfree
    _AMP_END_VALUE_OFFSET() returns (uint256) envfree
    _AMP_START_TIME_OFFSET() returns (uint256) envfree
    _AMP_END_TIME_OFFSET() returns (uint256) envfree
    _AMP_VALUE_BIT_LENGTH() returns (uint256) envfree
    _AMP_TIMESTAMP_BIT_LENGTH() returns (uint256) envfree
    _setAmplificationData(uint256, uint256, uint256, uint256) envfree
    getBptIndex() returns (uint256) envfree
	_getAmplificationParameter() returns (uint256,bool)
    getVault() returns address envfree;
    getAuthorizor() returns(address)=> NONDET
    registerPool(uint8 specialization) returns (bytes32) => NONDET
    registerTokens(bytes32, address[], address[]) => NONDET
    getPoolTokenInfo(bytes32, address) returns (int256, uint256, uint256, address) => NONDET;
    getPoolTokens(bytes32) returns (address[], uint256[], uint256) => NONDET;
    getProtocolFeesCollector() returns (address) => NONDET;

    _upscaleArray(uint256[], uint256[]) => NONDET;
    _downscaleUp(uint256, uint256) => NONDET;
    _downscaleUpArray(uint256[], uint256[]) => NONDET;
    _downscaleDownArray(uint256[], uint256[]) => NONDET;

    _joinExactTokensInForBPTOut(uint256, uint256, uint256, uint256[], uint256[], bytes) returns (uint256, uint256[]) => NONDET;
    _joinTokenInForExactBPTOut(uint256, uint256, uint256, uint256[], bytes) returns (uint256, uint256[]) => NONDET;

    _exitBPTInForExactTokensOut(uint256, uint256, uint256, uint256[], uint256[], bytes) returns (uint256, uint256[]) => NONDET;
    _exitExactBPTInForTokenOut(uint256, uint256, uint256, uint256[], bytes) returns (uint256, uint256[]) => NONDET;


    _updateInvariantAfterJoinExit(int256, uint256[], uint256,uint256, uint256) => NONDET;

    // IRateProvider
    getRate() returns (uint256) => NONDET
    canPerform(bytes32, address, address) returns (bool) => ALWAYS(true) // will always approve
    // // harness functions

    getToken(uint256 num) returns(address) envfree
    getTotalTokens() returns (uint256) envfree
    day() returns (uint256) envfree
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
/// @dev passing with rule_sanity advanced
rule onlyOnJoinPoolCanAndMustInitialize(method f) {
    env e; calldataarg args; address zero;
    require totalSupply() == 0;
    require zero == 0;
    
    f(e, args);
    
    assert totalSupply() > 0  <=> f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector, "onJoinPool must be the only function that can initialize a pool and must initialize if called";
    assert f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector => balanceOf(zero) > 0, "zero address must be minted some tokens on initialization";
}

/// @title: cantBurnZerosBPT
/// @notice: The zero address's BPT balance can never go from non-zero to zero.
/// @dev passing with rule_sanity advanced
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

function ampSetup() {
    require _MIN_UPDATE_TIME() <= DAY();
    require _MIN_UPDATE_TIME() > 0;
    // require _MIN_UPDATE_TIME() == DAY();
    require _MAX_AMP_UPDATE_DAILY_RATE() == 2;
    require _AMP_PRECISION() == 1000;
    require maxAmp() > minAmp();
    require minAmp() > 0;
    require maxAmp() < 100000; // normally 5000 
    require _AMP_START_VALUE_OFFSET() == 0;
    require _AMP_END_VALUE_OFFSET() == 64;
    require _AMP_START_TIME_OFFSET() == 128;
    require _AMP_END_TIME_OFFSET() == 192;
    require _AMP_VALUE_BIT_LENGTH() == 64;
    require _AMP_TIMESTAMP_BIT_LENGTH() == 64;
}

function getAmplificationFactor(env e) returns uint256 {
    uint256 param; bool updating;
    param, updating = _getAmplificationParameter(e);
    return param;
}

invariant amplificationFactorBounded(env e)
    getAmplificationFactor(e) <= maxAmp() && getAmplificationFactor(e) >= minAmp()
{ preserved {
    // require !initialized() => getAmplificationFactor(e) == 0; // amplification factor is 0 before initialization
    ampSetup();
    require !initialized() => getAmplificationFactor(e) == 0;
} }


/// @title: amplfiicationFactorFollowsEndTime
/// @notice: After starting an amplification factor increase and calling an artbirary function, for some e later than initial increase
/// amplification factor must be between the start value and target end value.
/// @notice: We split this rule into two cases, amplification factor is increasing and it's decreasing, for the sake of timeouts
/// @dev: passes
rule amplificationFactorFollowsEndTimeDecr(method f) {
    ampSetup();

    env e; calldataarg args;
    uint256 endValue; uint256 endTime;
    uint256 startValue; bool isUpdating;
    startValue, isUpdating = _getAmplificationParameter(e);
    require endValue * _AMP_PRECISION() < startValue;

    // inRecoveryMode();
    startAmplificationParameterUpdate(e, endValue, endTime);
    // f(e, args); // call some arbitrary function

    env e_post;
    require e_post.block.timestamp > e.block.timestamp;
    require e_post.block.timestamp < endTime;

    uint256 currentParam;
    currentParam, isUpdating = _getAmplificationParameter(e_post);

    uint256 actualEndValue;
    actualEndValue, isUpdating = _getAmplificationParameter(e_post);

    assert isUpdating, "is still updating";
    assert actualEndValue <= startValue && actualEndValue >= endValue * _AMP_PRECISION(), "not within proper range";
}

rule amplificationFactorFollowsEndTimeIncr(method f) {
    ampSetup();

    env e; calldataarg args;
    uint256 endValue; uint256 endTime;
    uint256 startValue; bool isUpdating;
    startValue, isUpdating = _getAmplificationParameter(e);
    require endValue * _AMP_PRECISION() > startValue;

    // inRecoveryMode();
    startAmplificationParameterUpdate(e, endValue, endTime);
    // f(e, args); // call some arbitrary function

    env e_post;
    require e_post.block.timestamp > e.block.timestamp;
    require e_post.block.timestamp < endTime;
    uint256 currentParam;
    currentParam, isUpdating = _getAmplificationParameter(e_post);

    require e_post.block.timestamp <= e.block.timestamp + _MIN_UPDATE_TIME();
    uint256 actualEndValue;
    actualEndValue, isUpdating = _getAmplificationParameter(e_post);

    assert isUpdating, "is still updating";
    assert actualEndValue >= startValue && actualEndValue <= endValue * _AMP_PRECISION(), "not within proper range";
}

rule amplificationFactorNoMoreThanDoubleIncr(method f) {
    ampSetup();

    env e; 
    uint256 endValue; uint256 endTime;
    uint256 startValue; bool isUpdating;

    startValue, isUpdating = _getAmplificationParameter(e);
    startAmplificationParameterUpdate(e, endValue, endTime);

    calldataarg args; env e_f;
    // f(e_f, args);

    env e_incr;
    require e_incr.block.timestamp == e.block.timestamp + day();
    require e_incr.block.timestamp <= max_uint256;
    uint256 actualEndValue;
    actualEndValue, isUpdating = _getAmplificationParameter(e_incr);

    assert actualEndValue <= startValue * 2, "amplification factor more than doubled";
}

/// @title: amplificationFactorNoMoreThanDouble
/// @notice: The amplification factor may not increase by more than a factor of two in a given day.
/// @notice: This rule has been split into two cases, increasing and decreasing, for the sake of handling timeouts.
/// @dev: passes
rule amplificationFactorNoMoreThanDoubleDecr(method f) {
    ampSetup();

    env e; 
    uint256 startValue; bool isUpdating;
    startValue, isUpdating = _getAmplificationParameter(e);

    uint256 endValue; uint256 endTime;
    startAmplificationParameterUpdate(e, endValue, endTime);

    calldataarg args; env e_f;
    f(e_f, args);

    env e_incr;
    require e_incr.block.timestamp == e.block.timestamp + day();
    uint256 actualEndValue;
    actualEndValue, _ = _getAmplificationParameter(e_incr);

    assert actualEndValue >= startValue / 2, "amplification factor more than halved";
}

/// @rule: amplificationFactorUpdatingOneDay
/// @descrption: if the amplification factor starts updating, then it must continue so for one day
/// @notice: passes
rule amplificationFactorUpdatingOneDay(method f) {
    ampSetup();

    env e_pre;
    uint256 endValue; uint256 endTime;
    require endTime > e_pre.block.timestamp;

    uint256 startValue; bool isUpdating;
    startValue, isUpdating = _getAmplificationParameter(e_pre);
    require endValue != startValue;
    require !isUpdating; // can't already be updating
    startAmplificationParameterUpdate(e_pre, endValue, endTime);

    env e_post;
    require (e_post.block.timestamp >= e_pre.block.timestamp) && (e_post.block.timestamp < e_pre.block.timestamp + _MIN_UPDATE_TIME());
    uint256 actualEndValue; bool isUpdating_;
    actualEndValue, isUpdating_ = _getAmplificationParameter(e_post);
    assert isUpdating_, "must still be updating";
}


/// @rule: amplificationUpdateCanFinish
/// @description: tests to see if it's possible for an amplification factor that will never realistically finish to exist
/// @dev: Fails with reason
rule amplificationUpdateCanFinish() {
    ampSetup();

    env _e;
    uint256 endValue; uint256 endTime;

    require maxAmp() < 100000;
    uint256 startValue; bool isUpdating;

    startValue, isUpdating = _getAmplificationParameter(_e);
    require !isUpdating;
    require startValue < maxAmp();

    startAmplificationParameterUpdate(_e, endValue, endTime);

    env e_;
    require e_.block.timestamp > _e.block.timestamp + (10000 * DAY()); // arbitrarily use 10000 days to represent a very long time
    bool isStillUpdating;
    _, isStillUpdating = _getAmplificationParameter(e_);
    assert !isStillUpdating, "system still updating";
}

/// @title: noDoubleUpdate
/// @notice: You must not be able to change the amplification factor if it is currently in the process of updating.
/// @dev: passes
rule noDoubleUpdate() {
    ampSetup();

    env e;
    uint256 startValue; bool isUpdating;
    startValue, isUpdating = _getAmplificationParameter(e);
    require isUpdating;

    uint256 endValue; uint256 endTime;
    startAmplificationParameterUpdate@withrevert(e, endValue, endTime);
    
    assert lastReverted;
}

/// @title: ampStoreAndReturn
/// @notice: Storing a value with _setAmplificationData must always return the set value through getAmplificationFactor.
rule ampStoreAndReturn() {
    ampSetup();

    uint256 startValue;
    uint256 endValue;
    uint256 startTime;
    uint256 endTime;
    require endTime > startTime;

    _setAmplificationData(startValue, endValue, startTime, endTime);

    env e;
    require e.block.timestamp > endTime;

    uint256 trueEndValue = getAmplificationFactor(e);
    
    assert trueEndValue == endValue;
}

// helper rule to test that starting an amp update will then later give you the set value
rule startUpdateSetsValue() {
    ampSetup();
    env e;

    uint256 startValue; bool isUpdating;
    startValue, isUpdating = _getAmplificationParameter(e);
    require !isUpdating;

    uint256 endValue; uint256 endTime;
    require endTime > e.block.timestamp + _MIN_UPDATE_TIME();
    startAmplificationParameterUpdate(e, endValue, endTime);

    env e_;
    require e_.block.timestamp > endTime;
    uint256 trueEndValue; bool isStillUpdating; 
    trueEndValue, isStillUpdating = _getAmplificationParameter(e_);

    assert !isStillUpdating, "still updating";
    assert trueEndValue == endValue * _AMP_PRECISION(), "wrong value";
}


// deprecated
    // _calcOutGivenIn(uint256 amplificationParameter, uint256[] balances,
    //     uint256 tokenIndexIn,
    //     uint256 tokenIndexOut,
    //     uint256 tokenAmountIn,
    //     uint256 invariant) returns (uint256) 
    //     => ghost_calcOutGivenIn(amplificationParameter, balances, tokenIndexIn, tokenIndexOut, tokenAmountIn, invariant);
	// stable pool


        // _calcTokenInGivenExactBptOut(
    //     uint256 amp,
    //     uint256[] balances,
    //     uint256 tokenIndex,
    //     uint256 bptAmountOut,
    //     uint256 bptTotalSupply,
    //     uint256 swapFeePercentage) returns (uint256)
    //     => ghost_calcTokenInGivenExactBptOut(amp, balances, tokenIndex, bptAmountOut, bptTotalSupply, swapFeePercentage);

        // mul(uint256 x, uint256 y) => ghost_multiplication(x, y);
    // mulUp(uint256 x, uint256 y) => ghost_multiplication_round(x, y);
    // mulDown(uint256 x, uint256 y) => ghost_multiplication_round(x, y);
    // div(uint256 x, uint256 y) => ghost_division(x, y);
    // divUp(uint256 x, uint256 y) => ghost_division_round(x, y);
    // divDown(uint256 x, uint256 y) => ghost_division_round(x, y);

    // function setup(env e) { 
//     require _token0<_token1 && _token1<_token2 && _token2<_token3 && _token3<_token4 && _token4<_token5;
//     require currentContract == getToken(getBptIndex());
//     require e.msg.sender < _token0;
//     require getTotalTokens()>2 && getTotalTokens()<7;
//     require getBptIndex() < getTotalTokens();
//     requireOrder(e.msg.sender);
// }