
/***
### Assumptions and Simplifications
 #### TODO
    
#### Harnessing
 #### TODO
    
#### Munging
    
#### Definitions

*/

import "../helpers/erc20.spec"

////////////////////////////////////////////////////////////////////////////
//                      Methods                                           //
////////////////////////////////////////////////////////////////////////////

methods {
    //// @dev harness functions
    totalTokensBalance() returns (uint256) envfree
    inRecoveryMode() returns (bool) envfree
    getJoinKind(bytes) returns (uint8) envfree
    requireNonzero(uint256[], uint256) envfree
    getTotalTokens() returns (uint256) envfree

    /// @dev StableMath functions are munged to call the below functions which 
    /// can be summarized. Functions with dynamic arrays can not be summarized 
    /// in CVL at this time.
    getTokenBal(uint256 balance1, uint256 balance2, uint256 newInvariant, uint256 index) returns(uint256) 
        => newGetTokenBalance(balance1, balance2, newInvariant, index)
    calculateInvariant(uint256 balance1, uint256 balance2) returns (uint256) 
        => calculatedInvariant(balance1,balance2)
}

////////////////////////////////////////////////////////////////////////////
//                            Helper Functions                            //
////////////////////////////////////////////////////////////////////////////

/// We assume that the pool has only 2 tokens to deal with limitations of the tool, our justification is that any 
/// exploit that is possible on 3+ tokens will be possible on 2 tokens
function setup() { 
    require getTotalTokens() == 2; 
}

/// This function is a summary of `_getTokenBalanceGivenInvariantAndAllOtherBalances` which assumes that if the 
/// invariant increases than the balance of the token that is being calculated increases. This is justified because we 
/// only use it when proving rules that depend on the functionality of `onJoinPool`.
function newGetTokenBalance(uint256 balance1, uint256 balance2, uint256 newInvariant, uint256 index) returns uint256 {
    uint256 newBalance;
    uint256 oldInvariant = calculatedInvariant(balance1,balance2);
    if (index == 0) {
        require newInvariant > oldInvariant => newBalance > balance1;
    } else {
        require newInvariant > oldInvariant => newBalance > balance2;
    }
    return newBalance;
}

/// `noFreeMinting` rule is broken up by cases to ease the load on the prover. The rule is proven for zero/non-zero 
/// totalSupply, on/off recovery mode, and the two types of `joinKind`. The below function is used to require these 
/// dconditions in a modular way.
function noFreeMintingSetup(uint8 joinKind, bool supply, bool recovery) {
    setup();

    bytes userData;
    require getJoinKind(userData) == joinKind;
    require (totalSupply() > 0) == supply;
    require inRecoveryMode() == recovery;

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

    method f; env e; calldataarg args;

    if f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        bytes32 poolId; address sender; address recipient; uint256[] balances; 
        uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; 
        require sender != currentContract; // times out if I remove this 
        requireNonzero(balances, 0);
        requireNonzero(balances, 1);
        onJoinPool(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData);
    } else {
        f(e, args);
    }

    uint256 totalBpt_ = totalSupply();
    uint256 totalTokens_ = totalTokensBalance();

    assert totalBpt_>_totalBpt => totalTokens_>_totalTokens, 
        "an increase in total BPT must lead to an increase in pool's total tokens";
}

////////////////////////////////////////////////////////////////////////////
//                    Ghosts, hooks and definitions                       //
////////////////////////////////////////////////////////////////////////////

/// @dev This function is a summary for `_calculateInvariant` that assumes that the invariant
/// is greater than or equal to the sum of pool's token balances and less than or equal 
/// to the product.
function calculatedInvariant(uint256 balance1, uint256 balance2) returns uint256 {
    uint256 invar;
    require invar >= balance1 + balance2;
    require invar <= balance1 * balance2;
    require determineInvariant[balance1][balance2] == invar;
    return invar;
}

/// @dev This ghost mapping is used to store all calculated invariants so we have a database of 
/// token balances to invariant which we can use to assume that `_calculateInvariant` is 
/// deterministic.
ghost mapping(uint256 => mapping(uint256 => uint256)) determineInvariant;

/// A ghost tracking values for an invariant given two token balances;
///
/// @dev we assume only 2 tokens in a pool and that a bounded arbitrary value for the invariant
// ghost calculatedInvariant1(uint256 balance1, uint256 balance2) returns(uint256) {
//     axiom forall uint256 balance1. forall uint256 balance2.
//         calculatedInvariant1(balance1, balance2) >= balance1 + balance2;
//     axiom forall uint256 balance1. forall uint256 balance2.
//         calculatedInvariant1(balance1, balance2) <= balance1 * balance2;
// }

// ghost calculatedInvariant1(uint256, uint256) returns(uint256) {
//     axiom forall uint256 a1. forall uint256 b1. calculatedInvariant1(a1, b1) >= a1 + b1;
//     axiom forall uint256 a2. forall uint256 b2. calculatedInvariant1(a2, b2) <= a2 * b2;
// }

/// A ghost tracking the sum of all BPT user balances in the pool
///
/// @dev We assume sum of all balances equals 0 on contract construction.
ghost mathint sum_all_users_BPT {
    init_state axiom sum_all_users_BPT == 0;
}

/// @dev A hook that keeps `sum_all_users_BPT` up to date with the `_balances` mapping.
hook Sstore _balances[KEY address user] uint256 balance (uint256 old_balance) STORAGE {
    sum_all_users_BPT = sum_all_users_BPT + balance - old_balance;
}

////////////////////////////////////////////////////////////////////////////
//                            Invariants                                  //
////////////////////////////////////////////////////////////////////////////

/// @title solvency
/// @notice Sum of all users' BPT balance must be less than or equal to BPT's `totalSupply`.
invariant solvency()
    totalSupply() >= sum_all_users_BPT

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
rule noFreeMinting_exactTokens_noSupply_noRecovery {
    noFreeMintingSetup(1, false, false);
}
rule noFreeMinting_exactTokens_noSupply_yesRecovery {
    noFreeMintingSetup(1, false, true);
}
rule noFreeMinting_exactTokens_yesSupply_noRecovery {
    noFreeMintingSetup(1, true, false);
}
rule noFreeMinting_exactTokens_yesSupply_yesRecovery {
    noFreeMintingSetup(1, true, true);
}
rule noFreeMinting_exactBpt_noSupply_noRecovery {
    noFreeMintingSetup(2, false, false);
}
rule noFreeMinting_exactBpt_noSupply_yesRecovery {
    noFreeMintingSetup(2, false, true);
}
rule noFreeMinting_exactBpt_yesSupply_noRecovery {
    noFreeMintingSetup(2, true, false);
}
rule noFreeMinting_exactBpt_yesSupply_yesRecovery {
    noFreeMintingSetup(2, true, true);
}

/// @title onlyOnJoinPoolCanAndMustInitialize
/// @notice `totalSupply` must be non-zero if and only if `onJoinPool` is successfully called. Additionally, the balance of the 
/// zero adress must be non-zero if `onJoinPool` was successfully called. 
/// @dev Calling `onJoinPool` for the first time initializes the pool, minting some BPT to the zero address.
rule onlyOnJoinPoolCanAndMustInitialize(method f) {
    env e; calldataarg args;
    require totalSupply() == 0;
    
    f(e, args);
    
    assert
        totalSupply() > 0 <=> f.selector==onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector,
        "onJoinPool must be the only function that can initialize a pool and must initialize if called";
    assert f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector 
        => balanceOf(0) > 0, "zero address must be minted some tokens on initialization";
}

/// @title cantBurnZerosBPT
/// @notice The zero address's BPT balance can never go from non-zero to zero.
rule cantBurnZerosBPT(method f) {
    require balanceOf(0) > 0;
    env e; calldataarg args;
    f(e, args); // vacuous for onSwap since ERC20 transfer revert when transferring to 0 address
    assert balanceOf(0) > 0, "zero address must always have non-zero balance";
}