import "erc20.spec"
import "timelockAuthorizerMain.spec"

rule sanity(env e, method f) {
    calldataarg args;
    f(e, args);
    assert false;
}


// STATUS - verified with workarounds explained on confluence
// Checking that hashing produces different outputs for different inputs
rule permissionCheck(env e, env e2) {
    bytes32 actionId1;
    address account1;
    address where1;

    bytes32 actionId2;
    address account2;
    address where2;

    bytes32 permission1;
    bytes32 permission2;

    permission1 = getPermissionId(actionId1, account1, where1);
    permission2 = getPermissionId(actionId2, account2, where2);

    assert (actionId1 != actionId2 || account1 != account2 || where1 != where2) => permission1 != permission2;
}


// STATUS - in progress (strange storage results: https://vaas-stg.certora.com/output/3106/57a10f4e5c1b41c5b1de883de54516a9/?anonymousKey=07ae614ca13ed4cffad1d6b423149c57f2c08814)
// executableAt is immutable
rule immutableExecuteAt(env e, method f) {
    uint256 actionIndex;

    uint256 executableAtBefore = getSchedExeExecutableAt(actionIndex);

    calldataarg args;
    f(e, args);

    uint256 executableAtAfter = getSchedExeExecutableAt(actionIndex);

    assert executableAtBefore == executableAtAfter;
}

// STATUS - in progress
// All the time there is only one address, that has root permissions and this address is currentRoot.
invariant theOnlyRoot(bytes32 actionId, address account1, address account2)
    (actionId == _GENERAL_GRANT_ACTION_ID()
        || actionId == _GENERAL_REVOKE_ACTION_ID())
    //     && _isPermissionGranted(getPermissionId(actionId, account1, EVERYWHERE())))
    // => account1 == _root()
    => _isPermissionGranted(getPermissionId(actionId, _root(), EVERYWHERE()))

    {
        preserved {
            requireInvariant matchingGenralActionIds();
        }
    }

    // ((actionId == getExtendedActionId(getActionId(getGrantActionId()), GENERAL_PERMISSION_SPECIFIER())
    //         || actionId == getExtendedActionId(getActionId(getRevokeActionId()), GENERAL_PERMISSION_SPECIFIER()))
    //     && _isPermissionGranted(getPermissionId(actionId, account1, EVERYWHERE())) 
    //     && _isPermissionGranted(getPermissionId(actionId, account2, EVERYWHERE())))
    // => account1 == account2 && account1 == _root()

// STATUS - in progress / verified / error / timeout / etc.
// TODO: rule description
rule basicFRule(env e, method f) {
    bytes32 actionId;

    require actionId == getExtendedActionId(getActionId(getGrantActionId()), GENERAL_PERMISSION_SPECIFIER())
                => _isPermissionGranted(getPermissionId(actionId, _root(), EVERYWHERE()));

    calldataarg args;
    f(e, args);

    assert actionId == getExtendedActionId(getActionId(getGrantActionId()), GENERAL_PERMISSION_SPECIFIER())
                => _isPermissionGranted(getPermissionId(actionId, _root(), EVERYWHERE()));
}

// STATUS - verified
// ensure that two ways to get ID mathc each other (saw before that it doesn't, needed to check)
invariant matchingGenralActionIds()
    _GENERAL_GRANT_ACTION_ID() == getExtendedActionId(getActionId(getGrantActionId()), GENERAL_PERMISSION_SPECIFIER())
    && _GENERAL_REVOKE_ACTION_ID() == getExtendedActionId(getActionId(getRevokeActionId()), GENERAL_PERMISSION_SPECIFIER())

// STATUS - in progress
// go over array, two the same action IDs, id with lower index should have lower or equal executableAt
// failing vacuous check: https://vaas-stg.certora.com/output/3106/19d7372700ca453f9d70f075ee13a73c/?anonymousKey=41665649305352d1003f370a810592b2a6d93bf9
invariant arrayHierarchy(env e, uint256 indexLow, uint256 indexHigh)
    indexLow < indexHigh && indexHigh < getSchedExeLength()
        // && getExecuteExecutionActionId(indexLow) == getExecuteExecutionActionId(indexHigh)
    => getSchedExeExecutableAt(indexLow) <= getSchedExeExecutableAt(indexHigh)

rule whoChangedBalanceOf(env eB, env eF, method f) {
    bytes32 actionId;
    calldataarg args;
    uint256 before = _delaysPerActionId(eB, actionId);
    f(eF, args);
    assert _delaysPerActionId(eF, actionId) == before, "balanceOf changed";
}