certoraRun \
    certora/munged/pool-linear/contracts/test/MockLinearPool.sol \
    --verify MockLinearPool:certora/spec/sanity.spec \
    --optimistic_loop \
    --loop_iter 3 \
    --send_only \
    --msg "Linear Pool sanity"

certoraRun \
    certora/munged/pool-stable/contracts/test/MockStablePool.sol \
    --verify MockStablePool:certora/spec/sanity.spec \
    --optimistic_loop \
    --loop_iter 3 \
    --send_only \
    --msg "Stable Pool sanity"

certoraRun \
    certora/munged/pool-stable-phantom/contracts/test/MockStablePhantomPool.sol \
    --verify MockStablePhantomPool:certora/spec/sanity.spec \
    --optimistic_loop \
    --loop_iter 3 \
    --send_only \
    --msg "Stable Phantom Pool sanity"

certoraRun \
    certora/munged/pool-weighted/contracts/test/MockWeightCompression.sol \
    --verify MockWeightCompression:certora/spec/sanity.spec \
    --optimistic_loop \
    --loop_iter 3 \
    --send_only \
    --msg "Weighted Pool sanity"