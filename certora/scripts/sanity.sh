make -C certora munged

certoraRun \
    certora/munged/pool-stable/contracts/StablePool.sol \
    --verify StablePool:certora/specs/sanity.spec \
    --optimistic_loop \
    --loop_iter 3 \
    --staging \
    --cache balancer \
    --send_only \
    --msg "Stable Pool sanity nondet all, more phantom"


certoraRun \
   certora/munged/pool-stable-phantom/contracts/StablePhantomPool.sol \
   --verify StablePhantomPool:certora/specs/sanity.spec \
   --optimistic_loop \
   --loop_iter 3 \
   --staging \
   --send_only \
   --msg "Phantom Stable Pool sanity nondet all, more summaries"


certoraRun \
    certora/harnesses/WordCodecHarness.sol \
    --verify WordCodecHarness:certora/specs/sanity.spec \
    --solc solc7.1 \
    --optimistic_loop \
    --loop_iter 3 \
    --cache balancer \
    --settings -useBitVectorTheory \
    --send_only \
    --msg "WordCodec sanity"