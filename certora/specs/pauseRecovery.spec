import "../helpers/erc20.spec"

// using DummyERC20A as _token0
// using DummyERC20B as _token1
// using DummyERC20C as _token2
// using DummyERC20D as _token3
// using DummyERC20E as _token4

////////////////////////////////////////////////////////////////////////////
//                      Methods                                           //
////////////////////////////////////////////////////////////////////////////

methods {
    totalTokensBalance(address) returns (uint256) envfree
    inRecoveryMode() returns (bool) envfree
    _MIN_UPDATE_TIME() returns (uint256) envfree
    _MAX_AMP_UPDATE_DAILY_RATE() returns (uint256) envfree

    getFeeTypePercentage(uint256) returns (uint256) => NONDET
    // 0x1a7c3263 => NONDET
    registerTokens(bytes32, address[], address[]) => NONDET
    // 0x66a9c7d2 => NONDET
    registerPool(uint8) returns (bytes32) => NONDET
    // 0xabd90846 => NONDET
    getProtocolFeesCollector() returns (address) => NONDET
    // getRate() returns (uint256) => NONDET
    getRate() returns (uint256) envfree
    getActualSupply() returns (uint256) envfree
    
    _DELEGATE_OWNER() returns (address) envfree
    getActionId(uint32 selector) returns (bytes32) envfree
    _getProtocolPoolOwnershipPercentage(uint256[],uint256,uint256) returns (uint256,uint256)
	// stable math
    _calculateInvariant(uint256,uint256[]) returns (uint256) => NONDET

    getPoolId() returns(bytes32) envfree
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

	// stable pool
	_getAmplificationParameter() returns (uint256,bool) => NONDET

    // vault 
    // getPoolTokens(bytes32) returns (address[], uint256[]) => NONDET
    // getPoolTokenInfo(bytes32,address) returns (uint256,uint256,uint256,address) => NONDET
    getVault() returns (address) envfree
    // // authorizor functions
    // getAuthorizor() returns address => DISPATCHER(true)
    // _getAuthorizor() returns address => DISPATCHER(true)
    // _canPerform(bytes32, address) returns (bool) => NONDET
    canPerform(bytes32, address, address) returns (bool) => NONDET
    // // harness functions
    disableRecoveryMode() envfree
    // setRecoveryMode(bool) envfree
    minAmp() returns(uint256) envfree
    maxAmp() returns(uint256) envfree
    AMP_PRECISION() envfree
    mul(uint256, uint256) returns (uint256) => NONDET

    balanceOf(uint256) returns (uint256) envfree
    balanceOf(address,uint256) returns (uint256) envfree
    // _token0.balanceOf(address) returns(uint256) envfree
    // _token1.balanceOf(address) returns(uint256) envfree
    // _token2.balanceOf(address) returns(uint256) envfree
    // _token3.balanceOf(address) returns(uint256) envfree
    // _token4.balanceOf(address) returns(uint256) envfree

    // getToken0() returns(address) envfree
    // getToken1() returns(address) envfree
    // getToken2() returns(address) envfree
    // getToken3() returns(address) envfree
    // getToken4() returns(address) envfree
    getTotalTokens() returns (uint256) envfree
    onSwap((uint8,address,address,uint256,bytes32,uint256,address,address,bytes),uint256[],uint256,uint256) returns (uint256)
}

// function setup() { 
//     require _token0<_token1 && _token1<_token2 && _token2<_token3 && _token3<_token4;
//     require getTotalTokens()>1 && getTotalTokens()<6;
// }

////////////////////////////////////////////////////////////////////////////
//                    Ghosts, hooks and definitions                       //
////////////////////////////////////////////////////////////////////////////

// assume sum of all balances initially equals 0
// ghost sum_all_users_BPT() returns uint256 {
//     init_state axiom sum_all_users_BPT() == 0;
// }

// // everytime `balances` is called, update `sum_all_users_BPT` by adding the new value and subtracting the old value
// hook Sstore _balances[KEY address user] uint256 balance (uint256 old_balance) STORAGE {
//   havoc sum_all_users_BPT assuming sum_all_users_BPT@new() == sum_all_users_BPT@old() + balance - old_balance;
// }

////////////////////////////////////////////////////////////////////////////
//                            Invariants                                  //
////////////////////////////////////////////////////////////////////////////

// /// @invariant cantBurnAllBPT
// /// @description Contract must not allow all BPT to be burned.
// invariant cantBurnAll()
//     totalSupply() > 0 

// // totalSupply nonzero after onJoinPool is called
// rule nonzeroSupply(method f) filtered {
//     f -> f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector
// } {
//     //require !inRecoveryMode();
    
//     env e1;
//     bytes32 poolId; address sender; address recipient; uint256[] balances; 
//     uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
//     onJoinPool(e1, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData);
//     assert totalSupply() > 0, "totalSupply must be greater than 0 after onJoinPool is called";

//     env e2; calldataarg args2; method g;
//     g(e2, args2); // user B had totalSupply tokens and exits
//     assert totalSupply() > 0, "totalSupply must be greater than 0 after an arbitrary function call if the pool has been initialized";
// }
// /// @title totalSupply can only go 0 to non-zero if `onJoinPool` is called without reverting
// rule onlyOnJoinPoolCanInitialize(method f) {
//     env e; calldataarg args;
//     require totalSupply() == 0;
//     f(e, args);
//     assert totalSupply() > 0 => f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector, "onJoinPool must be the only function that can initialize a pool";
// }


// /// @invariant noMonopoly
// /// @description One user must not own the whole BPT supply.
// invariant noMonopoly(address user, env e)
//     totalSupply() > balanceOf(e, user)
//     {preserved { require e.msg.sender != 0; }}

// rule noMonopolyRule(method f, method g, env e1, env e2, address user) filtered {
//     f -> f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector
// } {
//     require !inRecoveryMode();
//     require !inRecoveryMode();
    
//     calldataarg args1;
//     f(e1, args1); // user A joins with x tokens
//     assert totalSupply() > balanceOf(user), "totalSupply must be greater than 0 after onJoinPool is called";
// }

// /// @invariant BPTSolvency
// /// @description Sum of all users' BPT balance must be less than or equal to BPT's `totalSupply`
// invariant solvency()
//     totalSupply() >= sum_all_users_BPT()


////////////////////////////////////////////////////////////////////////////
//                               Rule                                     //
////////////////////////////////////////////////////////////////////////////

// rule NoFreeBPT(uint256 num, method f)
// {
//     setup();
//     env e;
// 	calldataarg args;

//     uint256 _totalBpt = totalSupply();
//     uint256 _totalTokens = totalTokensBalance();

// 	f(e,args);

//     uint256 totalBpt_ = totalSupply();
//     uint256 totalTokens_ = totalTokensBalance();

//     assert totalBpt_>_totalBpt => totalTokens_>_totalTokens;
//     assert totalBpt_<_totalBpt => totalTokens_<_totalTokens;
// }

// rule NoFreeBPTPerAccount(uint256 num, method f)
// {
//     setup();
//     env e;
// 	calldataarg args;

//     address u;
//     require u == e.msg.sender;
//     uint256 _bptPerUser = balanceOf(u);
//     uint256 _totalTokensPerUser = _token0.balanceOf(u) + _token1.balanceOf(u) + _token2.balanceOf(u) + _token3.balanceOf(u) + _token4.balanceOf(u);

// 	f(e,args);

//     uint256 bptPerUser_ = balanceOf(u);
//     uint256 totalTokensPerUser_ = _token0.balanceOf(u) + _token1.balanceOf(u) + _token2.balanceOf(u) + _token3.balanceOf(u) + _token4.balanceOf(u);

//     assert bptPerUser_>_bptPerUser => _totalTokensPerUser>totalTokensPerUser_;
//     assert bptPerUser_<_bptPerUser => _totalTokensPerUser<totalTokensPerUser_;
// }


// onSwap((uint8,address,address,uint256,bytes32,uint256,address,address,bytes),uint256[],uint256,uint256)
// // onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes)
// rule sanity(method f) 
// {
// 	env e;
// 	calldataarg args;
//     require !inRecoveryMode();
// 	f(e,args);
// 	assert false;
// }

// rule sanity1(method f) 
// {
// 	env e;
// 	calldataarg args;
//     require inRecoveryMode();
// 	f(e,args);
// 	assert false;
// }

// /// @rule noFreeMinting
// /// @description Contract must not allow any user to mint BPT for free
// rule noFreeMinting(method f) {
//     uint256 totalSupplyBefore = totalSupply();
//     // define free?
//     uint256 totalSupplyAfter = totalSupply();
//     assert totalSupplyAfter == totalSupplyBefore;
// }

// /// @rule calculateBPTAccuracy
// /// @description Given a value for `_calculateBPT`, calling `x` should result in user's balance increasing by that value
// rule calculateBPTAccuracy(address user) {
//     assert false;
// }

// /// @rule balanceIncreaseCorrelation
// /// @description A BPT balance increase must be correlated with a token balance increase in the vault
// rule balanceIncreaseCorrelation(env e, calldataarg args, method f) {
//     uint256 BPTBalanceBefore = balanceOf(e.msg.sender);
//     //uint256 tokenBalanceBefore = vault.balanceOf;
//     assert false;
// }
    




// ////////////////////////////////////////////////////////////////////////////
// //                            Helper Functions                            //
// ////////////////////////////////////////////////////////////////////////////

// // TODO: Any additional helper functions



// Amplification factor

// returns value encoded in solidity for 1 day
definition DAY() returns uint256 = 1531409238;

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
    require AMP_PRECISION() == 1000;
} }

rule recoveryExitAll() {
    env e;
	calldataarg args;
    require inRecoveryMode();
    onExitPool(e, args);
    assert(balanceOf(0)==0 && balanceOf(1)==0 && balanceOf(2)==0);
}

/// @rule amplfiicationFactorFollowsEndTime
/// @description: After starting an amplification factor increase and calling an artbirary function, for some e later than initial increase
/// amplification factor must be less than value set
/// @notice: passes
// rule amplificationFactorFollowsEndTime(method f) {
//     require _MAX_AMP_UPDATE_DAILY_RATE() == 2;
//     require _MIN_UPDATE_TIME() == DAY();
//     _AMP_PRECISION();

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
// /// @notice: passes
// rule amplificationFactorTwoDayWait(method f) {
//     require _MAX_AMP_UPDATE_DAILY_RATE() == 2;
//     require _MIN_UPDATE_TIME() == DAY();
//     AMP_PRECISION();

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
// /// @notice: passes
// rule amplificationFactorNoMoreThanDouble(method f) {
//     require _MAX_AMP_UPDATE_DAILY_RATE() == 2;
//     require _MIN_UPDATE_TIME() == DAY();
//     AMP_PRECISION();

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

// /// @rule: amplificationFactorUpdatingOneDay
// /// @descrption: if the amplification factor starts updating, then it must continue so for one day
// /// @notice: passes
// rule amplificationFactorUpdatingOneDay(method f) {
//     require _MIN_UPDATE_TIME() == DAY();
//     require _MAX_AMP_UPDATE_DAILY_RATE() == 2;
//     _AMP_PRECISION();

//     env e_pre;
//     uint256 endValue; uint256 endTime;
    
//     // require endValue >= minAmp();
//     // require endValue <= maxAmp();

//     uint256 startValue; bool isUpdating;
//     startValue, isUpdating = _getAmplificationParameter(e_pre);
//     require endValue != startValue;
//     require !isUpdating; // can't already be updating
//     startAmplificationParameterUpdate(e_pre, endValue, endTime);

//     env e_post;
//     require (e_post.block.timestamp >= e_pre.block.timestamp) && (e_post.block.timestamp < e_pre.block.timestamp + DAY());
//     uint256 actualEndValue; bool isUpdating_;
//     actualEndValue, isUpdating_ = _getAmplificationParameter(e_post);
//     assert isUpdating_, "must still be updating";
// }

// Recovery and Paused Modes
/// @title rule: noRevertOnRecoveryMode
/// @notice: When in recovery mode the following operation must not revert
/// onExitPool, but only when called by the Vault, and only when userData corresponds to a correct recovery mode call 
/// (that is, it is the abi encoding of the recovery exit enum and a bpt amount), and sender has sufficient bpt
rule exitNonRevertingOnRecoveryMode(method f) {
    env e; calldataarg args;
    require e.msg.sender == getVault();
    // require inRecoveryMode(e);
    // f(e, args); // arbitrary f in case there is frontrunning
    require inRecoveryMode(); // needs to stay in recovery mode
    // call exit with the proper variables. Need to use either the vault, or harnessing to directly call it
    require e.msg.value == 0;
    // setup();
    bytes32 poolId; address sender; address recipient; uint256[] balances;
    uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
    onExitPool@withrevert(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData); // Harness's onExitPool

    assert !lastReverted, "recovery mode must not fail";
}


/// @rule: recoveryModeGovernanceOnly
/// @description: Only governance can bring the contract into recovery mode
// rule recoveryModeGovernanceOnly(method f) {
//     env e; calldataarg args;
//     bool recoveryMode_ = inRecoveryMode();
//     f(e, args);
//     bool _recoveryMode = inRecoveryMode();
//     if (f.selector != enableRecoveryMode().selector) {
//         assert recoveryMode_ == _recoveryMode;
//     } else {
//         assert getOwner(e) != _DELEGATE_OWNER() && _isOwnerOnlyAction(getActionId(f.selector)) && e.msg.sender == getOwner(e) 
//         => _recoveryMode == true, "non owner changed recovery mode with public function";
//         if (_isOwnerOnlyAction(getActionId(f.selector))) {
//             assert false;
//         } else {
//             assert true;
//         }       
//     }
// }

 
// Paused Mode:

/// @rule: basicOperationsRevertOnPause
/// @description: All basic operations must revert while in a paused state
/// @notice: passes
rule basicOperationsRevertOnPause(method f) filtered {f -> ( 
        f.selector == onSwap((uint8,address,address,uint256,bytes32,uint256,address,address,bytes),uint256[],uint256,uint256).selector ||
        f.selector == setSwapFeePercentage(uint256).selector ||
        f.selector == setAssetManagerPoolConfig(address,bytes).selector ||
        f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256, bytes).selector || 
        f.selector == onExitPool(bytes32,address,address,uint256[],uint256,uint256, bytes).selector) }
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
    // require inRecoveryMode(e);
    // f(e, args); // arbitrary f in case there is frontrunning
    
    // call exit with the proper variables. Need to use either the vault, or harnessing to directly call it
    bool paused_; uint256 pauseWindowEndTime; uint256 bufferPeriodEndTime;
    paused_, pauseWindowEndTime, bufferPeriodEndTime = getPausedState(e);

    bytes32 poolId; address sender; address recipient; uint256[] balances; 
    uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;

    require balances.length == 3;
    require balances.length == getTotalTokens(); // correct number of tokens
    uint256 i;
    require i < balances.length && balances[i] > 0; // at least one token must have a nonzero value
    uint256 bptIn; uint256 tokenIndex;
    // tokenIndex, bptIn = exactTokensInForBptOut(userData);
    // uint256[] amountsOut; uint256 maxBptIn;
    // amountsOut, maxBptIn = bptInForExactTokensOut(userData);
    // require tokenIndex < getTotalTokens();
    
    uint256 _balance0 = balanceOf(sender, 0);
    uint256 _balance1 = balanceOf(sender, 0);
    uint256 _balance2 = balanceOf(sender, 0);
    
    require totalSupply() == 0;
    require sender == recipient;
    onJoinPool(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData); // Harness's onJoinPool

    require inRecoveryMode(); // needs to stay in recovery mode
    onExitPool@withrevert(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData); // Harness's onExitPool

    uint256 balance0_ = balanceOf(sender, 0);
    uint256 balance1_ = balanceOf(sender, 0);
    uint256 balance2_ = balanceOf(sender, 0);

    assert !lastReverted, "recovery mode must not fail";
    assert _balance0 == balance0_;
    assert _balance0 == balance1_;
    assert _balance0 == balance2_;
}

// c) _getProtocolPoolOwnershipPercentage should always return 0 if recovery mode is enabled
rule ZeroOwnerPercentageInRecovery() {
    env e; 
    calldataarg args;
    require inRecoveryMode(); 
    uint256 feePercentage;
    uint256 totalGrowthInvariant;
    feePercentage, totalGrowthInvariant = _getProtocolPoolOwnershipPercentage(e, args);
    assert feePercentage==0;
}

// d) disabling recovery mode causes no change in the return value of getRate() or getActualSupply()
rule DisablingRMDoesNotChangeRateAndActualSupply() {
    uint _rate = getRate();
    uint _actualSupply = getActualSupply();

    disableRecoveryMode();

    uint rate_ = getRate();
    uint actualSupply_ = getActualSupply();

    assert _rate == rate_;
    assert _actualSupply == actualSupply_;
}

// e) _getProtocolPoolOwnershipPercentage should return 0 immediately after disabling recovery mode
rule ZeroOwnerPercentageAfterDisablingRecovery() {
    env e; 
    calldataarg args;
    require inRecoveryMode(); 
    disableRecoveryMode();
    uint256 feePercentage;
    uint256 totalGrowthInvariant;
    feePercentage, totalGrowthInvariant = _getProtocolPoolOwnershipPercentage(e, args);
    assert feePercentage==0;
}


/// @title rule: prOtherFunctionsAlwaysRevert
/// @notice If both paused and recovery mode is active, the set functions must always revert
/// @notice: passes
rule prOtherFunctionsAlwaysRevert(method f) filtered {f -> ( 
        f.selector == onSwap((uint8,address,address,uint256,bytes32,uint256,address,address,bytes),uint256[],uint256,uint256).selector ||
        f.selector == setSwapFeePercentage(uint256).selector ||
        f.selector == setAssetManagerPoolConfig(address,bytes).selector ||
        f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256, bytes).selector)}
{
    env e; calldataarg args;

    require inRecoveryMode();
    bool paused; uint256 pauseWindowEndTime; uint256 bufferPeriodEndTime;
    paused, pauseWindowEndTime, bufferPeriodEndTime = getPausedState(e);
    require paused;
    f@withrevert(e, args);

    assert lastReverted, "function did not revert";
}

// rule noFeeForRecoveryMode() {
//     env e;
// 	calldataarg args;
//     uint256 _counter = payProtocolFreeCounter();
//     require inRecoveryMode();
//     onExitPool(bytes32,address,address,uint256[],uint256,uint256,bytes)
//     uint256 counter_ = payProtocolFreeCounter();
// }