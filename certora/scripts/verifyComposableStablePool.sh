make -C munged

if [[ "$1" ]]
then
    RULE="--rule $1"
fi
certoraRun \
    certora/harnesses/ComposableStablePoolHarness.sol \
    certora/harnesses/VaultHarness.sol \
    certora/helpers/DummyERC20Impl.sol \
    certora/helpers/DummyERC20A.sol \
    certora/helpers/DummyERC20B.sol \
    certora/helpers/DummyERC20C.sol \
    certora/helpers/DummyERC20D.sol \
    certora/helpers/DummyERC20E.sol \
    certora/helpers/DummyERC20F.sol \
    certora/helpers/DummyERC20F.sol \
    --link ComposableStablePoolHarness:_token0=DummyERC20A ComposableStablePoolHarness:_token1=DummyERC20B ComposableStablePoolHarness:_token2=DummyERC20C ComposableStablePoolHarness:_token3=DummyERC20D ComposableStablePoolHarness:_token4=DummyERC20E ComposableStablePoolHarness:_token5=DummyERC20F \
    ComposableStablePoolHarness:_vault=VaultHarness \
    --verify ComposableStablePoolHarness:certora/specs/ComposableStablePool.spec \
    --cache balancer \
    --staging \
    --optimistic_loop \
    --loop_iter 3 \
    --send_only \
    $RULE \
    --msg "ComposableStablePool: $1" \
    --solc solc7.3 \
    --solc_args "['--optimize', '--optimize-runs', '200']" \
    --settings -showInternalFunctions,-globalTimeout=18000 \
    --packages @balancer-labs=node_modules/@balancer-labs
    # --packages @balancer-labs=/mnt/c/Users/YufeiLi/Desktop/sms/certora/ComposableStablePool/node_modules/@balancer-labs
    # --packages_path node_modules
    # --packages_path /mnt/c/Users/YufeiLi/Desktop/sms/certora/ComposableStablePool/node_modules
    # --packages @balancer-labs=/mnt/c/Users/YufeiLi/Desktop/sms/certora/ComposableStablePool/node_modules/@balancer-labs
    # --settings -enableEqualitySaturation=false
    # , -Dverbose.times
