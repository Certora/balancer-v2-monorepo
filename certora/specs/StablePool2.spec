import "./erc20.spec";

using StableMath as stableMath;
using Vault as vault;
using InvCalculator as invCalculator;

methods {
    function StableMath._calculateInvariant(uint256 amplificationParameter, uint256[] memory balances) internal returns uint256 => cvl_calculateInvariantWrapper(amplificationParameter, balances); 
    function InvCalculator.cvl_calculateInvariant(uint256 amplificationParameter, uint256[] balances) external returns uint256 envfree;
    function Vault.getPoolTokens(bytes32 poolId) external returns (address[], uint256[], uint256) envfree;
    function StablePoolAmplification._getAmplificationParameter() internal returns (uint256, bool) => cvl_getAmplificationParameterWrapper();
    function StableMath._getTokenBalanceGivenInvariantAndAllOtherBalances(uint256, uint256[] memory, uint256, uint256) internal returns (uint256) => NONDET; // we need something more precise here, but not sure how to munge it following the invariant munge.
}

ghost uint256 g_getAmplificationParameter_ampFactor;
ghost bool g_getAmplificationParameter_isUpdating;

function cvl_calculateInvariantWrapper(uint256 amplificationParameter, uint256[] balances) returns (uint256) {
    return invCalculator.cvl_calculateInvariant(amplificationParameter, balances);
}

function cvl_getAmplificationParameterWrapper() returns (uint256, bool) {
    return (g_getAmplificationParameter_ampFactor, g_getAmplificationParameter_isUpdating);
}

rule sanity {
    env e;
    calldataarg args;
    method certoraF;
    certoraF(e, args);
    satisfy true, "sanity check failed";
}

rule monotonic_invariant() {
    env e;
    bytes32 poolId;
    address[] tokensBefore;
    uint256[] balancesBefore;
    uint256 lastChangeBlockBefore;

    tokensBefore, balancesBefore, lastChangeBlockBefore = vault.getPoolTokens(poolId);
     
    uint256 x1 = invCalculator.cvl_calculateInvariant(g_getAmplificationParameter_ampFactor, balancesBefore);
    calldataarg args;
    onSwap(e, args);
    calldataarg args2;
    onSwap(e, args2);

    address[] tokensAfter;
    uint256[] balancesAfter;
    uint256 lastChangeBlockAfter;
    tokensAfter, balancesAfter, lastChangeBlockAfter = vault.getPoolTokens(poolId);
    

    uint256 x2 = invCalculator.cvl_calculateInvariant(g_getAmplificationParameter_ampFactor, balancesAfter);
    assert x2 >= x1;
}