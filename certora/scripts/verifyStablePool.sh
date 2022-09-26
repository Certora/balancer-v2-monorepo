if [[ "$1" ]]
then
    RULE="--rule $1"
fi

certoraRun \
    certora/harnesses/StablePoolHarness.sol \
    certora/helpers/DummyERC20A.sol \
    certora/helpers/DummyERC20B.sol \
    --link StablePoolHarness:_token0=DummyERC20A StablePoolHarness:_token1=DummyERC20B \
    --verify StablePoolHarness:certora/specs/StablePool.spec \
    --settings -enableEqualitySaturation=false \
    --solc solc7.1 \
    --cache balancerOld \
    --staging \
    --optimistic_loop \
    --loop_iter 2 \
    --send_only \
    $RULE \
    --msg "StablePool require sender: $1" \

