#!/bin/bash

for rep in {1..1}
do
    echo "Starting repetition $rep"
    for i in 0 
    do
        echo "  Processing simulation $i (Repeat $rep)"
        mkdir -p "./output/"
 

  
        python ./Method/gene_hypo.py  > "./output/gene_hypo.txt" &
    
    done

    echo "Repetition $rep completed"
done