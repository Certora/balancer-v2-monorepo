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
    getRate() returns (uint256) envfree    
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
    disableRecoveryMode() envfree
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

definition DAY() returns uint256 = 1531409238;

function getAmplificationFactor(env e) returns uint256 {
    uint256 param; bool updating;
    param, updating = _getAmplificationParameter(e);
    return param;
}


////////////////////////////////////////////////////////////////////////////
//                            Invariants                                  //
////////////////////////////////////////////////////////////////////////////

invariant amplificationFactorBounded(env e)
    getAmplificationFactor(e) <= maxAmp() && getAmplificationFactor(e) >= minAmp()
{ preserved {
    // require !initialized() => getAmplificationFactor(e) == 0; // amplification factor is 0 before initialization
    require _MAX_AMP_UPDATE_DAILY_RATE() == 2;
    require _MIN_UPDATE_TIME() == DAY();
    require AMP_PRECISION() == 1000;
} }

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

/// @title: rule: DisablingRMDoesNotChangeValues
/// @notice: Disabling recovery mode should not change balances and virtualSupply. protocolFeeAmount should be reset to 0 by disableRecoveryMode
/// @notice: passes
rule DisablingRMDoesNotChangeValues() {
    uint256 _balance0 = getSupplyAndFeesData(0);
    uint256 _balance1 = getSupplyAndFeesData(1);
    uint256 _virtualSupply = getSupplyAndFeesData(2);
    uint256 _protocolFeeAmount =  getSupplyAndFeesData(3);

    disableRecoveryMode();

    uint256 balance0_ = getSupplyAndFeesData(0);
    uint256 balance1_ = getSupplyAndFeesData(1);
    uint256 virtualSupply_ = getSupplyAndFeesData(2);
    uint256 protocolFeeAmount_ =  getSupplyAndFeesData(3);

    assert _balance0 == balance0_;
    assert _balance1 == balance1_;
    assert _virtualSupply == virtualSupply_;
    assert protocolFeeAmount_ == 0;
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

/// @title: recoveryExitNoStableMath
/// @notice: in recovery mode, exit never calls any simple math functions
/// @notice: passes
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
