import "../helpers/erc20.spec"

methods {
    // ComposableStablePoolHarness
    totalTokensBalance(address) returns (uint256) envfree
    getBalance(uint256) returns (uint256)
    getAdjustedBalance(uint256, uint256, bool) returns (uint256)
    minAmp() returns(uint256) envfree
    maxAmp() returns(uint256) envfree
    AMP_PRECISION() envfree
    balanceOf(address,uint256) returns (uint256) envfree    
    getTotalTokens() returns (uint256) envfree
    getCurrentAmpAndInvariant() returns(uint256, uint256)

    // ComposableStablePool
    getSupplyAndFeesData(uint256) returns (uint256) envfree
    getActualSupply() returns (uint256) 
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
    disableRecoveryMode()

    // BasePoolUserData
    isRecoveryModeExitKind(bytes) returns (bool) envfree

    // ProtocolFeePercentagesProvider
    getFeeTypePercentage(uint256) returns (uint256) => DISPATCHER(true)

    // IRateProvider
    getRate() returns (uint256) => DISPATCHER(true)    
}


definition DAY() returns uint256 = 1531409238;

function getAmplificationFactor(env e) returns uint256 {
    uint256 param; bool updating;
    param, updating = _getAmplificationParameter(e);
    return param;
}

////////////////////////////////////////////////////////////////////////////
//                               Rule                                     //
////////////////////////////////////////////////////////////////////////////
 
/// @title: basicOperationsRevertOnPause
/// @notice: All basic operations must revert while in a paused state
/// @notice: SUCCESS
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
rule pauseStartOnlyPauseWindow(method f) filtered {f -> (!f.isView && f.selector != updateProtocolFeePercentageCache().selector)} {
    env e; calldataarg args;
    bool paused_; uint256 pauseWindowEndTime; uint256 bufferPeriodEndTime;
    paused_, pauseWindowEndTime, bufferPeriodEndTime = getPausedState(e);
    require !paused_; // start in an unpaused state

    f(e, args);

    bool _paused; uint256 dc1; uint256 dc2;
    _paused, dc1, dc2 = getPausedState(e);
    // if we are now paused, then the current time must be within the pauseWindow
    assert _paused => e.block.timestamp <= pauseWindowEndTime, "paused after end window";
}

/// @title: rule: unpausedAfterBuffer
/// @notice: After the buffer window finishes, the contract may not enter the paused state
/// @notice: SUCCESS
rule unpausedAfterBuffer(method f) filtered {f -> (!f.isView && f.selector != updateProtocolFeePercentageCache().selector)} {
    env e; calldataarg args;

    f(e, args);

    env e2;
    require e2.block.timestamp >= e.block.timestamp; // shouldn't change the results, but we only care about checking pause after the function call
    bool paused; uint256 pauseWindowEndTime; uint256 bufferPeriodEndTime;
    paused, pauseWindowEndTime, bufferPeriodEndTime = getPausedState(e2);
    require bufferPeriodEndTime >= pauseWindowEndTime; 
    assert e2.block.timestamp > bufferPeriodEndTime => !paused, "contract remained pauased after buffer period";
}

/// @title: prOtherFunctionsAlwaysRevert
/// @notice: If both paused and recovery mode is active, the set functions must always revert
/// @notice: SUCCESS
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
/// @notice: SUCCESS
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

/// @title: ZeroOwnerPercentageInRecovery
/// @notice _getProtocolPoolOwnershipPercentage should always return 0 if recovery mode is enabled
/// @notice: SUCCESS
rule ZeroOwnerPercentageInRecovery() {
    env e; 
    calldataarg args;
    require inRecoveryMode(); 
    uint256 feePercentage;
    uint256 totalGrowthInvariant;
    feePercentage, totalGrowthInvariant = _getProtocolPoolOwnershipPercentage(e, args);
    assert feePercentage==0;
}

/// @title: DisableRecoveryModeChangesStates
/// @notice: disableRecoveryMode() should update lastJoinExitAmp, lastPostJoinExitInvariant, as well as rate cache if rateProvider has been set, so that balance always equals adjusted balance
/// @notice: SUCCESS
rule DisableRecoveryModeChangesStates() {
    env e;
    calldataarg args;
    uint256 index=0;
    require index!=getBptIndex();
    require index<getTotalTokens();
    require getBptIndex()<getTotalTokens();
    require getBptIndex()==1;
    require getTotalTokens()==2;    
    // requireInvariant ExamptRequiresRateProvider(0); // the invariant itsefl will timeout in instate, so using require directly
    require _isTokenExemptFromYieldProtocolFee(0) => _hasRateProvider(0); // include bpt
    require _isTokenExemptFromYieldProtocolFee(1) => _hasRateProvider(1);
    // require _isTokenExemptFromYieldProtocolFee(2) => _hasRateProvider(2);    
    
    uint256 currentAmp;
    uint256 currentInvariant;
    bool ignoreExemptFlags;
    currentAmp, currentInvariant = getCurrentAmpAndInvariant(e);
    uint256 balance; // = getBalance(e, index); // use a random balance instead of from the pool, this is to avoid potential timeout

    disableRecoveryMode(e);

    uint256 lastJoinExitAmp;
    uint256 lastPostJoinExitInvariant;
    lastJoinExitAmp, lastPostJoinExitInvariant = getLastJoinExitData(e);
    uint256 adjustedBalance = getAdjustedBalance(e, index, balance, ignoreExemptFlags);

    assert currentAmp == lastJoinExitAmp, "amp is not stored correctly by disableRecoveryMode()";
    assert currentInvariant == lastPostJoinExitInvariant, "invariant is not stored correctly by disableRecoveryMode()";
    assert _hasRateProvider(index)==true => getOldRate(e, index) == getCurrentRate(e, index), "currentRate should be stored in oldRate when rateProvider has been set by disableRecoveryMode()";
    assert balance==adjustedBalance, "adjustedBalance should be the same as balance immediately after disableRecoveryMode()";
}

/// @title: ZeroOwnerPercentageAfterDisablingRecovery
/// @notice disableRecoveryMode() should not change virtualSupply. Immediately after disabling, _getProtocolPoolOwnershipPercentage should return 0 fee percentage. This assumes all invariants are the same, which is guaranteed by previous rule.
/// @notice: SUCCESS
rule ZeroOwnerPercentageAfterDisablingRecovery() {    
    env e; 
    calldataarg args;
    require getTotalTokens()==3; 
    // require getBptIndex()==2;
    require getBptIndex()<getTotalTokens();
    require _isTokenExemptFromYieldProtocolFee(0) => _hasRateProvider(0);
    require _isTokenExemptFromYieldProtocolFee(1) => _hasRateProvider(1);
    require _isTokenExemptFromYieldProtocolFee(2) => _hasRateProvider(2);
    uint256 _virtualSupply = totalSupply();
    
    // require inRecoveryMode(); 
    disableRecoveryMode(e);

    uint256 virtualSupply_ = totalSupply();
    uint256 protocolPoolOwnershipPercentage;
    uint256 totalGrowthInvariant;
    protocolPoolOwnershipPercentage, totalGrowthInvariant = getProtocolPoolOwnershipPercentage(e, args);
    assert protocolPoolOwnershipPercentage==0, "protocolPoolOwnershipPercentage should return 0 immediately after disableRecoveryMode()";
    assert _virtualSupply == virtualSupply_, "disableRecoveryMode() should not change virtualSupply";
}

