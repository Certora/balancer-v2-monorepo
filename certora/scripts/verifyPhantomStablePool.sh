if [[ "$1" ]]
then
    RULE="--rule $1"
fi
certoraRun \
    certora/harnesses/StablePhantomPoolHarness.sol certora/helpers/DummyERC20Impl.sol \
    certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol \
    --verify StablePhantomPoolHarness:certora/specs/PhantomStablePool.spec \
    --staging \
    --cache balancer \
    --optimistic_loop \
    --loop_iter 3 \
    --send_only \
    $RULE \
    --msg "PhantomStablePool test points_to warning: $1"
