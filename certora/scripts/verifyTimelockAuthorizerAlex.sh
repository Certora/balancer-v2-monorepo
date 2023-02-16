if [[ "$1" ]]
then
    RULE="--rule $1"
fi

if [[ "$2" ]]
then
    MSG="- $2"
fi

certoraRun  certora/harness/TimelockAuthorizerHarness.sol \
    certora/munged/vault/contracts/authorizer/TimelockExecutor.sol \
    certora/munged/vault/contracts/Vault.sol \
    certora/harness/AuthenticationHarness.sol \
    certora/helpers/Receiver.sol \
    certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol \
    --verify TimelockAuthorizerHarness:certora/spec/timelockAuthorizerAlex.spec \
    --link TimelockAuthorizerHarness:_vault=Vault \
            TimelockAuthorizerHarness:_executor=TimelockExecutor \
            TimelockExecutor:authorizer=TimelockAuthorizerHarness \
    --solc solc7.1 \
    --staging master \
    --optimistic_loop \
    --loop_iter 8 \
    --send_only \
    --rule_sanity basic \
    --settings -optimisticUnboundedHashing=true \
    --packages @balancer-labs=node_modules/@balancer-labs \
    $RULE \
    --msg "TimelockAuthorizer: $RULE $MSG"


    # --staging bgreenwald/cert-740 \
    # --staging EyalH/ShowCallTraceWrongIndex \