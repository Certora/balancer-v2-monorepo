/***
### Assumptions and Simplifications
 #### TODO
    
#### Harnessing
 #### TODO
    
#### Munging
    
#### Definitions

*/
methods {
    totalTokensBalance(address) returns (uint256) envfree
    inRecoveryMode() returns (bool) envfree
    _MIN_UPDATE_TIME() returns (uint256) envfree
    _MAX_AMP_UPDATE_DAILY_RATE() returns (uint256) envfree
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

    // // authorizor functions
    // getAuthorizor() returns address => DISPATCHER(true)
    // _getAuthorizor() returns address => DISPATCHER(true)
    // _canPerform(bytes32, address) returns (bool) => NONDET
    // // harness functions
    disableRecoveryMode() envfree
    // setRecoveryMode(bool) envfree
    minAmp() returns(uint256) envfree
    maxAmp() returns(uint256) envfree
    AMP_PRECISION() envfree
    mul(uint256, uint256) returns (uint256) => NONDET
    isRecoveryModeExitKind(bytes) returns (bool) envfree

    balanceOf(uint256) returns (uint256) envfree
    balanceOf(address,uint256) returns (uint256) envfree
    getTotalTokens() returns (uint256) envfree
    onSwap((uint8,address,address,uint256,bytes32,uint256,address,address,bytes),uint256[],uint256,uint256) returns (uint256)

    beenCalled() returns (bool) envfree // stableMath harness

    // external calls
    // getFeeTypePercentage(uint256) returns (uint256) => NONDET
    // // 0x1a7c3263 => NONDET
    // registerTokens(bytes32, address[], address[]) => NONDET
    // // 0x66a9c7d2 => NONDET
    // registerPool(uint8) returns (bytes32) => NONDET
    // // 0xabd90846 => NONDET
    // getProtocolFeesCollector() returns (address) => NONDET
    // getVault() returns (address) envfree
    // canPerform(bytes32, address, address) returns (bool) => NONDET
}

/// @title: recoveryExitNoExternalCalls
/// @notice: In recovery mode, exitPool must not call any external contracts
/// @dev manually check for havocs and view
rule recoveryExitNoExternalCalls() {
    require inRecoveryMode();

    bytes userData;
    require isRecoveryModeExitKind(userData);

    env e;
    bytes32 poolId; address sender; address recipient; uint256[] balances;
    uint256 lastChangeBlock; uint256 protocolSwapFeePercentage;

    onExitPool(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData);

    assert false, "check call resolution for anything other than getRate and transfer havocing";
}