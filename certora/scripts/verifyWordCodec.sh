if [[ "$1" ]]
then
    RULE="--rule $1"
fi

make -C certora munged

certoraRun \
    certora/harnesses/WordCodecHarness.sol \
    --verify WordCodecHarness:certora/specs/WordCodec.spec \
    --solc solc7.1 \
    --cache balancer \
    --optimistic_loop \
    --loop_iter 3 \
    --send_only \
    --cloud \
    --settings -useBitVectorTheory \
    $RULE \
    --msg "WordCodec verification: $1" \
