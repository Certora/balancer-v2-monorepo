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
    certora/harnesses/SymbolicVault.sol \
    --link StablePoolHarness:_vault=SymbolicVault \
    --verify StablePoolHarness:certora/specs/StablePool.spec \
    --staging \
    --cache balancer \
    --optimistic_loop \
    --loop_iter 3 \
    --solc solc7.0 \
    --send_only \
    $RULE \
    --msg "StablePool with linking vault: $1" \
    --debug


