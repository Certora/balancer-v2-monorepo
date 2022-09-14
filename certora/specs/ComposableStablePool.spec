// import "../helpers/erc20.spec"

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
    totalTokensBalance(address u) returns (uint256) envfree
    inRecoveryMode() returns (bool) envfree
    _getTotalTokens() envfree
    requireOrder(address) envfree
    totalSupply() envfree
    balanceOf(address) returns (uint256) envfree
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

    mul(uint256 x, uint256 y) => ghost_multiplication(x, y);
    mulUp(uint256 x, uint256 y) => ghost_multiplication_round(x, y);
    mulDown(uint256 x, uint256 y) => ghost_multiplication_round(x, y);
    div(uint256 x, uint256 y) => ghost_division(x, y);
    divUp(uint256 x, uint256 y) => ghost_division_round(x, y);
    divDown(uint256 x, uint256 y) => ghost_division_round(x, y);

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
rule onlyOnJoinPoolCanAndMustInitialize(method f) {
    env e; calldataarg args; address zero;
    require totalSupply() == 0;
    require zero == 0;
    
    f(e, args);
    
    assert totalSupply() > 0  <=> f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector, "onJoinPool must be the only function that can initialize a pool and must initialize if called";
    assert f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector => balanceOf(zero) > 0, "zero address must be minted some tokens on initialization";
}

// @title The zero address's BPT balance can never go from non-zero to zero.
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
    
    setup();

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

    address u; env e;
    joinExit(e, f, u);

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
    // require getTotalTokens()>2 && getTotalTokens()<7;
    // require getBptIndex() < getTotalTokens();
    requireOrder(e.msg.sender);
}

function setup() { 
    require _token0<_token1 && _token1<_token2 && _token2<_token3 && _token3<_token4;
    require getTotalTokens()>1 && getTotalTokens()<6;
}

function joinExit(env e, method f, address user) {
    bytes32 poolId; address sender; address recipient; uint256[] balances; 
    uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;

    if f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        require sender != currentContract; // times out if I remove this 
        onJoinPool(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData);
    } else if f.selector == onExitPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        require sender == user;
        require recipient == user;
        require totalSupply() > 0;
        require e.msg.sender != currentContract;
        require !inRecoveryMode();
        onExitPool(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData);
    } else {
        calldataarg args;
        f(e, args);
    }
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



// Amplification factor

// returns value encoded in solidity for 1 day
definition DAY() returns uint256 = 1531409238;


/// @rule amplfiicationFactorFollowsEndTime
/// @description: After starting an amplification factor increase and calling an artbirary function, for some e later than initial increase
/// amplification factor must be less than value set
rule amplificationFactorFollowsEndTime(method f) {
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

/// @rule: amplificationFactorTwoDayWait
/// @description: start the amplification factor changing. Wait 2 days. Check the value at that timestamp, and then assert the value doesn't change after
rule amplificationFactorTwoDayWait(method f) {
    env e; 
    uint256 endValue; uint256 endTime;
    uint256 startValue; bool isUpdating;
    startValue, isUpdating = _getAmplificationParameter(e);
    startAmplificationParameterUpdate(e, endValue, endTime);

    env e_f; calldataarg args;
    f(e_f, args);

    env e_2days;
    require e_2days.block.timestamp == e.block.timestamp + (2 * DAY());
    uint256 actualEndValue;
    actualEndValue, isUpdating = _getAmplificationParameter(e_2days);

    env e_post;
    require e_post.block.timestamp > e_2days.block.timestamp;
    uint256 endValuePost;
    endValuePost, isUpdating = _getAmplificationParameter(e_post);
    assert endValuePost == actualEndValue, "amplfication factor still changing after 2 days";
}

/// @rule: amplificationFactorNoMoreThanDouble
/// @descrption: the amplification factor may not increase by more than a factor of two in a given day
rule amplificationFactorNoMoreThanDouble(method f) {
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

// Recovery and Paused Modes
/// @title rule: noRevertOnRecoveryMode
/// @notice: When in recovery mode the following operation must not revert
/// onExitPool, but only when called by the Vault, and only when userData corresponds to a correct recovery mode call 
/// (that is, it is the abi encoding of the recovery exit enum and a bpt amount), and sender has sufficient bpt
rule exitNonRevertingOnRecoveryMode(method f) {
    env e; calldataarg args;
    require e.msg.sender == getVault();
    require inRecoveryMode();
    f(e, args); // arbitrary f in case there is frontrunning
    require inRecoveryMode(); // needs to stay in recovery mode
    // call exit with the proper variables. Need to use either the vault, or harnessing to directly call it
    bytes32 poolId; address sender; address recipient; uint256[] balances; 
    uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
    onExitPool@withrevert(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData); // Harness's onExitPool

    assert !lastReverted, "recovery mode must not fail";
}

/// @rule: recoveryModeSimpleMath
/// @description: none of the complex math functions will be called on recoveryMode
// rule recoveryModeSimpleMath(method f) {
//     env e; calldataarg args;
//     require inRecoveryMode();
//     f@withrevert(e, args);
//     assert (some check for math) => lastReverted, "no revert on math function"
// }


/// @rule: recoveryModeGovernanceOnly
/// @description: Only governance can bring the contract into recovery mode
rule recoveryModeGovernanceOnly(method f) {
    env e; calldataarg args;
    bool recoveryMode_ = inRecoveryMode();
    f(e, args);
    bool _recoveryMode = inRecoveryMode();
    assert e.msg.sender != getOwner(e) => recoveryMode_ == _recoveryMode, "non owner changed recovery mode with public function";
}

 
// Paused Mode:

/// @rule: basicOperationsRevertOnPause
/// @description: All basic operations must revert while in a paused state
rule basicOperationsRevertOnPause(method f) filtered {f -> !f.isView }
{
    env e; calldataarg args;
    require !inRecoveryMode(); // we will test this case independently
    bool paused; uint256 pauseWindowEndTime; uint256 bufferPeriodEndTime;
    paused, pauseWindowEndTime, bufferPeriodEndTime = getPausedState(e);
    f@withrevert(e, args);
    assert paused => lastReverted, "basic operations succeeded on pause";
}

/// @title rule: pauseStartOnlyPauseWindow
/// @notice If a function sets the contract into pause mode, it must only be during the pauseWindow
/// @notice passing 
rule pauseStartOnlyPauseWindow(method f) filtered {f -> !f.isView} {
    env e; calldataarg args;
    bool paused_; uint256 pauseWindowEndTime; uint256 bufferPeriodEndTime;
    paused_, pauseWindowEndTime, bufferPeriodEndTime = getPausedState(e);
    require !paused_; // start in an unpaused state

    // call any function
    f(e, args);

    bool _paused; uint256 dc1; uint256 dc2;
    _paused, dc1, dc2 = getPausedState(e);
    // if we are now paused, then the current time must be within the pauseWindow
    assert _paused => e.block.timestamp <= pauseWindowEndTime, "paused after end window";
}

/// @title: rule: unpausedAfterBuffer
/// @notice: After the buffer window finishes, the contract may not enter the paused state
/// @notice: passes
rule unpausedAfterBuffer(method f) filtered {f -> !f.isView} {
    env e; calldataarg args;
    // call some arbitrary function
    f(e, args);

    env e2;
    require e2.block.timestamp >= e.block.timestamp; // shouldn't change the results, but we only care about checking pause after the function call
    bool paused; uint256 pauseWindowEndTime; uint256 bufferPeriodEndTime;
    paused, pauseWindowEndTime, bufferPeriodEndTime = getPausedState(e2);
    require bufferPeriodEndTime >= pauseWindowEndTime; 
    assert e2.block.timestamp > bufferPeriodEndTime => !paused, "contract remained pauased after buffer period";
}
 
// Pause + recovery mode

// People can only withdraw 

/// @title rule: prWithdrawOnly
/// @notice if both paused and recovery mode is active, withdraw must never revert
rule prWithdrawNeverReverts(method f) {
    env e; calldataarg args;
    require e.msg.sender == getVault();
    require inRecoveryMode();
    f(e, args); // arbitrary f in case there is frontrunning
    require inRecoveryMode(); // needs to stay in recovery mode
    // call exit with the proper variables. Need to use either the vault, or harnessing to directly call it
    bool paused_; uint256 pauseWindowEndTime; uint256 bufferPeriodEndTime;
    paused_, pauseWindowEndTime, bufferPeriodEndTime = getPausedState(e);

    bytes32 poolId; address sender; address recipient; uint256[] balances; 
    uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
    onExitPool@withrevert(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData); // Harness's onExitPool

    assert !lastReverted, "recovery mode must not fail";
}

rule prOtherFunctionsAlwaysRevert(method f) filtered { 
    f -> (f.selector != onExitPool(bytes32, address, address, uint256[], uint256, uint256, bytes).selector && !f.isView) } 
{
    env e; calldataarg args;

    require inRecoveryMode();
    bool paused; uint256 pauseWindowEndTime; uint256 bufferPeriodEndTime;
    paused, pauseWindowEndTime, bufferPeriodEndTime = getPausedState(e);
    require paused;
    f@withrevert(e, args);

    assert lastReverted, "function did not revert";
}