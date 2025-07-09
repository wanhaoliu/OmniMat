#!/bin/bash

for rep in {1..1}
do
    echo "Starting repetition $rep"
    for i in 0 
    do
        echo "  Processing simulation $i (Repeat $rep)"
        mkdir -p "./process_results5/"
 

  
        python  ./Method/refine_hypo.py  > "./process_results5/output.txt" &
    
    done

    echo "Repetition $rep completed"
done