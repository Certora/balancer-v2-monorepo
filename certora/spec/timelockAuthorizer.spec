import "erc20.spec"

methods {
    execute(address, bytes) returns(bytes) => DISPATCHER(true)
    getActionId(bytes4) returns(bytes32) => DISPATCHER(true)        // what is the "target/where" in cancel()? "where" in schedule?   setDelay()

    // unresolved calls
    // execute() - dispatcher doesn't work, don't know why
    // cancel() - dispatcher doesn't work, don't know why (need to clarify taget/where)
    // schedule() - solved, not sure if correct about "where"
    // setDelay() - dispatcher doesn't work, don't know why
}

rule sanity(env e, method f) {
    calldataarg args;
    f(e, args);
    assert false;
}