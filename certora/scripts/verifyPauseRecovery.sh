if [[ "$1" ]]
then
    RULE="--rule $1"
fi
certoraRun \
    certora/harnesses/ComposableStablePoolHarness.sol \
    certora/helpers/DummyERC20A.sol \
    certora/helpers/DummyERC20B.sol \
    certora/harnesses/VaultHarness.sol \
    --address ComposableStablePoolHarness:0xce4604a0000000000000000000000062 \
    DummyERC20A:0xce4604a000000000000000000000005c \
    DummyERC20B:0xce4604a0000000000000000000000060 \
    --link ComposableStablePoolHarness:_token0=DummyERC20A \
    --link ComposableStablePoolHarness:_token1=DummyERC20B \
    --link ComposableStablePoolHarness:_token2=ComposableStablePoolHarness \
    --link ComposableStablePoolHarness:_vault=VaultHarness \
    --verify ComposableStablePoolHarness:certora/specs/pauseRecovery.spec \
    --staging \
    --settings -enableEqualitySaturation=false \
    --settings -divideNoRemainder=true \
    --optimistic_loop \
    --loop_iter 3 \
    --send_only \
    $RULE \
    --rule_sanity \
    --msg "CSP: PauseRecovery $1 $2" \
    --solc solc7.3
