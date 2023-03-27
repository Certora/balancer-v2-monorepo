if [[ "$1" ]]
then
    RULE="--rule $1"
fi

if [[ "$2" ]]
then
    MSG="- $2"
fi

certoraRun  certora/harness/TimelockAuthorizerHarness.sol \
    certora/munged/vault/contracts/authorizer/TimelockExecutionHelper.sol \
    certora/munged/vault/contracts/Vault.sol \
    certora/helpers/Receiver.sol \
    --verify TimelockAuthorizerHarness:certora/spec/timelockAuthorizerAlex.spec \
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