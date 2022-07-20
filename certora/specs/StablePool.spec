import "../helpers/erc20.spec"

// nondet all,				onSwap			|  onJoinPool

// nondet 		1st, 		onSwap 	timeout |  onJoinPool
// nondet 		2nd, 		onSwap		 	|  onJoinPool 	timeout
// nondet 		3rd, 		onSwap		 	|  onJoinPool 	timeout
// nondet 		4th, 		onSwap 	timeout |  onJoinPool 	timeout
// nondet 		5th, 		onSwap 	timeout |  onJoinPool 	timeout
// nondet 		6th, 		onSwap 	timeout |  onJoinPool 	timeout
// nondet 		7th, 		onSwap 	timeout |  onJoinPool 	timeout
// nondet 		8th, 		onSwap 	timeout |  onJoinPool 	timeout
// nondet 		9th, 		onSwap 	timeout |  onJoinPool 	timeout
// nondet 		10th,	 	onSwap 			|  onJoinPool 	timeout
// nondet 		11th,	 	onSwap 	timeout |  onJoinPool 	timeout

// nondet 1st and 10th, 	onSwap 			|  onJoinPool 	

/// Functions that matter
// _calculateInvariant matters for onJoinPool
// _calcOutGivenIn matters for onSwap
// _calcInGivenOut matters for onSwap
// _getTokenBalanceGivenInvariantAndAllOtherBalances matters for onSwap

// want properties of math functions which we can require

////////////////////////////////////////////////////////////////////////////
//                      Methods                                           //
////////////////////////////////////////////////////////////////////////////

methods {
	// stable math
    _calculateInvariant(uint256,uint256[]) returns (uint256) => NONDET
    //_calcOutGivenIn(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) => NONDET
    //_calcInGivenOut(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) => NONDET
    //_calcBptOutGivenExactTokensIn(uint256,uint256[],uint256[],uint256,uint256) returns (uint256) => NONDET
    //_calcTokenInGivenExactBptOut(uint256,uint256[],uint256,uint256,uint256,uint256)returns (uint256) => NONDET
    //_calcBptInGivenExactTokensOut(uint256,uint256[],uint256[],uint256,uint256) returns (uint256) => NONDET
    //_calcTokenOutGivenExactBptIn(uint256,uint256[],uint256,uint256,uint256,uint256) returns (uint256) => NONDET
	//_calcTokensOutGivenExactBptIn(uint256[],uint256,uint256) returns (uint256[]) => NONDET
    //_calcDueTokenProtocolSwapFeeAmount(uint256 ,uint256[],uint256,uint256,uint256) returns (uint256) => NONDET
    _getTokenBalanceGivenInvariantAndAllOtherBalances(uint256,uint256[],uint256,uint256) returns (uint256) => NONDET
    //_getRate(uint256[],uint256,uint256) returns (uint256) => NONDET

	// stable pool
	//_getAmplificationParameter() returns (uint256,bool) => NONDET

    // vault 
    getPoolTokens(bytes32) returns (address[], uint256[]) => NONDET
    getPoolTokenInfo(bytes32,address) returns (uint256,uint256,uint256,address) => NONDET


    // authorizor functions
    getAuthorizor() returns address => DISPATCHER(true)
    _getAuthorizor() returns address => DISPATCHER(true)
    _canPerform(bytes32, address) returns (bool) => NONDET
    canPerform(bytes32, address, address) returns (bool) => NONDET
}


////////////////////////////////////////////////////////////////////////////
//                    Ghosts, hooks and definitions                       //
////////////////////////////////////////////////////////////////////////////

// assume sum of all balances initially equals 0
ghost sum_all_users_BPT() returns uint256 {
    init_state axiom sum_all_users_BPT() == 0;
}

// everytime `balances` is called, update `sum_all_users_BPT` by adding the new value and subtracting the old value
hook Sstore _balances[KEY address user] uint256 balance (uint256 old_balance) STORAGE {
  havoc sum_all_users_BPT assuming sum_all_users_BPT@new() == sum_all_users_BPT@old() + balance - old_balance;
}

////////////////////////////////////////////////////////////////////////////
//                            Invariants                                  //
////////////////////////////////////////////////////////////////////////////

/// @invariant cantBurnAllBPT
/// @description Contract must not allow all BPT to be burned.
invariant cantBurnAll()
    totalSupply() > 0 

/// @invariant noMonopoly
/// @description One user must not own the whole BPT supply.
invariant noMonopoly(address user)
    totalSupply() > balanceOf(user)

/// @invariant BPTSolvency
/// @description Sum of all users' BPT balance must be less than or equal to BPT's `totalSupply`
invariant solvency()
    totalSupply() >= sum_all_users_BPT()


////////////////////////////////////////////////////////////////////////////
//                               Rule                                     //
////////////////////////////////////////////////////////////////////////////

// onSwap((uint8,address,address,uint256,bytes32,uint256,address,address,bytes),uint256[],uint256,uint256)
// onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes)
rule sanity(method f) 
//filtered {f -> f.selector == onJoinPool(bytes32,address,address,uint256[],uint256,uint256,bytes).selector}
//filtered {f -> f.selector == onSwap((uint8,address,address,uint256,bytes32,uint256,address,address,bytes),uint256[],uint256,uint256).selector}
{
	env e;
	calldataarg args;
	f(e,args);
	assert false;
}

/// @rule noFreeMinting
/// @description Contract must not allow any user to mint BPT for free
rule noFreeMinting(method f) {
    uint256 totalSupplyBefore = totalSupply();
    // define free?
    uint256 totalSupplyAfter = totalSupply();
    assert totalSupplyAfter == totalSupplyBefore;
}

/// @rule calculateBPTAccuracy
/// @description Given a value for `_calculateBPT`, calling `x` should result in user's balance increasing by that value
rule calculateBPTAccuracy(address user) {
    assert false;
}

/// @rule balanceIncreaseCorrelation
/// @description A BPT balance increase must be correlated with a token balance increase in the vault



////////////////////////////////////////////////////////////////////////////
//                            Helper Functions                            //
////////////////////////////////////////////////////////////////////////////

// TODO: Any additional helper functions



// Amplification factor

// increase amplification factor
// call method f
// for some e later than initial increase, amplification factor must be less than value set
definition DAY() returns uint256 = 1531409238;

rule amplificationFactorFollowsEndTime(method f) {
    env e; calldataarg args;
    uint256 endValue; uint256 endTime;
    uint256 startValue = _getAmplificationParameter(e);

    startAmplificationParameterUpdate(e, endValue, endTime);
    f(e, args); // call some arbitrary function

    env e_post;
    require e_post.block.timestamp > e;
    require e_post.block.timestamp < endTime;
    uint256 currentParam = _getAmplificationParameter(e_post);

    if (endValue > startValue) {
        assert currentParam < endValue, "getter: parameter increased too fast";
        assert currentParam > startValue, "amplification did not increase";
    } else {
        assert currentParam > endValue, "getter: parameter decreased too fast";
        assert currentParam < startValue, "amplification did not decrease";
    }
}

// start the amplification factor changing. Wait 2 days. Check the value at that timestamp, and then assert the value doesn't change after
rule amplificationFactorTwoDayWait(method f) {
    env e; 
    uint256 endValue; uint256 endTime;
    uint256 startValue = _getAmplificationParameter(e);
    startAmplificationParameterUpdate(e, endValue, endTime);

    env e_f; calldataarg args;
    f(e_f, args);

    env e_2days;
    require e_2days.block.timestamp == e.block.timestamp + (2 * DAY());
    uint256 actualEndValue = _getAmplificationParameter(e_days);

    env e_post;
    require e_post.block.timestamp > e_end.block.timestamp;
    assert _getAmplificationParameter(e_post) == actualEndValue, "amplfication factor still changing after 2 days";
}

rule amplificationFactorNoMoreThanDouble(method f) {
    env e; 
    uint256 endValue; uint256 endTime;
    uint256 startValue = _getAmplificationParameter(e);
    startAmplificationParameterUpdate(e, endValue, endTime);

    calldataarg args; env e_f;
    f(e_f, args);

    env e_incr;
    require e_incr.block.timestamp <= e.block.timestamp + (2 * DAY());
    uint256 actualEndValue = _getAmplificationParameter(e_days);

    assert actualEndValue <= startValue * 2, "amplification factor more than doubled";
}

// Recovery and Paused Modes

// Basic operation must not revert

// Will not call math functions

// Only governance can bring the contract into recovery mode

 
// Paused Mode:

// All basic operations must revert

 

// Pause + recovery mode

// People can only withdraw 
