if [[ "$1" ]]
then
    RULE="--rule $1"
fi
certoraRun \
    certora/harnesses/StablePoolHarness.sol \
    certora/helpers/DummyERC20Impl.sol \
    certora/helpers/DummyERC20A.sol \
    certora/helpers/DummyERC20B.sol\
    pkg/vault/contracts/Vault.sol \
    pkg/vault/contracts/VaultAuthorization.sol \
    --link StablePool:vault=Vault \
    --verify StablePoolHarness:certora/specs/StablePool.spec \
    --staging \
    --cache balancer \
    --optimistic_loop \
    --loop_iter 3 \
    --send_only --solc solc7.1\
    $RULE \
    --msg "Pool Registry with simplification andd loop 3: $1"


