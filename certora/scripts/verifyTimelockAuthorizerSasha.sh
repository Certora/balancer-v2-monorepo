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
    certora/harness/SingletonAuthenticationHarness.sol \
    certora/helpers/Receiver.sol \
    --verify TimelockAuthorizerHarness:certora/spec/CVL2/timelockAuthorizerSasha.spec \
    --link TimelockAuthorizerHarness:_vault=Vault \
            TimelockAuthorizerHarness:_executionHelper=TimelockExecutionHelper \
            TimelockExecutionHelper:_authorizer=TimelockAuthorizerHarness \
            SingletonAuthenticationHarness:_vault=Vault \
    --solc solc7.1 \
    --staging shelly/manifold \
    --optimistic_loop \
    --loop_iter 8 \
    --send_only \
    --rule_sanity \
    --settings -optimisticUnboundedHashing=true,-mediumTimeout=20,-adaptiveSolverConfig=false \
    --packages @balancer-labs=node_modules/@balancer-labs \
    $RULE \
    --msg "TimelockAuthorizerSasha: $RULE $MSG"
