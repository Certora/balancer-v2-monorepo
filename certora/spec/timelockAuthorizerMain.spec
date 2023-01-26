import "erc20.spec"

// using MockVault as MockVault
using Vault as Vault

methods {
    execute(address, bytes) returns(bytes) => DISPATCHER(true)
    getActionId(bytes4) returns(bytes32) => DISPATCHER(true)        // what is the "target/where" in cancel()? "where" in schedule?   setDelay()

    getSchedExeWhere(uint256) returns(address) envfree
    getSchedExeData(uint256) returns(bytes) envfree
    getSchedExeExecuted(uint256) returns(bool) envfree
    getSchedExeCancelled(uint256) returns(bool) envfree
    getSchedExeProtected(uint256) returns(bool) envfree
    getSchedExeExecutableAt(uint256) returns(uint256) envfree
    getSchedExeLength() returns(uint256) envfree

    EVERYWHERE() returns(address) envfree
    _isPermissionGranted(bytes32) returns(bool) envfree
    getPermissionId(bytes32, address, address) returns(bytes32) envfree
    _root() returns(address) envfree
}

rule sanity(env e, method f) {
    calldataarg args;
    f(e, args);
    assert false;
}
