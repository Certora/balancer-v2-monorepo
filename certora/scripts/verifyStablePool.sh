make -C munged

if [[ "$1" ]]
then
    RULE="--rule $1"
fi
certoraRun \
    certora/harnesses/StablePoolHarness.sol \
    certora/helpers/DummyERC20Impl.sol \
    certora/helpers/DummyERC20A.sol \
    certora/helpers/DummyERC20B.sol \
    certora/helpers/DummyERC20C.sol \
    certora/helpers/DummyERC20D.sol \
    certora/helpers/DummyERC20E.sol \
    --link StablePoolHarness:_token0=DummyERC20A StablePoolHarness:_token1=DummyERC20B StablePoolHarness:_token2=DummyERC20C StablePoolHarness:_token3=DummyERC20D StablePoolHarness:_token4=DummyERC20E \
    --verify StablePoolHarness:certora/specs/StablePool.spec \
    --settings -enableEqualitySaturation=false,-Dverbose.times \
    --cache balancer \
    --staging \
    --optimistic_loop \
    --loop_iter 3 \
    --send_only \
    $RULE \
    --msg "StablePool with linking vault: $1" \

