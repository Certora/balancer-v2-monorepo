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

rule insertUintIntegrity() {
    bytes32 word;
    uint256 value;
    uint256 offset;
    uint256 bitLength;
    assert false, 
        "TODO: Replace placeholder assert message";
}

rule insertIntIntegrity() {
    bytes32 word;
    int256 value;
    uint256 offset;
    uint256 bitLength;
    assert false, 
        "TODO: Replace placeholder assert message";
}

rule encodeUintIntegrity() {
    uint256 value;
    uint256 offset;
    uint256 bitLength;
    assert false, 
        "TODO: Replace placeholder assert message";
}

rule encodeIntIntegrity() {
    int256 value;
    uint256 offset;
    uint256 bitLength;
    assert false, 
        "TODO: Replace placeholder assert message";
}

rule decodeUintIntegrity() {
    bytes32 word;
    uint256 offset;
    uint256 bitLength;
    assert false, 
        "TODO: Replace placeholder assert message";
}

rule decodeIntIntegrity() {
    bytes32 word;
    uint256 offset;
    uint256 bitLength;
    assert false, 
        "TODO: Replace placeholder assert message";
}

rule decodeBoolIntegrity() {
    bytes32 word;
    uint256 offset;
    assert false, 
        "TODO: Replace placeholder assert message";
}

rule insertBits192Integrity() {
    bytes32 word;
    bytes32 value;
    uint256 offset;
    assert false, 
        "TODO: Replace placeholder assert message";
}

rule insertBoolIntegrity() {
    bytes32 word;
    bool value;
    uint256 offset;
    assert false, 
        "TODO: Replace placeholder assert message";
}

rule doesNotRevertImproperly() {
    method f; env e; calldataarg args;
    require e.msg.value == 0;

    f@withrevert(e, args);

    assert !lastReverted, "wordCodec method calls must not revert improperly";
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

rule boolInsertDecodeIntegrity() {
    bytes32 word; bool _value; uint256 offset;
    // require offset < 256;
    bytes32 newWord = insertBool(word, _value, offset);
    bool value_ = decodeBool(newWord, offset);

    assert _value == value_, 
        "Inserting and decoding a bool must return the original value";
}

rule uintInsertBitIndependence() {
    bytes32 word; uint256 bitOffset;
    // require bitOffset < 256;
    bool _bitValue = decodeBool(word, bitOffset);

    uint256 offset; uint256 bitLength;
    bytes32 newWord = insertUint(word, _, offset, bitLength);

    bool bitValue_ = decodeBool(newWord, bitOffset);

    assert _bitValue != bitValue_ => ((offset + bitLength) > bitOffset && bitOffset >= offset),
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
