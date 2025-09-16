#!/bin/bash

for rep in {1..1}
do
    echo "Starting repetition $rep"
    for i in 0 
    do
        echo "  Processing simulation $i (Repeat $rep)"
        mkdir -p "Method/0916_output/process_results/"
 

  
        # python  ./Method/refine_hypo.py  > "Method/0916_output/process_results/output.txt" &
        python ./Method/refine_hypo.py \
    --input_path "./Data_experiment/i-TE/0/0.json" \
    --output_dir "./Method/0916_output/process_results/" \
    --inspire_paper_path "./Data_experiment/inspire_paper.json" \
    --expert_suggestions "none" "none" \
    --experimental_results "Experimental testing of low, medium, and high molecular weight PVA at mass fractions of 2 wt%, 5 wt%, 10 wt%, and 20 wt% under potassium ferrocyanide/potassium ferricyanide concentrations of 0.1 M, 0.2 M, 0.5 M, and 0.8 M showed the following gelation behavior: For low molecular weight PVA (l-PVA), no gel formation was observed under all tested concentration combinations. For medium and high molecular weight PVA, no gel formation occurred at 2 wt% PVA." > "Method/0916_output/process_results/output.txt" &
    
    done

    echo "Repetition $rep completed"
done