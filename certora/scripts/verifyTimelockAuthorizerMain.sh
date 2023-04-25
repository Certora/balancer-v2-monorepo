cd certora
touch applyHarness.patch
make munged
cd ..
echo "key length" ${#CERTORAKEY}

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
    --verify TimelockAuthorizerHarness:certora/spec/CVL2/timelockAuthorizerMain.spec \
    --link TimelockAuthorizerHarness:_vault=Vault \
            TimelockAuthorizerHarness:_executionHelper=TimelockExecutionHelper \
            TimelockExecutionHelper:_authorizer=TimelockAuthorizerHarness \
            SingletonAuthenticationHarness:_vault=Vault \
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
