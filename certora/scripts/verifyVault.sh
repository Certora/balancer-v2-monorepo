if [[ "$1" ]]
then
    RULE="--rule $1"
fi

certoraRun \
    certora/harnesses/VaultHarness.sol certora/helpers/DummyERC20Impl.sol \
    certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol \
    --verify VaultHarness:certora/specs/Vault.spec \
    --staging \
    --cache balancer \
    --optimistic_loop \
    --send_only \
    --msg "VaultHarness: $1"
