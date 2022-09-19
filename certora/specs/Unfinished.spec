
rule cantProfitOffRecovery {
    require !inRecoveryMode();
    env e;
    storage initial = lastStorage;

    bytes32 poolId; address sender; address recipient; uint256[] balances; 
    uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;

    onExitPool(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData) at initial;
    uint256 totalTokensNormal = totalTokensBalance();

    setRecoveryMode(e, true) at initial;
    onExitPool(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData);
    uint256 totalTokensRecovery = totalTokensBalance();

    assert totalTokensRecovery < totalTokensNormal;
}