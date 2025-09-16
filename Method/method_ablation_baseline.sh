# !/bin/bash

for i in {1..1}

do
    echo "$i"
    mkdir -p "./output/Output_0420-noise-baseline0-all-4o-min/$i"
    python ./Method/method_ablation_baseline.py --num $i --baseline 0 --num_entries all > ./output/Output_0420-noise-baseline0-all-4o-min/$i/$i.txt &
 
done

