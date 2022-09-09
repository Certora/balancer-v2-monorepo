if [[ "$1" ]]
then
    RULE="--rule $1"
fi
certoraRun \
    certora/harnesses/ComposableStablePoolHarness.sol \
    certora/helpers/DummyERC20A.sol \
    certora/helpers/DummyERC20B.sol \
    --link ComposableStablePoolHarness:_token0=DummyERC20A \
    --link ComposableStablePoolHarness:_token1=DummyERC20B \
    --link ComposableStablePoolHarness:_token2=ComposableStablePoolHarness \
    --verify ComposableStablePoolHarness:certora/specs/pauseRecovery.spec \
    --staging \
    --settings -enableEqualitySaturation=false \
    --optimistic_loop \
    --loop_iter 3 \
    --send_only \
    $RULE \
    --msg "CSP: $1 $2" \
    --solc solc7.3 