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
