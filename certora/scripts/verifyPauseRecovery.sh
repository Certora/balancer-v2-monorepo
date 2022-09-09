if [[ "$1" ]]
then
    RULE="--rule $1"
fi
certoraRun \
    certora/harnesses/ComposableStablePoolHarness.sol \
    certora/helpers/DummyERC20A.sol \
    certora/helpers/DummyERC20B.sol \
    certora/harnesses/VaultHarness.sol \
    --link ComposableStablePoolHarness:_token0=DummyERC20A \
    --link ComposableStablePoolHarness:_token1=DummyERC20B \
    --link ComposableStablePoolHarness:_token2=ComposableStablePoolHarness \
    --link ComposableStablePoolHarness:_vault=VaultHarness \
    --verify ComposableStablePoolHarness:certora/specs/pauseRecovery.spec \
    --staging \
    --settings -enableEqualitySaturation=false \
    --optimistic_loop \
    --loop_iter 3 \
    --send_only \
    $RULE \
    --rule_sanity \
    --msg "CSP: $1 $2" \
    --solc solc7.3