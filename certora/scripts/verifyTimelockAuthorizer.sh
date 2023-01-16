if [[ "$1" ]]
then
    RULE="--rule $1"
fi

if [[ "$2" ]]
then
    MSG="- $2"
fi

certoraRun  certora/munged/vault/contracts/authorizer/TimelockAuthorizer.sol \
    certora/munged/vault/contracts/authorizer/TimelockExecutor.sol \
    certora/munged/pool-utils/contracts/test/MockVault.sol \
    certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol \
    --verify TimelockAuthorizer:certora/spec/timelockAuthorizer.spec \
    --link TimelockAuthorizer:_vault=MockVault \
            TimelockAuthorizer:_executor=TimelockExecutor \
    --solc solc7.1 \
    --staging master \
    --optimistic_loop \
    --send_only \
    --packages @balancer-labs=node_modules/@balancer-labs \
    $RULE \
    --msg "TimelockAuthorizer: $RULE $MSG"