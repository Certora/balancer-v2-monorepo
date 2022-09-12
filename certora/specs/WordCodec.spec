methods {
    insertUint(bytes32,uint256,uint256,uint256) returns bytes32 envfree
    insertInt(bytes32,int256,uint256,uint256) returns bytes32 envfree
    encodeUint(uint256,uint256,uint256) returns bytes32 envfree
    encodeInt(int256,uint256,uint256) returns bytes32 envfree
    decodeUint(bytes32,uint256,uint256) returns uint256 envfree
    decodeInt(bytes32,uint256,uint256) returns int256 envfree
    decodeBool(bytes32,uint256) returns bool envfree
    insertBits192(bytes32,bytes32,uint256) returns bytes32 envfree
    insertBool(bytes32,bool,uint256) returns bytes32 envfree
    validateEncodingParamsUint(uint256,uint256,uint256) envfree
    validateEncodingParamsInt(int256,uint256,uint256) envfree
}


// needs reworking
// TODO remove rule
rule doesNotRevert() {
    method f; env e; calldataarg args;
    require e.msg.value == 0;

    f@withrevert(e, args);
    assert !lastReverted, "wordCodec method calls must not revert TODO remove rule";
}

/// Calls each contract method with the appropriate args. Returns lastReverted.
function callWithArgs(method f, uint256 value, uint256 offset, uint256 bitLength) returns bool {
    if (f.selector == insertUint(bytes32,uint256,uint256,uint256).selector) {

        insertUint@withrevert(_, value, offset, bitLength);
        return lastReverted;
    }    
    if (f.selector == insertInt(bytes32,int256,uint256,uint256).selector) {

        insertInt@withrevert(_, to_int256(value), offset, bitLength);
        return lastReverted;
    }
    if (f.selector == encodeUint(uint256,uint256,uint256).selector) {

        encodeUint@withrevert(value, offset, bitLength);
        return lastReverted;
    }
    if (f.selector == encodeInt(int256,uint256,uint256).selector) {

        encodeInt@withrevert(to_int256(value), offset, bitLength);
        return lastReverted;
    }
    // TODO for all methods
    else {
        // assert false, "TODO other funcs not implemented";
        require false;
        return false;
    }
}

/// Returns lastReverted for validation of appropriate contract methods. Returns false for other methods.
function validateWithArgs(method f, uint256 value, uint256 offset, uint256 bitLength) returns bool {
    if (f.selector == insertUint(bytes32,uint256,uint256,uint256).selector) {

        validateEncodingParamsUint@withrevert(value, offset, bitLength);
        return lastReverted;
    }
    if (f.selector == insertInt(bytes32,int256,uint256,uint256).selector) {

        validateEncodingParamsInt@withrevert(to_int256(value), offset, bitLength);
        return lastReverted;
    }
    if (f.selector == encodeUint(uint256,uint256,uint256).selector) {

        validateEncodingParamsUint@withrevert(value, offset, bitLength);
        return lastReverted;
    }
    if (f.selector == encodeInt(int256,uint256,uint256).selector) {

        validateEncodingParamsInt@withrevert(to_int256(value), offset, bitLength);
        return lastReverted;
    }
    // TODO for all methods
    else {
        // assert false, "TODO other funcs not implemented";
        require false;
        return false;
    }
}

/// wordCodec method calls must not revert improperly.
rule doesNotRevertImproperly() {
    method f; uint256 value; uint256 offset; uint256 bitLength;
    bool mainReverted = callWithArgs(f, value, offset, bitLength);

    bool validateReverted = validateWithArgs(f, value, offset, bitLength);

    assert mainReverted => validateReverted, 
        "wordCodec method calls must not revert improperly";
}

//// # Integrity ///////////////////////////////////////////////////////////////

// All rules implemented
// all except bool integrity passing
// Redundant rules

/// Returns integrity of each placing-decoding method pair.
function placeDecodeValue(method f, bytes32 word, uint256 offset, uint256 bitLength) returns bool {
    if (f.selector == insertUint(bytes32,uint256,uint256,uint256).selector) {
        uint256 uintValue;
        bytes32 newWord = insertUint(word, uintValue, offset, bitLength);
        uint256 decodedValue = decodeUint(newWord, offset, bitLength);
        return uintValue == decodedValue;
    }
    else if (f.selector == insertInt(bytes32,int256,uint256,uint256).selector) {
        int256 intValue;
        bytes32 newWord = insertInt(word, intValue, offset, bitLength);
        int256 decodedValue = decodeInt(newWord, offset, bitLength);
        return intValue == decodedValue;
    }
    else if (f.selector == encodeUint(uint256,uint256,uint256).selector) {
        uint256 uintValue;
        bytes32 newWord = encodeUint(uintValue, offset, bitLength);
        uint256 decodedValue = decodeUint(newWord, offset, bitLength);
        return uintValue == decodedValue;
    }
    else if (f.selector == encodeInt(int256,uint256,uint256).selector) {
        int256 intValue;
        bytes32 newWord = encodeInt(intValue, offset, bitLength);
        int256 decodedValue = decodeInt(newWord, offset, bitLength);
        return intValue == decodedValue;
    }
    else if (f.selector == insertBool(bytes32,bool,uint256).selector) {
        bool boolValue;
        // require offset < 256;
        bytes32 newWord = insertBool(word, boolValue, offset);
        bool decodedValue = decodeBool(newWord, offset);
        return boolValue == decodedValue;
    }
    else {
        require false; // constrains search to only above methods
        return true; // avoids compiler errors
    }
}

/// Placing and decoding a value must return the original value.
/// @dev an offset greater than 255 breaks bool insert-decode integrity (always returns the original word for insertBool and always returns false for decodeBool)
rule codecIntegrity() {
    method f; bytes32 word; uint256 offset; uint256 bitLength;

    bool identity = placeDecodeValue(f, word, offset, bitLength);

    assert identity, 
        "placing and decoding a value must return the original value";
}

/// Inserting and decoding a uint must return the original value.
rule uintInsertDecodeIntegrity() {
    bytes32 word; uint256 startingValue; uint256 offset; uint256 bitLength;

    bytes32 newWord = insertUint(word, startingValue, offset, bitLength);
    uint256 decodedValue = decodeUint(newWord, offset, bitLength);

    assert startingValue == decodedValue, 
        "inserting and decoding a uint must return the original value";
}

/// Inserting and decoding an int must return the original value.
rule intInsertDecodeIntegrity() {
    bytes32 word; int256 startingValue; uint256 offset; uint256 bitLength;

    bytes32 newWord = insertInt(word, startingValue, offset, bitLength);
    int256 decodedValue = decodeInt(newWord, offset, bitLength);

    assert startingValue == decodedValue, 
        "inserting and decoding an int must return the original value";
}

/// Encoding and decoding a uint must return the original value.
rule uintEncodeDecodeIntegrity() {
    uint256 startingValue; uint256 offset; uint256 bitLength;

    bytes32 newWord = encodeUint(startingValue, offset, bitLength);
    uint256 decodedValue = decodeUint(newWord, offset, bitLength);

    assert startingValue == decodedValue, 
        "encoding and decoding a uint must return the original value";
}

/// Encoding and decoding an int must return the original value.
rule intEncodeDecodeIntegrity() {
    int256 startingValue; uint256 offset; uint256 bitLength;

    bytes32 newWord = encodeInt(startingValue, offset, bitLength);
    int256 decodedValue = decodeInt(newWord, offset, bitLength);

    assert startingValue == decodedValue, 
        "encoding and decoding an int must return the original value";
}

/// Inserting and decoding a bool must return the original value.
/// @dev an offset greater than 255 breaks bool insert-decode integrity (always returns the original word for insertBool and always returns false for decodeBool)
rule boolInsertDecodeIntegrity() {
    bytes32 word; bool startingValue; uint256 offset;
    // require offset < 256;
    bytes32 newWord = insertBool(word, startingValue, offset);
    bool decodedValue = decodeBool(newWord, offset);

    assert startingValue == decodedValue, 
        "inserting and decoding a bool must return the original value";
}

//// # Bit Independence / Constraint ///////////////////////////////////////////

// 6/6 rules implemented
// Documentation needed
// 6/6 passing

/// If a bit changes value after inserting a uint, it must be within the correct range.
rule uintInsertBitIndependence() {
    bytes32 word; uint256 bitOffset;
    bool _bitValue = decodeBool(word, bitOffset);

    uint256 offset; uint256 bitLength;
    bytes32 newWord = insertUint(word, _, offset, bitLength);

    bool bitValue_ = decodeBool(newWord, bitOffset);

    // bitOffset of a changed bit can be as small as offset but must remain
    // smaller than offset + bitLength
    assert _bitValue != bitValue_ => (offset <= bitOffset && bitOffset < (offset + bitLength)),
        "if a bit changes value after inserting a uint, it must be within the correct range";
}

/// If a bit is outside the correct range when encoding a uint, its value must be 0.
rule uintEncodeBitConstraint() {
    uint256 offset; uint256 bitLength;
    bytes32 newWord = encodeUint(_, offset, bitLength);

    uint256 bitOffset;
    bool bitValue = decodeBool(newWord, bitOffset);

    // bitOffsets are outside the encoding range when smaller than offset or 
    // when at least as large as offset + bitLength
    assert (bitOffset < offset || (offset + bitLength) <= bitOffset) => !bitValue, 
        "if a bit is outside the correct range when encoding a uint, its value must be 0";
}

/// If a bit changes value after inserting an int, it must be within the correct range.
rule intInsertBitIndependence() {
    bytes32 word; uint256 bitOffset;
    bool _bitValue = decodeBool(word, bitOffset);

    uint256 offset; uint256 bitLength;
    bytes32 newWord = insertInt(word, _, offset, bitLength);

    bool bitValue_ = decodeBool(newWord, bitOffset);

    // bitOffset of a changed bit can be as small as offset but must remain
    // smaller than offset + bitLength
    assert _bitValue != bitValue_ => (offset <= bitOffset && bitOffset < (offset + bitLength)),
        "if a bit changes value after inserting an int, it must be within the correct range";
}

/// If a bit is outside the correct range when encoding an int, its value must be 0.
rule intEncodeBitConstraint() {
    uint256 offset; uint256 bitLength;
    bytes32 newWord = encodeInt(_, offset, bitLength);

    uint256 bitOffset;
    bool bitValue = decodeBool(newWord, bitOffset);

    // bitOffsets are outside the encoding range when smaller than offset or 
    // when at least as large as offset + bitLength
    assert (bitOffset < offset || (offset + bitLength) <= bitOffset) => !bitValue, 
        "if a bit is outside the correct range when encoding an int, its value must be 0";
}

/// If a bit changes value after inserting a bool, it must have the correct offset.
rule boolInsertBitIndependence() {
    bytes32 word; uint256 bitOffset;
    bool _bitValue = decodeBool(word, bitOffset);

    uint256 offset;
    bytes32 newWord = insertBool(word, _, offset);

    bool bitValue_ = decodeBool(newWord, bitOffset);

    assert _bitValue != bitValue_ => bitOffset == offset,
        "if a bit changes value after inserting a bool, it must have the correct offset";
}

/// If a bit changes value after inserting with insertBits192, it must be within the correct range.
rule insertBits192BitIndependence() {
    bytes32 word; uint256 bitOffset;
    bool _bitValue = decodeBool(word, bitOffset);

    uint256 offset; bytes32 value;
    // insertBits192 assumes `value` can be represented using 192 bits
    require value < 2^192;
    bytes32 newWord = insertBits192(word, value, offset);

    bool bitValue_ = decodeBool(newWord, bitOffset);

    // bitOffset of a changed bit can be as small as offset but must remain
    // smaller than offset + 192
    assert _bitValue != bitValue_ => (offset <= bitOffset && bitOffset < (offset + 192)), 
        "if a bit changes value after inserting with insertBits192, it must be within the correct range";
}

//// # Method Equivalence //////////////////////////////////////////////////////

// 5/6 rules implemented
// 5/5 passing

/// Encoding a uint and moving the appropriate value into a given word must yield the same result as inserting the uint into that same word.
rule uintInsertEncodeEquivalence() {
    bytes32 slottedWord; uint256 value; uint256 offset; uint256 bitLength;
    // slottedWord has 0 in the appropriate range
    require decodeUint(slottedWord, offset, bitLength) == 0; 
    // valueWord has 0 everywhere outside the appropriate range
    bytes32 valueWord = encodeUint(value, offset, bitLength);
    // wordA should have no zeroed-out ranges
    bytes32 wordA = slottedWord | valueWord;
    // unslottedWord has the range filled with some other value
    uint256 tempValue;
    bytes32 unslottedWord = insertUint(slottedWord, tempValue, offset, bitLength);
    // wordB should also have no zeroed-out ranges
    bytes32 wordB = insertUint(unslottedWord, value, offset, bitLength);

    assert wordA == wordB, 
        "encoding a uint and moving the appropriate value into a given word must yield the same result as inserting the uint into that same word";
}

/// Inserting a uint into an empty word must yield the same result as encoding that uint.
rule uintEncodeInsertZeroWordEquivalence() {
    uint256 value; uint256 offset; uint256 bitLength;

    bytes32 zeroWord = 0;
    bytes32 wordA = insertUint(zeroWord, value, offset, bitLength);

    bytes32 wordB = encodeUint(value, offset, bitLength);

    assert wordA == wordB, 
        "inserting a uint into an empty word must yield the same result as encoding that uint";
}

/// Encoding an int and moving the appropriate value into a given word must yield the same result as inserting the int into that same word.
rule intInsertEncodeEquivalence() {
    bytes32 slottedWord; int256 value; uint256 offset; uint256 bitLength;
    // slottedWord has 0 in the appropriate range
    require decodeInt(slottedWord, offset, bitLength) == 0; 
    // valueWord has 0 everywhere outside the appropriate range
    bytes32 valueWord = encodeInt(value, offset, bitLength);
    // wordA should have no zeroed-out ranges
    bytes32 wordA = slottedWord | valueWord;
    // unslottedWord has the range filled with some other value
    int256 tempValue;
    bytes32 unslottedWord = insertInt(slottedWord, tempValue, offset, bitLength);
    // wordB should also have no zeroed-out ranges
    bytes32 wordB = insertInt(unslottedWord, value, offset, bitLength);

    assert wordA == wordB, 
        "encoding an int and moving the appropriate value into a given word must yield the same result as inserting the int into that same word";
}

/// Inserting an int into an empty word must yield the same result as encoding that int.
rule intEncodeInsertZeroWordEquivalence() {
    int256 value; uint256 offset; uint256 bitLength;

    bytes32 zeroWord = 0;
    bytes32 wordA = insertInt(zeroWord, value, offset, bitLength);

    bytes32 wordB = encodeInt(value, offset, bitLength);

    assert wordA == wordB, 
        "inserting an int into an empty word must yield the same result as encoding that int";
}

/// Inserting a 192 bit value using insertUint must yield the same result as using insertBits192.
rule uintInsertBits192InsertEquivalence() {
    bytes32 word; bytes32 value; uint256 offset;
    // insertBits192 assumes `value` can be represented using 192 bits
    require value < 2^192;
    bytes32 wordA = insertBits192(word, value, offset);

    bytes32 wordB = insertUint(word, to_uint256(value), offset, 192);

    assert wordA == wordB, 
        "inserting a 192 bit value using insertUint must yield the same result as using insertBits192";
}

// // TODO finish and choose. This approach starts with a bytes32 value
// rule intInsertBits192InsertEquivalenc1() {
//     bytes32 word; bytes32 value; uint256 offset;
//     // insertBits192 assumes `value` can be represented using 192 bits
//     require value < 2^192;
//     bytes32 wordA = insertBits192(word, value, offset);

//     bytes32 wordB = insertInt(word, to_int256(value), offset, 192);

//     assert wordA == wordB, 
//         "inserting a 192 bit value using insertInt must yield the same result as using insertBits192";
// }

// // TODO finish and choose. This approach starts with an int256 value
// rule intInsertBits192InsertEquivalence2() {
//     bytes32 word; int256 value; uint256 offset;
//     // insertBits192 assumes `value` can be represented using 192 bits
//     require value < 2^192;
//     // require value...
//     bytes32 wordA = insertBits192(word, bytes32(bytes24(value)), offset);

//     bytes32 wordB = insertInt(word, value, offset, 192);

//     assert wordA == wordB, 
//         "inserting a 192 bit value using insertInt must yield the same result as using insertBits192";
// }

//// # Decoding from Zero //////////////////////////////////////////////////////

// All rules implemented
// 2/3 passing, with known cause of failure for 3rd

/// Decoding a uint from a zero word must yield 0.
rule uintDecodeFromZero() {
    bytes32 zeroWord; uint256 offset; uint256 bitLength;
    require zeroWord == 0;

    uint256 value = decodeUint(zeroWord, offset, bitLength);

    assert value == 0,
        "decoding a uint from a zero word must yield 0";
}

/// Decoding an int from a zero word must yield 0.
/// @dev a bitLength of 0 yields a value of -1 instead of 0.
rule intDecodeFromZero() {
    bytes32 zeroWord; uint256 offset; uint256 bitLength;
    require zeroWord == 0;
    // require bitLength > 0;

    int256 value = decodeInt(zeroWord, offset, bitLength);

    assert value == 0,
        "decoding an int from a zero word must yield 0";
}
/// Decoding a bool from a zero word must yield false.
rule boolDecodeFromZero() {
    bytes32 zeroWord; uint256 offset;
    require zeroWord == 0;

    bool value = decodeBool(zeroWord, offset);

    assert !value,
        "decoding a bool from a zero word must yield false";
}

