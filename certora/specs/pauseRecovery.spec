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
    // ComposableStablePoolHarness
    totalTokensBalance(address) returns (uint256) envfree
    getAdjustedBalances(uint256, bool) returns (uint256)
    // setRecoveryMode(bool) envfree
    minAmp() returns(uint256) envfree
    maxAmp() returns(uint256) envfree
    AMP_PRECISION() envfree
    balanceOf(address,uint256) returns (uint256) envfree    
    getTotalTokens() returns (uint256) envfree
    getCurrentAmpAndInvariant() returns(uint256, uint256)

    // ComposableStablePool
    getSupplyAndFeesData(uint256) returns (uint256) envfree
    getActualSupply() returns (uint256) envfree
    onSwap((uint8,address,address,uint256,bytes32,uint256,address,address,bytes),uint256[],uint256,uint256) returns (uint256)

    // StableMathHarness
    beenCalled() returns (bool) envfree // stableMath harness

    // BasePool
    inRecoveryMode() returns (bool) envfree
    getPoolId() returns(bytes32) envfree

    // StablePoolAmplifcation
    _MIN_UPDATE_TIME() returns (uint256) envfree
    _MAX_AMP_UPDATE_DAILY_RATE() returns (uint256) envfree
    _getAmplificationParameter() returns (uint256,bool) => CONSTANT

    // ComposableStablePoolRates
    _scalingFactors() returns (uint256[]) => CONSTANT

    // VaultHarness
    registerTokens(bytes32, address[], address[]) => NONDET
    registerPool(uint8) returns (bytes32) => NONDET
    getProtocolFeesCollector() returns (address) => NONDET
        
    // BasePoolAuthorization
    _DELEGATE_OWNER() returns (address) envfree
    getActionId(uint32 selector) returns (bytes32) envfree

    // ComposableStablePoolProtocolFees
    getProtocolPoolOwnershipPercentage(uint256[]) returns (uint256,uint256)
    getLastJoinExitData() returns (uint256, uint256)    
    _getProtocolPoolOwnershipPercentage(uint256[],uint256,uint256) returns (uint256, uint256)

    // ComposableStablePoolStorage
    _isTokenExemptFromYieldProtocolFee(uint) returns bool envfree    
    _hasRateProvider(uint) returns bool envfree
    _areAllTokensExempt() returns (bool) envfree
    _areNoTokensExempt() returns (bool) envfree
    _rateProvider0() returns (address) envfree
    getBptIndex() envfree

    // BalancerPoolToken 
    getVault() returns (address) envfree

    // BasePoolAuthorization
    canPerform(bytes32, address, address) returns (bool) => NONDET

    // RecoveryMode
    disableRecoveryMode() envfree

    // BasePoolUserData
    isRecoveryModeExitKind(bytes) returns (bool) envfree

    // ProtocolFeePercentagesProvider
    getFeeTypePercentage(uint256) returns (uint256) => NONDET

    // IRateProvider
    getRate() returns (uint256) => NONDET    
}


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

invariant NoTokensExempt(uint256 index) 
    _areNoTokensExempt()==true => _hasRateProvider(index) == false

invariant AllTokensExample(uint256 index) 
    _areAllTokensExempt()==true => _hasRateProvider(index) == true

invariant ExamptRequiresRateProvider(uint index)
    _isTokenExemptFromYieldProtocolFee(index) => _hasRateProvider(index)

invariant isRateProviderSet()
    _rateProvider0() == 0 <=> _hasRateProvider(0)==false

rule AdjustedEqualToBalance() {
    require _isTokenExemptFromYieldProtocolFee(0) => _hasRateProvider(0);
    require getBptIndex()>0;
    env e;
    uint256 balance;
    bool ignoreExemptFlags;
    uint256 adjustedBalance = getAdjustedBalances(e, balance, ignoreExemptFlags);
    assert !(_isTokenExemptFromYieldProtocolFee(0) || (ignoreExemptFlags && _hasRateProvider(0))) => balance==adjustedBalance;
}

rule updateRate() {
    env e;
    uint256 index;
    require index<3;
    require index<getTotalTokens();
    uint256 currentAmp;
    uint256 currentInvariant;
    bool ignoreExemptFlags;
    currentAmp, currentInvariant = getCurrentAmpAndInvariant(e);
    uint256 balance;

    // _updateOldRate(e, index);
    disableRecoveryMode();

    uint256 lastJoinExitAmp;
    uint256 lastPostJoinExitInvariant;
    lastJoinExitAmp, lastPostJoinExitInvariant = getLastJoinExitData(e);
    uint256 adjustedBalance = getAdjustedBalances(e, balance, ignoreExemptFlags);

    assert currentAmp == lastJoinExitAmp;
    assert currentInvariant == lastPostJoinExitInvariant;
    assert getOldRate(e, index) == getCurrentRate(e, index);
    assert balance==adjustedBalance;
}

rule ZeroFeeWhenAllInvariantsAreSame() {
    env e;
    calldataarg args;
    uint256 feePercentage;
    uint256 totalGrowthInvariant;
    feePercentage, totalGrowthInvariant =  _getProtocolPoolOwnershipPercentage(e, args);
    assert feePercentage==0;
}

// d) disabling recovery mode causes no change in the return value of getRate() or getActualSupply()
rule DisablingRMDoesNotChangeRateAndActualSupply() {
    // uint _rate = getRate();
    uint _actualSupply = getActualSupply();
    disableRecoveryMode();
    // uint rate_ = getRate();
    uint actualSupply_ = getActualSupply();
    // assert _rate == rate_;
    assert _actualSupply == actualSupply_;
}
// // e) _getProtocolPoolOwnershipPercentage should return 0 immediately after disabling recovery mode
// rule ZeroOwnerPercentageAfterDisablingRecovery() {
//     env e; 
//     calldataarg args;
//     require inRecoveryMode(); 
//     disableRecoveryMode();
//     uint256 feePercentage;
//     uint256 totalGrowthInvariant;
//     feePercentage, totalGrowthInvariant = getProtocolPoolOwnershipPercentage(e, args);
//     assert feePercentage==0;
// }