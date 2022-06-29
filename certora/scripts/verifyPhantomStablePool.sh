if [[ "$1" ]]
then
    RULE="--rule $1"
fi
certoraRun \
    certora/harness/PoolRegistryHarness.sol certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol\
    --verify PoolRegistryHarness:certora/spec/PoolRegistry.spec \
    --staging \
    --cache balancer \
    --optimistic_loop \
    --loop_iter 3 \
    --send_only --solc solc\
    $RULE \
    --msg "Pool Registry with simplification andd loop 3: $1"