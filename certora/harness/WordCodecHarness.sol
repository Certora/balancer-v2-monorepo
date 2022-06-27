pragma solidity ^0.7.0;

import "../munged/solidity-utils/contracts/helpers/WordCodec.sol";

// This is the contract that is actually verified; it may contain some helper
// methods for the spec to access internal state, or may override some of the
// more complex methods in the original contract.
contract WordCodecHarness is WordCodec{
//    using WordCodec for *;
}
