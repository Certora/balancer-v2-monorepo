pragma solidity ^0.8.0;

import "../munged/MainContract.sol";

// This is the contract that is actually verified; it may contain some helper
// methods for the spec to access internal state, or may override some of the
// more complex methods in the original contract.
abstract contract ExampleHarness is MainContract {

}

