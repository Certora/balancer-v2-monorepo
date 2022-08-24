# make -C certora munged

# certoraRun \
#     certora/munged/pool-stable/contracts/StablePool.sol \
#     --verify StablePool:certora/specs/sanity.spec \
#     --optimistic_loop \
#     --loop_iter 3 \
#     --staging \
#     --cache balancer \
#     --send_only \
#     --msg "Stable Pool sanity nondet all, more phantom"


# certoraRun \
#    certora/munged/pool-stable-phantom/contracts/StablePhantomPool.sol \
#    --verify StablePhantomPool:certora/specs/sanity.spec \
#    --optimistic_loop \
#    --loop_iter 3 \
#    --staging \
#    --send_only \
#    --msg "Phantom Stable Pool sanity nondet all, more summaries"


# certoraRun \
#     certora/harnesses/WordCodecHarness.sol \
#     --verify WordCodecHarness:certora/specs/sanity.spec \
#     --solc solc7.1 \
#     --optimistic_loop \
#     --loop_iter 3 \
#     --cache balancer \
#     --settings -useBitVectorTheory \
#     --send_only \
#     --msg "WordCodec sanity"

if [[ "$1" ]]
then
    RULE="--rule $1"
fi
certoraRun \
    certora/munged/pool-stable/contracts/ComposableStablePool.sol \
    certora/helpers/DummyERC20A.sol \
    --verify ComposableStablePool:certora/specs/sanity.spec \
    --staging \
    --settings -enableEqualitySaturation=false,-simplificationDepth=10 \
    --optimistic_loop \
    --loop_iter 3 \
    $RULE \
    --send_only \
    --msg "ComposableStablePool query mutate actual norecovery initialized: $1" \
    --packages @balancer-labs=node_modules/@balancer-labs \


# --solc_args "['--optimize', '--optimize-runs', '200']" \
# ,-simplificationDepth=10 \