
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


////////////////////////////////////////////////////////////////////////////
//                    Ghosts, hooks and definitions                       //
////////////////////////////////////////////////////////////////////////////

/// @dev This ghost mapping is used to store all calculated invariants so we have a database of 
/// token balances to invariant which we can use to assume that `_calculateInvariant` is 
/// deterministic.
ghost mapping(uint256 => mapping(uint256 => uint256)) determineInvariant;

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

/// @title `noFreeMinting` 
/// @notice rule is broken up by cases to ease the load on the prover. The rule below is proven in 8 cases base on 
/// zero/non-zero totalSupply, on/off recovery mode, and the two types of `joinKind`. The below function is used to 
/// require these conditions in a modular way.
rule noFreeMinting(uint8 joinKind, bool supply, bool recovery) {
    setup();

    uint256 _totalBpt = totalSupply();
    uint256 _totalTokens = totalTokensBalance();

    method f; env e; calldataarg args;

    if f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector {
        bytes32 poolId; address sender; address recipient; uint256[] balances; 
        uint256 lastChangeBlock; uint256 protocolSwapFeePercentage; bytes userData;
        require sender != currentContract;
        requireNonzero(balances, 0); // requires the 0th index of balances is nonzero
        requireNonzero(balances, 1); // requires the 1st index of balances is nonzero
        onJoinPool(e, poolId, sender, recipient, balances, lastChangeBlock, protocolSwapFeePercentage, userData);
    } else {
        f(e, args);
    }

    uint256 totalBpt_ = totalSupply();
    uint256 totalTokens_ = totalTokensBalance();

    assert totalBpt_>_totalBpt => totalTokens_>_totalTokens, 
        "an increase in total BPT must lead to an increase in pool's total tokens";
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