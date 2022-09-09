# if [[ "$1" ]]
# then
#     RULE="--rule $1"
# fi

make -C munged

certoraRun \
    certora/harnesses/StablePoolHarness.sol \
    certora/helpers/DummyERC20Impl.sol \
    certora/helpers/DummyERC20A.sol \
    certora/helpers/DummyERC20B.sol \
    certora/helpers/DummyERC20C.sol \
    certora/helpers/DummyERC20D.sol \
    certora/helpers/DummyERC20E.sol \
    --link StablePoolHarness:_token0=DummyERC20A StablePoolHarness:_token1=DummyERC20B StablePoolHarness:_token2=DummyERC20C StablePoolHarness:_token3=DummyERC20D StablePoolHarness:_token4=DummyERC20E \
    --verify StablePoolHarness:certora/specs/AmplificationFactor.spec \
    --settings -enableEqualitySaturation=false \
    --cache balancer \
    --optimistic_loop \
    --loop_iter 2 \
    --send_only \
    --solc solc7.1 \
    --msg "StablePool: $2" \
    # --rule_sanity \

    # $RULE \