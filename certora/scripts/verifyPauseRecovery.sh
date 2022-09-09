if [[ "$1" ]]
then
    RULE="--rule $1"
fi
certoraRun \
    certora/harnesses/StablePoolRSHarness.sol \
    certora/harnesses/StableMathHarness.sol:StableMath \
    certora/helpers/DummyERC20Impl.sol \
    certora/helpers/DummyERC20A.sol \
    certora/helpers/DummyERC20B.sol \
    certora/helpers/DummyERC20C.sol \
    certora/helpers/DummyERC20D.sol \
    certora/helpers/DummyERC20E.sol \
    --link StablePoolRSHarness:_token0=DummyERC20A StablePoolRSHarness:_token1=DummyERC20B StablePoolRSHarness:_token2=DummyERC20C StablePoolRSHarness:_token3=DummyERC20D StablePoolRSHarness:_token4=DummyERC20E \
    --verify StablePoolRSHarness:certora/specs/PauseRecovery.spec \
    --staging \
    --settings -enableEqualitySaturation=false \
    --cache balancer \
    --optimistic_loop \
    --loop_iter 2 \
    --send_only \
    --solc solc7.1 \
    $RULE \
    --msg "StablePoolRS: $1" \

