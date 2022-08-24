# make -C munged

if [[ "$1" ]]
then
    RULE="--rule $1"
fi
certoraRun \
    certora/harnesses/ComposableStablePoolHarness.sol \
    certora/helpers/DummyERC20A.sol \
    certora/helpers/DummyERC20B.sol \
    certora/helpers/DummyERC20C.sol \
    certora/helpers/DummyERC20D.sol \
    certora/helpers/DummyERC20E.sol \
    certora/helpers/DummyERC20F.sol \
    certora/harnesses/VaultHarness.sol \
    --link ComposableStablePoolHarness:_vault=VaultHarness \
    --verify ComposableStablePoolHarness:certora/specs/ComposableStablePool.spec \
    --address ComposableStablePoolHarness:0xce4604a0000000000000000000000062 \
    DummyERC20A:0xce4604a000000000000000000000005c \
    DummyERC20B:0xce4604a0000000000000000000000060 \
    DummyERC20C:0xce4604a0000000000000000000000064 \
    DummyERC20D:0xce4604a0000000000000000000000068 \
    DummyERC20E:0xce4604a000000000000000000000006c \
    DummyERC20F:0xce4604a0000000000000000000000070 \
    --link ComposableStablePoolHarness:_token0=DummyERC20A \
    --link ComposableStablePoolHarness:_token1=DummyERC20B \
    --link ComposableStablePoolHarness:_token2=ComposableStablePoolHarness \
    --link ComposableStablePoolHarness:_token3=DummyERC20D \
    --link ComposableStablePoolHarness:_token4=DummyERC20E \
    --link ComposableStablePoolHarness:_token5=DummyERC20F \
    --staging \
    --optimistic_loop \
    --loop_iter 3 \
    $RULE \
    --send_only \
    --msg "ComposableStablePool: $1 $2" \
    --solc solc7.3 \
    --settings -enableEqualitySaturation=false \
    --settings -s=z3 \
    --packages @balancer-labs=node_modules/@balancer-labs \
    --solc_args "['--optimize', '--optimize-runs', '200']" \
    --path ./
    # --packages @balancer-labs=/mnt/c/Users/YufeiLi/Desktop/sms/certora/ComposableStablePool/node_modules/@balancer-labs
    # --packages_path node_modules
    # --packages_path /mnt/c/Users/YufeiLi/Desktop/sms/certora/ComposableStablePool/node_modules
    # --packages @balancer-labs=/mnt/c/Users/YufeiLi/Desktop/sms/certora/ComposableStablePool/node_modules/@balancer-labs
    # --settings -enableEqualitySaturation=false
    # , -Dverbose.times
    # --link ComposableStablePoolHarness:_token0=DummyERC20A \
    # --link ComposableStablePoolHarness:_token1=DummyERC20B \
    # --link ComposableStablePoolHarness:_token2=ComposableStablePoolHarness \
    # --link ComposableStablePoolHarness:_token3=DummyERC20D \
    # --link ComposableStablePoolHarness:_token4=DummyERC20E \
    # --link ComposableStablePoolHarness:_token5=DummyERC20F \
#  -showInternalFunctions,
    
