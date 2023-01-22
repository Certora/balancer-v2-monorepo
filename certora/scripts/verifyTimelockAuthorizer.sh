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
    certora/munged/vault/contracts/Vault.sol \
    certora/harness/AuthenticationHarness.sol \
    certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol \
    --verify TimelockAuthorizer:certora/spec/timelockAuthorizer.spec \
    --link TimelockAuthorizer:_vault=Vault \
            TimelockAuthorizer:_executor=TimelockExecutor \
            TimelockExecutor:authorizer=TimelockAuthorizer \
    --solc solc7.1 \
    --staging EyalH/ShowCallTraceWrongIndex \
    --optimistic_loop \
    --loop_iter 3 \
    --send_only \
    --settings -optimisticUnboundedHashing=true \
    --packages @balancer-labs=node_modules/@balancer-labs \
    $RULE \
    --msg "TimelockAuthorizer: $RULE $MSG"


    # --staging bgreenwald/cert-740 \