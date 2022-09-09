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
    --msg "StableMath no setts 1000: $1" \

    #--settings -t=500,-mediumTimeout=30,-depth=20,-enableEqualitySaturation=false \
    #--settings -divideNoRemainder=true,-s=z3_def,yices,z3,-smt_hashingScheme=PlainInjectivity,-t=1000,-mediumTimeout=30,-depth=40 \
