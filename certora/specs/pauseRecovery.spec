/***
### Assumptions and Simplifications
 #### TODO
    
#### Harnessing
 #### TODO
    
#### Munging
    
#### Definitions

*/

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

    _scalingFactors() returns (uint256[]) => CONSTANT
    getFeeTypePercentage(uint256) returns (uint256) => NONDET
    registerTokens(bytes32, address[], address[]) => NONDET
    registerPool(uint8) returns (bytes32) => NONDET
    getProtocolFeesCollector() returns (address) => NONDET
    getRate() returns (uint256) 
    getSupplyAndFeesData(uint256) returns (uint256) envfree
    getActualSupply() returns (uint256) envfree
    
    _DELEGATE_OWNER() returns (address) envfree
    getActionId(uint32 selector) returns (bytes32) envfree
    getProtocolPoolOwnershipPercentage(uint256[]) returns (uint256,uint256)

    getPoolId() returns(bytes32) envfree
    _getTokenBalanceGivenInvariantAndAllOtherBalances(uint256,uint256[],uint256,uint256) returns (uint256) => NONDET

	// stable pool
	_getAmplificationParameter() returns (uint256,bool) => CONSTANT

    // vault 
    getVault() returns (address) envfree
    canPerform(bytes32, address, address) returns (bool) => NONDET
    getBptIndex() envfree

    // harness functions
    disableRecoveryMode()
    // setRecoveryMode(bool) envfree
    minAmp() returns(uint256) envfree
    maxAmp() returns(uint256) envfree
    AMP_PRECISION() envfree
    // mul(uint256, uint256) returns (uint256) => NONDET
    mul(uint256, uint256) returns (uint256) => NONDET
    isRecoveryModeExitKind(bytes) returns (bool) envfree

    balanceOf(uint256) returns (uint256) envfree
    balanceOf(address,uint256) returns (uint256) envfree

    getTotalTokens() returns (uint256) envfree
    onSwap((uint8,address,address,uint256,bytes32,uint256,address,address,bytes),uint256[],uint256,uint256) returns (uint256)

    beenCalled() returns (bool) envfree // stableMath harness
} 

////////////////////////////////////////////////////////////////////////////
//                    Ghosts, hooks and definitions                       //
////////////////////////////////////////////////////////////////////////////

definition DAY() returns uint256 = 1531409238;

function getAmplificationFactor(env e) returns uint256 {
    uint256 param; bool updating;
    param, updating = _getAmplificationParameter(e);
    return param;
}

////////////////////////////////////////////////////////////////////////////
//                               Rule                                     //
////////////////////////////////////////////////////////////////////////////

rule recoveryExitAll() {
    env e;
	calldataarg args;
    require inRecoveryMode();
    onExitPool(e, args);
    assert(balanceOf(0)==0 && balanceOf(1)==0 && balanceOf(2)==0);
}


// // Recovery and Paused Modes

/// @title: basicOperationsRevertOnPause
/// @description: All basic operations must revert while in a paused state.
/// @dev: passes
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

/// @title pauseStartOnlyPauseWindow
/// @notice If a function sets the contract into pause mode, it must only be during the pauseWindow.
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

/// @title: rule: unpausedAfterBuffer
/// @notice: After the buffer window finishes, the contract may not enter the paused state
/// @dev: passes
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

/// @title: ZeroOwnerPercentageInRecovery
/// @notice: _getProtocolPoolOwnershipPercentage must always return 0 if recovery mode is enabled.
rule ZeroOwnerPercentageInRecovery() {
    env e; 
    calldataarg args;
    require inRecoveryMode(); 
    uint256 feePercentage;
    uint256 totalGrowthInvariant;
    feePercentage, totalGrowthInvariant = _getProtocolPoolOwnershipPercentage(e, args);
    assert feePercentage==0;
}

/// @title: DisablingRMDoesNotChangeValues
/// @notice: Disabling recovery mode must not change balances and virtualSupply. protocolFeeAmount should be reset to 0 by disableRecoveryMode.
/// @dev: passes
rule DisablingRMDoesNotChangeValues() {
    uint256 _balance0 = getSupplyAndFeesData(0);
    uint256 _balance1 = getSupplyAndFeesData(1);
    uint256 _virtualSupply = getSupplyAndFeesData(2);
    uint256 _protocolFeeAmount =  getSupplyAndFeesData(3);
    env e;

    disableRecoveryMode(e);

    uint256 balance0_ = getSupplyAndFeesData(0);
    uint256 balance1_ = getSupplyAndFeesData(1);
    uint256 virtualSupply_ = getSupplyAndFeesData(2);
    uint256 protocolFeeAmount_ =  getSupplyAndFeesData(3);

    assert _balance0 == balance0_;
    assert _balance1 == balance1_;
    assert _virtualSupply == virtualSupply_;
    assert protocolFeeAmount_ == 0;
}

/// @title: prOtherFunctionsAlwaysRevert
/// @notice If both paused and recovery mode is active, the set functions must always revert.
/// @dev: passes
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

/// @title: recoveryExitNoStableMath
/// @notice: In recovery mode, exit must never enter any of the functions in StableMath.sol.
/// @dev: passes
rule recoveryExitNoStableMath() {

    require inRecoveryMode();
    require !beenCalled();

    env e;
    // setup(e);

    bytes userData;
    require isRecoveryModeExitKind(userData);

    bytes32 poolId; address sender; address recipient; uint256[] balances;
    uint256 lastChangeBlock; uint256 protocolSwapFeePercentage;

    onExitPool(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData);

    assert !beenCalled();
}
