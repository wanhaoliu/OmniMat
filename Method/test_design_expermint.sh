#!/bin/bash

for rep in 3
do
    echo "Starting repetition $rep"
    for i in 0 
    do
        echo "  Processing simulation $i (Repeat $rep)"
        mkdir -p "./output1/$i-$rep"
 

  
        python ./Method/test_design_expermint.py  > "./output1/$i-$rep/$i-$rep.txt" &
    
    done

    echo "Repetition $rep completed"
done