import "../helpers/erc20.spec"

using DummyERC20A as _token0
using DummyERC20B as _token1
using DummyERC20C as _token2
using DummyERC20D as _token3
using DummyERC20E as _token4

////////////////////////////////////////////////////////////////////////////
//                      Methods                                           //
////////////////////////////////////////////////////////////////////////////

methods {
    totalTokensBalance() returns (uint256) envfree
    inRecoveryMode() returns (bool) envfree


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
    //_getRate(uint256[],uint256,uint256) returns (uint256) => NONDET

    // _calcOutGivenIn(uint256 amplificationParameter, uint256[] balances,
    //     uint256 tokenIndexIn,
    //     uint256 tokenIndexOut,
    //     uint256 tokenAmountIn,
    //     uint256 invariant) returns (uint256) 
    //     => ghost_calcOutGivenIn(amplificationParameter, balances, tokenIndexIn, tokenIndexOut, tokenAmountIn, invariant);
	// stable pool
	// _getAmplificationParameter() returns (uint256,bool) => NONDET

    // _calcTokenInGivenExactBptOut(
    //     uint256 amp,
    //     uint256[] balances,
    //     uint256 tokenIndex,
    //     uint256 bptAmountOut,
    //     uint256 bptTotalSupply,
    //     uint256 swapFeePercentage) returns (uint256)
    //     => ghost_calcTokenInGivenExactBptOut(amp, balances, tokenIndex, bptAmountOut, bptTotalSupply, swapFeePercentage);

    //// @dev vault 
    getPoolTokens(bytes32) returns (address[], uint256[]) => NONDET
    getPoolTokenInfo(bytes32,address) returns (uint256,uint256,uint256,address) => NONDET
    getVault() returns address envfree;

    //// @dev authorizor functions
    getAuthorizor() returns address => DISPATCHER(true)
    _getAuthorizor() returns address => DISPATCHER(true)
    _canPerform(bytes32, address) returns (bool) => NONDET
    canPerform(bytes32, address, address) returns (bool) => NONDET

    //// @dev harness functions
    setRecoveryMode(bool)

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

/// Add the following assumptions:
///  - addresses `currentContract`, `token0`, ..., `token4` are distinct and ordered
///  - `e.msg.sender` is distinct from `currentContract` and `token0` ... `token4`
///  - there are at least 2 tokens and at most 5
function setup(env e) { 
    require _token0<_token1 && _token1<_token2 && _token2<_token3 && _token3<_token4;
    require currentContract < _token0;
    require e.msg.sender < currentContract;
    require getTotalTokens()>1 && getTotalTokens()<6;
}

////////////////////////////////////////////////////////////////////////////
//                    Ghosts, hooks and definitions                       //
////////////////////////////////////////////////////////////////////////////

/// A ghost tracking the sum of all BPT user balances in the pool
///
/// @dev we assume sum of all balances initially equals 0
ghost sum_all_users_BPT() returns uint256 {
    init_state axiom sum_all_users_BPT() == 0;
}

/// @dev keep `sum_all_users_BPT` up to date with the `_balances` mapping
hook Sstore _balances[KEY address user] uint256 balance (uint256 old_balance) STORAGE {
  havoc sum_all_users_BPT assuming sum_all_users_BPT@new() == sum_all_users_BPT@old() + balance - old_balance;
}

////////////////////////////////////////////////////////////////////////////
//// ###                      Invariants                                  //
////////////////////////////////////////////////////////////////////////////

/// @title Can't burn all BPT
/// @notice Contract must not allow all BPT to be burned.
invariant cantBurnAll()
    totalSupply() > 0 

/// `totalSupply` nonzero after `onJoinPool` is called
rule nonzeroSupply(method f) filtered {
    f -> f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector
} {
    //require !inRecoveryMode();
    
    env e1;
    bytes32 poolId; address sender; address recipient; uint256[] balances; 
    uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
    onJoinPool(e1, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData);
    assert totalSupply() > 0, "totalSupply must be greater than 0 after onJoinPool is called";

    env e2; calldataarg args2; method g;
    g(e2, args2); // user B had totalSupply tokens and exits
    assert totalSupply() > 0, "totalSupply must be greater than 0 after an arbitrary function call if the pool has been initialized";
}

/// `totalSupply` can only become non-zero if `onJoinPool` is called without reverting.
rule onlyOnJoinPoolCanInitialize(method f) {
    env e; calldataarg args;
    require totalSupply() == 0;
    f(e, args);
    assert totalSupply() > 0 => f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector, "onJoinPool must be the only function that can initialize a pool";
}

/// One user must not own the whole BPT supply.
invariant noMonopoly(address user, env e)
    totalSupply() > balanceOf(e, user)
    {preserved { require e.msg.sender != 0; }}

/// Reimplements [`noMonopoly`](#noMonopoly) as a rule
/// @dev TODO: how/why is this different from `noMonopoly`?
rule noMonopolyRule(method f, method g, env e1, env e2, address user) filtered {
    f -> f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector
} {
    require !inRecoveryMode();
    require !inRecoveryMode();
    
    calldataarg args1;
    f(e1, args1); // user A joins with x tokens
    assert totalSupply() > balanceOf(user), "totalSupply must be greater than 0 after onJoinPool is called";
}

/// Sum of all users' BPT balance must be less than or equal to BPT's `totalSupply`
invariant solvency()
    totalSupply() >= sum_all_users_BPT()


////////////////////////////////////////////////////////////////////////////
//                               Rule                                     //
////////////////////////////////////////////////////////////////////////////

rule NoFreeBPT(uint256 num, method f) {
    env e;
    setup(e);
	calldataarg args;

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

	f(e,args);

    uint256 totalBpt_ = totalSupply();
    uint256 totalTokens_ = totalTokensBalance();

    assert totalBpt_>_totalBpt => totalTokens_>_totalTokens;
    assert totalBpt_<_totalBpt => totalTokens_<_totalTokens;
}

rule NoFreeBPTPerAccount(uint256 num, method f) filtered { f ->
    f.selector != transfer(address,uint256).selector 
    && f.selector != transferFrom(address,address,uint256).selector 
} {
    env e;
    setup(e);
	calldataarg args;

    require totalSupply() > 0;

    address u;
    require u == e.msg.sender;
    uint256 _bptPerUser = balanceOf(u);
    uint256 _totalTokensPerUser = _token0.balanceOf(u) + _token1.balanceOf(u) + _token2.balanceOf(u) + _token3.balanceOf(u) + _token4.balanceOf(u);

	f(e,args);

    uint256 bptPerUser_ = balanceOf(u);
    uint256 totalTokensPerUser_ = _token0.balanceOf(u) + _token1.balanceOf(u) + _token2.balanceOf(u) + _token3.balanceOf(u) + _token4.balanceOf(u);

    assert bptPerUser_>_bptPerUser => _totalTokensPerUser>totalTokensPerUser_;
    assert bptPerUser_<_bptPerUser => _totalTokensPerUser<totalTokensPerUser_;
}


/// @dev TODO: there is an unexplained comment `onSwap((uint8,address,address,uint256,bytes32,uint256,address,address,bytes),uint256[],uint256,uint256)`
/// @dev TODO: there is an unexplained comment `onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes)`
rule sanity(method f) 
{
	env e;
	calldataarg args;
    require !inRecoveryMode();
	f(e,args);
	assert false;
}

rule sanity1(method f) 
{
	env e;
	calldataarg args;
    require inRecoveryMode();
	f(e,args);
	assert false;
}

/// Contract must not allow any user to mint BPT for free
rule noFreeMinting(method f) {
    uint256 totalSupplyBefore = totalSupply();
    // define free?
    uint256 totalSupplyAfter = totalSupply();
    assert totalSupplyAfter == totalSupplyBefore;
}

/// Given a value for `_calculateBPT`, calling `x` should result in user's
/// balance increasing by that value
rule calculateBPTAccuracy(address user) {
    assert false;
}

/// A BPT balance increase must be correlated with a token balance increase in
/// the vault
rule balanceIncreaseCorrelation(env e, calldataarg args, method f) {
    uint256 BPTBalanceBefore = balanceOf(e.msg.sender);
    //uint256 tokenBalanceBefore = vault.balanceOf;
    assert false;
}

////////////////////////////////////////////////////////////////////////////
//                            Helper Functions                            //
////////////////////////////////////////////////////////////////////////////

// TODO: Any additional helper functions



// Amplification factor

/// returns value encoded in solidity for 1 day
definition DAY() returns uint256 = 1531409238;


/// After starting an amplification factor increase and calling an artbirary
/// function, for some `t` later than initial increase, the amplification
/// factor must be less than value set
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

/// The amplification parameter can't change within two days of the the
/// `startAmplificationParameterUpdate`
///
/// @formula
///    {
///       startValue == amplificationParameter,
///       !isUpdating
///    }
///    startAmplificationParameterUpdate(...);
///    wait two days;
///    {
///       amplificationParameter == startValue
///    }
///
/// @dev start the amplification factor changing. Wait 2 days. Check the value
/// at that timestamp, and then assert the value doesn't change after
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

/// The amplification factor may not increase by more than a factor of two in a given day
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

//// # Recovery and Paused Modes

/// When in recovery mode the following operation must not revert onExitPool,
/// but only when called by the Vault, and only when userData corresponds to a
/// correct recovery mode call (that is, it is the abi encoding of the recovery
/// exit enum and a bpt amount), and sender has sufficient bpt
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

// /// None of the complex math functions will be called on recoveryMode
// rule recoveryModeSimpleMath(method f) {
//     env e; calldataarg args;
//     require inRecoveryMode();
//     f@withrevert(e, args);
//     assert (some check for math) => lastReverted, "no revert on math function"
// }


/// Only governance can bring the contract into recovery mode
rule recoveryModeGovernanceOnly(method f) {
    env e; calldataarg args;
    bool recoveryMode_ = inRecoveryMode();
    f(e, args);
    bool _recoveryMode = inRecoveryMode();
    assert e.msg.sender != getOwner(e) => recoveryMode_ == _recoveryMode, "non owner changed recovery mode with public function";
}

 
//// # Paused Mode

/// All basic operations must revert while in a paused state
rule basicOperationsRevertOnPause(method f) filtered {f -> !f.isView }
{
    env e; calldataarg args;
    require !inRecoveryMode(); // we will test this case independently
    bool paused; uint256 pauseWindowEndTime; uint256 bufferPeriodEndTime;
    paused, pauseWindowEndTime, bufferPeriodEndTime = getPausedState(e);
    f@withrevert(e, args);
    assert paused => lastReverted, "basic operations succeeded on pause";
}

/// If a function sets the contract into pause mode, it must only be during the
/// pauseWindow
///
/// @dev passing
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

/// After the buffer window finishes, the contract may not enter the paused state
/// @dev passes
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
 
//// # Pause + recovery mode
////
//// The only allowed operation when the pool is both paused and in recovery
//// mode is `withdraw`, and `withdraw` should never revert in this mode.

/// @title Withdraw doesn't revert when in paused recovery mode
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

/// @title Non-withdraw functions always revert when in paused recovery mode
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

