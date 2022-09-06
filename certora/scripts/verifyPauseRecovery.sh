if [[ "$1" ]]
then
    RULE="--rule $1"
fi
certoraRun \
    certora/harnesses/ComposableStablePoolHarness.sol \
    certora/helpers/DummyERC20A.sol \
    certora/helpers/DummyERC20B.sol \
    --link ComposableStablePoolHarness:_token0=DummyERC20A ComposableStablePoolHarness:_token1=DummyERC20B \
    --verify ComposableStablePoolHarness:certora/specs/pauseRecovery.spec \
    --staging \
    --settings -enableEqualitySaturation=false \
    --cache balancer \
    --optimistic_loop \
    --loop_iter 1 \
    --send_only \
    $RULE \
    --msg "CSP: $1 $2" \
    --solc solc7.3 