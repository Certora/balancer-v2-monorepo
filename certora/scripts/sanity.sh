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

