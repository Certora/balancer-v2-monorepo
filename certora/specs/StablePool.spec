
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
    
    //// @dev vault 
    getPoolTokens(bytes32) returns (address[], uint256[]) => NONDET
    getPoolTokenInfo(bytes32,address) returns (uint256,uint256,uint256,address) => NONDET
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
    getUintArrayIndex(uint256[], uint256) returns (uint256) envfree

    getTotalTokens() returns (uint256) envfree

}

////////////////////////////////////////////////////////////////////////////
//                            Helper Functions                            //
////////////////////////////////////////////////////////////////////////////

function setup() { 
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
//                               Rules                                    //
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
    
    setup();
    require totalSupply() == 0;
    require !inRecoveryMode();

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

    env e;

    if f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        bytes32 poolId; address sender; address recipient; uint256[] balances; 
        uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
        require getUintArrayIndex(balances, 0) > 0;
        require getUintArrayIndex(balances, 1) > 0;
        require getJoinKind(userData) == 1; // exact tokens
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
    
    setup();
    require totalSupply() == 0;
    require inRecoveryMode();

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

    env e;

    if f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        bytes32 poolId; address sender; address recipient; uint256[] balances; 
        uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
        require getUintArrayIndex(balances, 0) > 0;
        require getUintArrayIndex(balances, 1) > 0;
        require getJoinKind(userData) == 1; // exact tokens
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
    
    setup();
    require totalSupply() > 0; // cutting out big branch
    require !inRecoveryMode();

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

    env e;

    if f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        bytes32 poolId; address sender; address recipient; uint256[] balances; 
        uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
        require getUintArrayIndex(balances, 0) > 0;
        require getUintArrayIndex(balances, 1) > 0;
        require getJoinKind(userData) == 1; // exact tokens
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
    
    setup();
    require totalSupply() > 0; // cutting out big branch
    require inRecoveryMode();

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

    env e;

    if f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        bytes32 poolId; address sender; address recipient; uint256[] balances; 
        uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
        require getUintArrayIndex(balances, 0) > 0;
        require getUintArrayIndex(balances, 1) > 0;
        require getJoinKind(userData) == 1; // exact tokens
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
    
    setup();
    require totalSupply() == 0;
    require !inRecoveryMode();

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

    env e;

    if f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        bytes32 poolId; address sender; address recipient; uint256[] balances; 
        uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
        require getUintArrayIndex(balances, 0) > 0;
        require getUintArrayIndex(balances, 1) > 0;
        require getJoinKind(userData) == 2; // exact bpt
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
    
    setup();
    require totalSupply() == 0;
    require inRecoveryMode();

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

    env e;

    if f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        bytes32 poolId; address sender; address recipient; uint256[] balances; 
        uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
        require getUintArrayIndex(balances, 0) > 0;
        require getUintArrayIndex(balances, 1) > 0;
        require getJoinKind(userData) == 2; // exact bpt
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
    
    setup();
    require totalSupply() > 0; // cutting out big branch
    require !inRecoveryMode();

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

    env e;

    if f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        bytes32 poolId; address sender; address recipient; uint256[] balances; 
        uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
        require getUintArrayIndex(balances, 0) > 0;
        require getUintArrayIndex(balances, 1) > 0;
        require getJoinKind(userData) == 2; // exact bpt
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
    
    setup();
    require totalSupply() > 0; // cutting out big branch
    require inRecoveryMode();

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

    env e;

    if f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        bytes32 poolId; address sender; address recipient; uint256[] balances;
        uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
        require sender != currentContract; // times out if I remove this 
        require getUintArrayIndex(balances, 0) > 0;
        require getUintArrayIndex(balances, 1) > 0;
        require getJoinKind(userData) == 2; // exact bpt
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