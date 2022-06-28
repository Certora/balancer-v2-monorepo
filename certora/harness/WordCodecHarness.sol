pragma solidity ^0.7.0;

import "../munged/solidity-utils/contracts/helpers/WordCodec.sol";

// This contract calls internal functions from the WordCodec library using 
// public wrapper functions.
contract WordCodecHarness {
    using WordCodec for *;

    // In-place insertion

    function insertUint_wrapper(
        bytes32 word,
        uint256 value,
        uint256 offset,
        uint256 bitLength
    ) public pure returns (bytes32) { // HARNESS: internal -> public
        return insertUint(word, value, offset, bitLength);
    }

    function insertInt_wrapper(
        bytes32 word,
        int256 value,
        uint256 offset,
        uint256 bitLength
    ) public pure returns (bytes32) { // HARNESS: internal -> public
        return insertInt(word, value, offset, bitLength);
    }

    // Encoding

    function encodeUint_wrapper(
        uint256 value,
        uint256 offset,
        uint256 bitLength
    ) public pure returns (bytes32) { // HARNESS: internal -> public
        return encodeUint(value, offset, bitLength);
    }

    function encodeInt_wrapper(
        int256 value,
        uint256 offset,
        uint256 bitLength
    ) public pure returns (bytes32) { // HARNESS: internal -> public
        return encodeInt(value, offset, bitLength);
    }

    // Decoding

    function decodeUint_wrapper(
        bytes32 word,
        uint256 offset,
        uint256 bitLength
    ) public pure returns (uint256) { // HARNESS: internal -> public
        return decodeUint(word, offset, bitLength);
    }

    function decodeInt_wrapper(
        bytes32 word,
        uint256 offset,
        uint256 bitLength
    ) public pure returns (int256) { // HARNESS: internal -> public
        return decodeInt(word, offset, bitLength);
    }

    // Special cases

    function decodeBool_wrapper(bytes32 word, uint256 offset) public pure returns (bool) { // HARNESS: internal -> public
        return decodeBool(word, offset);
    }

    function insertBits192_wrapper(
        bytes32 word,
        bytes32 value,
        uint256 offset
    ) public pure returns (bytes32) { // HARNESS: internal -> public
        return insertBits192(word, value, offset);
    }

    function insertBool_wrapper(
        bytes32 word,
        bool value,
        uint256 offset
    ) public pure returns (bytes32) { // HARNESS: internal -> public
        return insertBool(word, value, offset);
    }
}
