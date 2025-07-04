#!/bin/bash

for rep in {1..1}
do
    echo "Starting repetition $rep"
    for i in 0 
    do
        echo "  Processing simulation $i (Repeat $rep)"
        mkdir -p "./output/$i-$rep"
 

  
        python ./Method/simulation_validation.py --num $i --rep $rep  --correction_factor 1 > "./output/$i-$rep/$i-$rep.txt" &
    
    done

    echo "Repetition $rep completed"
done