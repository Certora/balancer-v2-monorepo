make -C certora munged

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
    certora/harness/WordCodecHarness.sol \
    --verify WordCodecHarness:certora/spec/sanity.spec \
    --solc solc7.0 \
    --optimistic_loop \
    --loop_iter 3 \
    --settings -useBitVectorTheory \
    --send_only \
    --msg "WordCodec sanity"