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
    // _validateEncodingParams(uint256,uint256,uint256) envfree
    // _validateEncodingParams(int256,uint256,uint256) envfree
}

// needs reworking
rule doesNotRevertImproperly() {
    method f; env e; calldataarg args;
    require e.msg.value == 0;
    // when we call our methods, if they revert it is only because they called _validateEncodingParams which reverted
    // e.g. when f == insertUint
    // f calls _validateEncodingParams
    // if _validateEncodingParams reverts, store that result, 
    // then when f reverts, make sure _validateEncodingParams had also reverted
    f@withrevert(e, args);
    
    assert !lastReverted, "wordCodec method calls must not revert improperly";
}

//// # Integrity ///////////////////////////////////////////////////////////////

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
        require offset < 256;
        bytes32 newWord = insertBool(word, boolValue, offset);
        bool decodedValue = decodeBool(newWord, offset);
        return boolValue == decodedValue;
    }
    else {
        // require false;
        return false;
    }
}

rule codecIntegrity() {
    method f; bytes32 word; uint256 offset; uint256 bitLength;

    bool identity = placeDecodeValue(f, word, offset, bitLength);

    assert identity, 
        "placing and decoding a value must return the original value";
}

rule uintInsertDecodeIntegrity() {
    bytes32 word; uint256 startingValue; uint256 offset; uint256 bitLength;

    bytes32 newWord = insertUint(word, startingValue, offset, bitLength);
    uint256 decodedValue = decodeUint(newWord, offset, bitLength);

    assert startingValue == decodedValue, 
        "Inserting and decoding a uint must return the original value";
}

rule intInsertDecodeIntegrity() {
    bytes32 word; int256 startingValue; uint256 offset; uint256 bitLength;

    bytes32 newWord = insertInt(word, startingValue, offset, bitLength);
    int256 decodedValue = decodeInt(newWord, offset, bitLength);

    assert startingValue == decodedValue, 
        "Inserting and decoding an int must return the original value";
}

rule uintEncodeDecodeIntegrity() {
    uint256 startingValue; uint256 offset; uint256 bitLength;

    bytes32 newWord = encodeUint(startingValue, offset, bitLength);
    uint256 decodedValue = decodeUint(newWord, offset, bitLength);

    assert startingValue == decodedValue, 
        "Encoding and decoding a uint must return the original value";
}

rule intEncodeDecodeIntegrity() {
    int256 startingValue; uint256 offset; uint256 bitLength;

    bytes32 newWord = encodeInt(startingValue, offset, bitLength);
    int256 decodedValue = decodeInt(newWord, offset, bitLength);

    assert startingValue == decodedValue, 
        "Encoding and decoding a uint must return the original value";
}

// add @dev comment regarding offset
rule boolInsertDecodeIntegrity() {
    bytes32 word; bool startingValue; uint256 offset;
    // require offset < 256;
    bytes32 newWord = insertBool(word, startingValue, offset);
    bool decodedValue = decodeBool(newWord, offset);

    assert startingValue == decodedValue, 
        "Inserting and decoding a bool must return the original value";
}

//// # Bit Independence ////////////////////////////////////////////////////////

rule uintInsertBitIndependence() {
    bytes32 word; uint256 bitOffset;
    bool _bitValue = decodeBool(word, bitOffset);

    uint256 offset; uint256 bitLength;
    bytes32 newWord = insertUint(word, _, offset, bitLength);

    bool bitValue_ = decodeBool(newWord, bitOffset);

    // bitOffset of a changed bit can be as small as offset but may not reach 
    // offset + bitLength
    assert _bitValue != bitValue_ => (offset <= bitOffset && bitOffset < (offset + bitLength)),
        "If a bit changes value, it must be within the correct range";
}

// check logic during daytime
rule boolInsertBitIndependence() {
    bytes32 word; uint256 bitOffset;
    bool _bitValue = decodeBool(word, bitOffset);

    uint256 offset;
    bytes32 newWord = insertBool(word, _, offset);

    bool bitValue_ = decodeBool(newWord, bitOffset);

    assert _bitValue != bitValue_ => bitOffset == offset,
        "If a bit changes value, it must be within the correct range";
}

//// # Method Equivalence //////////////////////////////////////////////////////


// Shelving this rule for now to try a simpler approach

// (5) decode section of word, insert arbitrary value into section of word, insert decoded value into section, 
// check to see that original word and new word are same
// (4) Encoding a uint and |ing it with a word having zeros in the right range is eq to inserting that uint
// bytes32 word
// require word[range] == 000000 (idea)
// require decodeUint(word, value, offset) == 0 (possible syntax)
// (3) try Armen approach w 2 x casting functions in harness (easy but ugly)
// (2) try casting things to uint256 and compare uint words to each other in assert
// (1) cvl syntax is to_uint256() look for bytes32 analog [to_bytes32()?]

// This rule relies heavily on logic from insertUint in the path for encodeUint.
// Consider alternate approaches if possible.
// rule uintInsertEncodeEquivalence() {
//     bytes32 word; uint256 value; uint256 offset; uint256 bitLength;

//     // moving value into word using insertUint
//     bytes32 wordA = insertUint(word, value, offset, bitLength);

//     // moving value into word using encodeUint
//     bytes32 valueWord = encodeUint(value, offset, bitLength);
//     uint256 mask = (1 << bitLength) - 1;
//     bytes32 preparedWord = bytes32(uint256(word) & ~(mask << offset));
//     bytes32 wordB = preparedWord | valueWord;

//     assert wordA == wordB, 
//         "Encoding a uint and moving the appropriate values into a given word must yield the same result as inserting the uint into that same word";
// }


rule uintEncodeInsertZeroWordEquivalence() {
    uint256 value; uint256 offset; uint256 bitLength;

    bytes32 zeroWord = 0;
    bytes32 wordA = insertUint(zeroWord, value, offset, bitLength);

    bytes32 wordB = encodeUint(value, offset, bitLength);

    assert wordA == wordB, 
        "Inserting a value into an empty word must yield the same result as encoding that value";
}

// calling twice

// try to generalize bit independence functions with CVL function / semi-
// parametric rule

// new rule(s) to make sure encode uint/int do not alter word outside correct
// range

// new rule to ensure insert uint/int does same as encode uint/int then | with other

// rule to show decoding from 0 gives 0

// consider rules for 192 method
