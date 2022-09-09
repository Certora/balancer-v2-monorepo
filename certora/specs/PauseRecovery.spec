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
    //// @dev envfree functions
    totalTokensBalance() returns (uint256) envfree
    totalTokensBalanceUser(address) returns (uint256) envfree
    totalFees() returns (uint256) envfree
    inRecoveryMode() returns (bool) envfree
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
 
// Recovery and Paused Modes
/// @title rule: noRevertOnRecoveryMode
/// @notice: When in recovery mode the following operation must not revert
/// onExitPool, but only when called by the Vault, and only when userData corresponds to a correct recovery mode call 
/// (that is, it is the abi encoding of the recovery exit enum and a bpt amount), and sender has sufficient bpt
rule exitNonRevertingOnRecoveryMode(method f) {
    env e; calldataarg args;
    require e.msg.sender == getVault();
    storage init = lastStorage;
    bytes32 poolId; address sender; address recipient; uint256[] balances;
    uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
    onExitPool@withrevert(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData);
    require !lastReverted; // only cases where exit pool does not revert

    setRecoveryMode(true) at init;
    // call exit with the proper variables. Need to use either the vault, or harnessing to directly call it

    // setup(e); // not sure we need this

    onExitPool@withrevert(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData); // Harness's onExitPool

    assert !lastReverted, "recovery mode must not fail";
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

/// @rule: recoveryModeSimpleMath
/// @description: none of the complex math functions will be called on recoveryMode
rule recoveryModeSimpleMath(method f) {
    env e; calldataarg args;
    require inRecoveryMode();
    require !beenCalled();
    f@withrevert(e, args);
    assert beenCalled() => lastReverted, "math function didn't revert";
}