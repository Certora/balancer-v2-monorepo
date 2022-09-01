if [[ "$1" ]]
then
    RULE="--rule $1"
fi
certoraRun \
    certora/harnesses/StableMath2.sol:StableMath \
    --verify StableMath:certora/specs/StableMath.spec \
    --staging \
    --cache balancerOld \
    --optimistic_loop \
    --loop_iter 2 \
    --send_only \
    $RULE \
    --msg "StableMath top bottom sum: $1" \

    #--settings -t=500,-mediumTimeout=30,-depth=20,-enableEqualitySaturation=false \
