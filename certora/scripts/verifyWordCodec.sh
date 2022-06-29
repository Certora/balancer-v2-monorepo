make -C certora munged

certoraRun \
    certora/harness/WordCodecHarness.sol \
    --verify WordCodecHarness:certora/spec/WordCodec.spec \
    --solc solc7.1 \
    --cache balancer \
    --optimistic_loop \
    --loop_iter 3 \
    --send_only \
    --cloud \
    --settings -useBitVectorTheory \
    --msg "WordCodec verification all rules"