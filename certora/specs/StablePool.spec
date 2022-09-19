
import "../helpers/erc20.spec"

using DummyERC20A as _token0
using DummyERC20B as _token1
using DummyERC20C as _token2
using DummyERC20D as _token3
using DummyERC20E as _token4

/*
need to check:
    which assumptions are needed for no free mintint to pass
    which assumptions are needed for no unpaid burning to pass
*/


////////////////////////////////////////////////////////////////////////////
//                      Methods                                           //
////////////////////////////////////////////////////////////////////////////

methods {
    //// @dev envfree functions
    totalTokensBalance() returns (uint256) envfree
    totalTokensBalanceUser(address) returns (uint256) envfree
    totalFees() returns (uint256) envfree
    inRecoveryMode() returns (bool) envfree

    _MIN_UPDATE_TIME() returns (uint256) envfree
    _MAX_AMP_UPDATE_DAILY_RATE() returns (uint256) envfree

    // stable pool
	_getAmplificationParameter() returns (uint256,bool)
    getJoinKind(bytes) returns (uint8) envfree

    //// @dev functions called by stable math functions to remove dynamic array from funtion signature
    getTokenBal(uint256 balance1, uint256 balance2, uint256 newInvariant, uint256 index) returns(uint256) => newGetTokenBalance(balance1, balance2, newInvariant, index)
    calculateInvariant(uint256 balance1, uint256 balance2) returns (uint256) => newCalcInvar(balance1,balance2)

    //// @dev decoding function called internally by one of the join kinds
    //exactTokensInForBptOut(bytes) returns (uint256[], uint256) => NONDET
	
    //// @dev stable math
    //_calculateInvariant(uint256 ampParam, uint256[] balances) returns (uint256) => NONDET
    // _calcOutGivenIn(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) => NONDET
    // _calcInGivenOut(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) => NONDET
    // _calcBptOutGivenExactTokensIn(uint256,uint256[],uint256[],uint256,uint256) returns (uint256) => NONDET
    //_calcTokenInGivenExactBptOut(uint256,uint256[],uint256,uint256,uint256,uint256)returns (uint256) => ALWAYS(1)
    // _calcBptInGivenExactTokensOut(uint256,uint256[],uint256[],uint256,uint256) returns (uint256) => NONDET
    // _calcTokenOutGivenExactBptIn(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) => NONDET
	// _calcTokensOutGivenExactBptIn(uint256[],uint256,uint256) returns (uint256[]) => NONDET
    // _calcDueTokenProtocolSwapFeeAmount(uint256 ,uint256[],uint256,uint256,uint256) returns (uint256) => NONDET
    //_getTokenBalanceGivenInvariantAndAllOtherBalances(uint256,uint256[],uint256,uint256) returns (uint256) => NONDET
    // _getRate(uint256[],uint256,uint256) returns (uint256) => NONDET
    
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

    getTotalTokens() returns (uint256) envfree

}

function setup(env e) { 
    require _token0<_token1 && _token1<_token2 && _token2<_token3 && _token3<_token4;
    require currentContract < _token0;
    require e.msg.sender < currentContract;
    require getTotalTokens()>1 && getTotalTokens()<6;
}

function setup1() { 
    require _token0<_token1 && _token1<_token2 && _token2<_token3 && _token3<_token4;
    require getTotalTokens()>1 && getTotalTokens()<6;
}

// invariant must be greater than the sum of pool's token balances and less than the product 
function newCalcInvar(uint256 balance1, uint256 balance2) returns uint256 {
    uint256 invar;
    require invar >= balance1 + balance2;
    require invar <= balance1 * balance2;
    require determineInvariant[balance1][balance2] == invar;
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

////////////////////////////////////////////////////////////////////////////
//                    Ghosts, hooks and definitions                       //
////////////////////////////////////////////////////////////////////////////

/// A ghost tracking values for an invariant given two token balances;
///
/// @dev we assume only 2 tokens in a pool and that a bounded arbitrary value for the invariant
ghost mapping(uint256 => mapping(uint256 => uint256)) determineInvariant;

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
//                            Invariants                                  //
////////////////////////////////////////////////////////////////////////////

/// @title Sum of all users' BPT balance must be less than or equal to BPT's `totalSupply`
invariant solvency()
    totalSupply() >= sum_all_users_BPT()

////////////////////////////////////////////////////////////////////////////
//                               Rule                                     //
////////////////////////////////////////////////////////////////////////////

// balances == 0 && totalSupply == 0 => no mint
// everything zero or all nonzero
// assumption about invariant
// assumption 2: balances increase if invariant increased

// totalSupply > 0, noRecovery sane
// _joinExactTokensInForBPTOut: https://vaas-stg.certora.com/output/93493/e30c999191a5376ce1d4/?anonymousKey=e3118f4c4be777bdf4dae67da3d961e23b49e20b
// _joinTokenInForExactBPTOut: https://vaas-stg.certora.com/output/93493/c25ae22b90a487c8ed3c/?anonymousKey=e528798fd99a3a481ec6df1d5a53c7401a7514f0

// totalSupply == 0, noRecovery, sane
// _joinExactTokensInForBPTOut: https://vaas-stg.certora.com/output/93493/6feaeddf8f79219dd9d0/?anonymousKey=d373e7198e408779d3b5d58c60f977009e2c6c2e
// _joinTokenInForExactBPTOut: https://vaas-stg.certora.com/output/93493/41515ce11a120f23cc68/?anonymousKey=471d5eb61d6f67f3261ba4b6a44975b23e290ad5

// totalSupply > 0, Recovery, sane
// _joinExactTokensInForBPTOut: https://vaas-stg.certora.com/output/93493/e1a9bb7822505b64d11b/?anonymousKey=994e6cb322a0d1f0fa4270c4027a13ee585c4a75
// _joinTokenInForExactBPTOut: https://vaas-stg.certora.com/output/93493/568f236669cb8e863831/?anonymousKey=9b9bda670b64e5b6e19f0175ebd3db0de6da5052

// totalSupply == 0, Recovery, sane
// _joinExactTokensInForBPTOut: https://vaas-stg.certora.com/output/93493/80fc853c0ff47c343d48/?anonymousKey=4abfb9806a151f68f7433a7f9bb718d9f0edecac
// _joinTokenInForExactBPTOut: https://vaas-stg.certora.com/output/93493/b5e2cd6a77a88c1099d7/?anonymousKey=9822a1adfb5e2eec4fed08a5ed6a320337e51c2d
rule noFreeMinting_exactTokens_noSupply_noRecovery(method f) {
    
    setup1();
    require totalSupply() == 0;
    require !inRecoveryMode();

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

    env e;

    if f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        bytes32 poolId; address sender; address recipient; uint256[] balances; 
        uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
        require sender != currentContract;
        require getJoinKind(bytes) == 1; // exact tokens
        onJoinPool(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData);
    } else {
        calldataarg args;
        f(e, args);
    }

    uint256 totalBpt_ = totalSupply();
    uint256 totalTokens_ = totalTokensBalance();

    assert totalBpt_>_totalBpt => totalTokens_>_totalTokens, "an increase in total BPT must lead to an increase in pool's total tokens";
}

rule noFreeMinting_exactTokens_noSupply_yesRecovery(method f) {
    
    setup1();
    require totalSupply() == 0;
    require inRecoveryMode();

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

    env e;

    if f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        bytes32 poolId; address sender; address recipient; uint256[] balances; 
        uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
        require sender != currentContract;
        require getJoinKind(bytes) == 1; // exact tokens
        onJoinPool(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData);
    } else {
        calldataarg args;
        f(e, args);
    }

    uint256 totalBpt_ = totalSupply();
    uint256 totalTokens_ = totalTokensBalance();

    assert totalBpt_>_totalBpt => totalTokens_>_totalTokens, "an increase in total BPT must lead to an increase in pool's total tokens";
}

rule noFreeMinting_exactTokens_yesSupply_noRecovery(method f) {
    
    setup1();
    require totalSupply() > 0; // cutting out big branch
    require !inRecoveryMode();

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

    env e;

    if f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        bytes32 poolId; address sender; address recipient; uint256[] balances; 
        uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
        require sender != currentContract;
        require getJoinKind(bytes) == 1; // exact tokens
        onJoinPool(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData);
    } else {
        calldataarg args;
        f(e, args);
    }

    uint256 totalBpt_ = totalSupply();
    uint256 totalTokens_ = totalTokensBalance();

    assert totalBpt_>_totalBpt => totalTokens_>_totalTokens, "an increase in total BPT must lead to an increase in pool's total tokens";
}

rule noFreeMinting_exactTokens_yesSupply_yesRecovery(method f) {
    
    setup1();
    require totalSupply() > 0; // cutting out big branch
    require inRecoveryMode();

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

    env e;

    if f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        bytes32 poolId; address sender; address recipient; uint256[] balances; 
        uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
        require sender != currentContract; // times out if I remove this 
        require getJoinKind(bytes) == 1; // exact tokens
        onJoinPool(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData);
    } else {
        calldataarg args;
        f(e, args);
    }

    uint256 totalBpt_ = totalSupply();
    uint256 totalTokens_ = totalTokensBalance();

    assert totalBpt_>_totalBpt => totalTokens_>_totalTokens, "an increase in total BPT must lead to an increase in pool's total tokens";
}

rule noFreeMinting_exactBpt_noSupply_noRecovery(method f) {
    
    setup1();
    require totalSupply() == 0;
    require !inRecoveryMode();

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

    env e;

    if f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        bytes32 poolId; address sender; address recipient; uint256[] balances; 
        uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
        require sender != currentContract;
        require getJoinKind(bytes) == 2; // exact bpt
        onJoinPool(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData);
    } else {
        calldataarg args;
        f(e, args);
    }

    uint256 totalBpt_ = totalSupply();
    uint256 totalTokens_ = totalTokensBalance();

    assert totalBpt_>_totalBpt => totalTokens_>_totalTokens, "an increase in total BPT must lead to an increase in pool's total tokens";
}

rule noFreeMinting_exactBpt_noSupply_yesRecovery(method f) {
    
    setup1();
    require totalSupply() == 0;
    require inRecoveryMode();

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

    env e;

    if f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        bytes32 poolId; address sender; address recipient; uint256[] balances; 
        uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
        require sender != currentContract;
        require getJoinKind(bytes) == 2; // exact bpt
        onJoinPool(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData);
    } else {
        calldataarg args;
        f(e, args);
    }

    uint256 totalBpt_ = totalSupply();
    uint256 totalTokens_ = totalTokensBalance();

    assert totalBpt_>_totalBpt => totalTokens_>_totalTokens, "an increase in total BPT must lead to an increase in pool's total tokens";
}

rule noFreeMinting_exactBpt_yesSupply_noRecovery(method f) {
    
    setup1();
    require totalSupply() > 0; // cutting out big branch
    require !inRecoveryMode();

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

    env e;

    if f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        bytes32 poolId; address sender; address recipient; uint256[] balances; 
        uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
        require sender != currentContract;
        require getJoinKind(bytes) == 2; // exact bpt
        onJoinPool(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData);
    } else {
        calldataarg args;
        f(e, args);
    }

    uint256 totalBpt_ = totalSupply();
    uint256 totalTokens_ = totalTokensBalance();

    assert totalBpt_>_totalBpt => totalTokens_>_totalTokens, "an increase in total BPT must lead to an increase in pool's total tokens";
}

rule noFreeMinting_exactBpt_yesSupply_yesRecovery(method f) {
    
    setup1();
    require totalSupply() > 0; // cutting out big branch
    require inRecoveryMode();

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

    env e;

    if f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        bytes32 poolId; address sender; address recipient; uint256[] balances; 
        uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
        require sender != currentContract; // times out if I remove this 
        require getJoinKind(bytes) == 2; // exact bpt
        onJoinPool(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData);
    } else {
        calldataarg args;
        f(e, args);
    }

    uint256 totalBpt_ = totalSupply();
    uint256 totalTokens_ = totalTokensBalance();

    assert totalBpt_>_totalBpt => totalTokens_>_totalTokens, "an increase in total BPT must lead to an increase in pool's total tokens";
}

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

////////////////////////////////////////////////////////////////////////////
//                            Helper Functions                            //
////////////////////////////////////////////////////////////////////////////

// TODO: Any additional helper functions



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
    getAmplificationFactor(e) <= maxAmp() * AMP_PRECISION() && getAmplificationFactor(e) >= minAmp() * AMP_PRECISION()
{ preserved {
    require !initialized() => getAmplificationFactor(e) == 0; // amplification factor is 0 before initialization
    require _MAX_AMP_UPDATE_DAILY_RATE() == 2;
    require _MIN_UPDATE_TIME() == DAY();
    require AMP_PRECISION() == 1000;
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

/// @rule: amplificationFactorTwoDayWait
/// @description: start the amplification factor changing. Wait 2 days. Check the value at that timestamp, and then assert the value doesn't change after
/// @notice: passes
rule amplificationFactorTwoDayWait(method f) {
    // require _MAX_AMP_UPDATE_DAILY_RATE() == 2;
    // require _MIN_UPDATE_TIME() == DAY();
    // require AMP_PRECISION() == 1000;

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

    setup(e);
    bytes32 poolId; address sender; address recipient; uint256[] balances;
    uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
    onExitPool@withrevert(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData); // Harness's onExitPool

    assert !lastReverted, "recovery mode must not fail";
}

 
// Paused Mode:

/// @rule: basicOperationsRevertOnPause
/// @description: All basic operations must revert while in a paused state
/// @notice: passes
rule basicOperationsRevertOnPause(method f) filtered {f -> ( 
        f.selector == onSwap((uint8,address,address,uint256,bytes32,uint256,address,address,bytes),uint256[],uint256,uint256).selector ||
        f.selector == setSwapFeePercentage(uint256).selector ||
        f.selector == setAssetManagerPoolConfig(address,bytes).selector ||
        f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256, bytes).selector || 
        f.selector == onSwap(uint8,uint256,bytes32,uint256,uint256).selector || 
        f.selector == onSwap((uint8,address,address,uint256,bytes32,uint256,address,address,bytes),uint256,uint256).selector ||
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
    require inRecoveryMode(); // needs to stay in recovery mode
    // call exit with the proper variables. Need to use either the vault, or harnessing to directly call it
    bool paused_; uint256 pauseWindowEndTime; uint256 bufferPeriodEndTime;
    paused_, pauseWindowEndTime, bufferPeriodEndTime = getPausedState(e);

    bytes32 poolId; address sender; address recipient; uint256[] balances; 
    uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;

    require balances.length == getTotalTokens(); // correct number of tokens
    uint256 i;
    require i < balances.length && balances[i] > 0; // at least one token must have a nonzero value
    uint256 bptIn; uint256 tokenIndex;
    // tokenIndex, bptIn = exactTokensInForBptOut(userData);
    // uint256[] amountsOut; uint256 maxBptIn;
    // amountsOut, maxBptIn = bptInForExactTokensOut(userData);
    // require tokenIndex < getTotalTokens();

    onExitPool@withrevert(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData); // Harness's onExitPool

    assert !lastReverted, "recovery mode must not fail";
}

/// @title rule: prOtherFunctionsAlwaysRevert
/// @notice If both paused and recovery mode is active, the set functions must always revert
/// @notice: passes
rule prOtherFunctionsAlwaysRevert(method f) filtered {f -> ( 
        f.selector == onSwap((uint8,address,address,uint256,bytes32,uint256,address,address,bytes),uint256[],uint256,uint256).selector ||
        f.selector == setSwapFeePercentage(uint256).selector ||
        f.selector == setAssetManagerPoolConfig(address,bytes).selector ||
        f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256, bytes).selector || 
        f.selector == onSwap(uint8,uint256,bytes32,uint256,uint256).selector || 
        f.selector == onSwap((uint8,address,address,uint256,bytes32,uint256,address,address,bytes),uint256,uint256).selector) }
{
    env e; calldataarg args;

    require inRecoveryMode();
    bool paused; uint256 pauseWindowEndTime; uint256 bufferPeriodEndTime;
    paused, pauseWindowEndTime, bufferPeriodEndTime = getPausedState(e);
    require paused;
    f@withrevert(e, args);

    assert lastReverted, "function did not revert";
}