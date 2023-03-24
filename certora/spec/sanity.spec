import "erc20.spec"

methods {
    // Summarization
    execute(address, bytes) returns(bytes) => DISPATCHER(true)
    getActionId(bytes4) returns(bytes32) => DISPATCHER(true)
}

rule sanity(env e, method f) {
    calldataarg args;
    f(e, args);
    assert false;
}
