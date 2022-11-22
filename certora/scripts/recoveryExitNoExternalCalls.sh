certoraRun \
    certora/harnesses/ComposableStablePoolHarness.sol \
    certora/harnesses/VaultHarness.sol \
    --verify ComposableStablePoolHarness:certora/specs/recoveryExitNoExternalCalls.spec \
    --settings -enableEqualitySaturation=false \
    --optimistic_loop \
    --loop_iter 3 \
    --send_only \
    --rule_sanity \
    --msg "CSP: exitNoExternalCalls $1" \
    --solc solc7.1