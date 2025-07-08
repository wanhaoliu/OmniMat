from tqdm import tqdm
import os
import re
import ast
import textwrap
from openai import OpenAI
from gpt_api import api_request
import json
from simulation_validation import feedback_score

# --- FILE PATHS ---
INITIAL_DATA_FILE = "./output/0-1/filtered_dataset_test.json"
PROMPT_1_FILE = "./Simulator/prompt/mc4_prompt/classify.txt"
PROMPT_2_FILE = "./Simulator/prompt/mc4_prompt/key_points_list.txt"
PROMPT_3_FILE = "./Simulator/prompt/mc4_prompt/prompt_ablation.text"
PROMPT_4_FILE = "./Simulator/prompt/mc4_prompt/generated_hypo.txt"
PROMPT_5_FILE = "./Simulator/prompt/mc4_prompt/experimental_design.txt"


# PROMPT_2_FILE = "./Simulator/prompt/mc4_prompt/generated_hypo.txt"
# PROMPT_3_FILE = "./Simulator/prompt/mc4_prompt/experimental_design.txt"

def print_header(title):
    """Prints a formatted header to the console."""
    print("\n" + "="*80)
    print(f"// {title.upper()} //")
    print("="*80 + "\n")

def load_and_parse_initial_data(filepath):
    """Loads and parses the initial data file into a question and data part."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # initial_data = f.read()
            initial_data = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Initial data file not found: {INITIAL_DATA_FILE}")
        return None, None

    # initial_data[0] is the question, initial_data[1] is the gdth hypothesis, initial_data[2] is the key points
    return initial_data[0],initial_data[2]


def extract_effective_list(feedback):
    """
    Extract the list between ###Final Output### and ### End ###.
    Parameters:
   
    """
    # Regex to match content between###Final Output### and ###End ###
    match = re.search(r"###\s*Final Output\s*###\s*(.*?)\s*###\s*End\s*###", feedback, re.DOTALL)
    if match:
        content = match.group(1).strip()
        try:
            # Convert the content to a dictionary using `ast.literal_eval`
            return ast.literal_eval(content)
        except (ValueError, SyntaxError):
            # If parsing fails, return None
            return None
    return None


def validate_and_retry_list(feedback, prompt, api_request):
    """
    Validates if the extracted key points is a valid list. 
    """
    max_retries = 10
    retry_count = 0
    while retry_count < max_retries:
        extract_list = extract_effective_list(feedback)
        if isinstance(extract_list, list):
            return extract_list  # 
        else:
            print("Error: Extracted data is not a valid list. Retrying...")
            prompt += """Please ensure the output format is correct. Output Format:###Final Output###[]###End###"""
           
        retry_count += 1
        # Check if we've exhausted the retry attempts
        print(f"Retry attempt {retry_count} of {max_retries}...")
        feedback = api_request(prompt)
        print(f"Retry feedback:\n\n{feedback}")
    print("Critical Error: Could not extract a valid dictionary after retries.")
    return None


def regenerate_from_filtered_data(input_path, output_path,num=10):
    """
    Regenerates the dataset from the filtered data file.
    
    Parameters:
    - input_path (str): Path to the input JSON file containing the filtered data.
    - output_path (str): Path to save the regenerated dataset.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Input file not found: {input_path}")
        return

    # Assuming data is structured as [question, hypothesis, key_points]
    # question = data[0]
    # hypothesis = data[1]
    # key_points = data[2]

    # Format the output
    formatted_data = []
    # Add the question and hypothesis to the formatted data
    formatted_data.append(data[0])
    formatted_data.append(data[1])
    regenerate_data = []
    for i in range(num):
        print(f"\n// Regenerating data for iteration {i+1} //")
        # --- STEP 0: Load initial data ---
        chemical_question, technical_data= load_and_parse_initial_data(input_path)
        # --- STEP 1: DECONSTRUCTION & CATEGORIZATION ---
        print_header("STEP 1: DECONSTRUCTING INFORMATION")
        try:
            with open(PROMPT_1_FILE, 'r', encoding='utf-8') as f:
                prompt1_template = f.read()
        except FileNotFoundError:
            print(f"[ERROR] Prompt file not found: {PROMPT_1_FILE}")
            return

        prompt1_formatted = prompt1_template.format(
            chemical_question=chemical_question,
            technical_data=technical_data
        )
        
        print(f"prompt1_formatted{prompt1_formatted}\n")
        step1_output = api_request(prompt1_formatted)

        if not step1_output:
            print("[ERROR] Step 1 failed. Aborting process.")
            return
        print("deconstructing information...\n")
        print(textwrap.fill(step1_output, width=100))

        # --- STEP 2: HYPOTHESIS FORMULATION ---
        print_header("STEP 2: FORMULATING HYPOTHESIS")
        try:
            with open(PROMPT_2_FILE, 'r', encoding='utf-8') as f:
                prompt2_template = f.read()
        except FileNotFoundError:
            print(f"[ERROR] Prompt file not found: {PROMPT_2_FILE}")
            return

        prompt2_formatted = prompt2_template.format(
            chemical_question=chemical_question,
            analysis_from_step1=step1_output,
            history_of_hypotheses = regenerate_data
        )
        print(f"prompt2_formatted{prompt2_formatted}\n")
        step2_output = api_request(prompt2_formatted)

        if not step2_output:
            print("[ERROR] Step 2 failed. Aborting process.")
            return
        print("formulating hypothesis...\n")
        print(textwrap.fill(step2_output, width=100))
        regenerate_data.append(step2_output) 

    #add the regenerated data to the formatted data
    formatted_data.append(regenerate_data)
    # Save to output path
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, indent=4)
        
    print(f"Regenerated dataset saved to: {output_path}")
      



def ablate_hypothesis(key_points_to_ablate, question, source_hypothesis, baseline_score,input_path,output_path,score_drop_threshold=0.08):
    try:
        with open(PROMPT_3_FILE, 'r', encoding='utf-8') as f:
            prompt3_template = f.read()
    except FileNotFoundError:
        print(f"[ERROR] Prompt file not found: {PROMPT_3_FILE}")
        return
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Input file not found: {input_path}")
        return
    # Format the output
    # formatted_data = []
    # # Add the question and hypothesis to the formatted data
    # formatted_data.append(data[0])
    # formatted_data.append(data[1])
    questions_hypothesis_data = [data[0],data[1]] # Initialize the list with question and hypothesis
    essential_key_points = []
    for i, point_to_ablate in enumerate(tqdm(key_points_to_ablate, desc="Processing key points")):
        print_header(f"STEP 3.{i+1}: ABLATING KEY POINT: '{point_to_ablate}'")

        # --- Generate the Ablated Hypothesis ---
        print("Generating ablated (rewritten) hypothesis...")

        prompt3_formatted = prompt3_template.format(
        chemical_question=question,
        source_hypothesis=source_hypothesis,
        key_point_to_ablate=point_to_ablate
        )

        ablated_hypothesis = api_request(prompt3_formatted)
        if not ablated_hypothesis:
            print("Failed to generate ablated hypothesis. Skipping this point.")
            continue
        print("Ablated Hypothesis:\n", textwrap.fill(ablated_hypothesis, 80))
        regenerate_data = []
        regenerate_data.append(ablated_hypothesis)
        formatted_data = questions_hypothesis_data.copy()  # Start with the original question and hypothesis
        formatted_data.append(regenerate_data)
        # Save the ablated hypothesis to a file
        output_dir = f"{output_path}/ablated_hypothesis_{i+1}"
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        ablated_hypothesis_file = f"{output_dir}/ablated_hypothesis_{i+1}.json"

        with open(ablated_hypothesis_file, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, indent=4)
        output_dir = f"{output_path}/ablated_hypothesis_{i+1}"
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        essential_key_points = evaluate_ablated_hypothesis(ablated_hypothesis_file, i+1, baseline_score, score_drop_threshold, point_to_ablate, essential_key_points,output_dir)
    return essential_key_points



def evaluate_ablated_hypothesis(ablated_hypothesis_file, index, baseline_score, score_drop_threshold, point_to_ablate, essential_key_points, output_dir):
            # --- Score the Ablated Hypothesis ---
            correction_factor = 1
            sore_data_path = feedback_score(ablated_hypothesis_file, index, correction_factor, output_dir)
            
            with open(sore_data_path, 'r') as file:
                score_data = json.load(file)
            
            print(f"Processing data point with value {score_data[2][-1][-1]}")
            ablated_score = score_data[2][-1][-1]
            
            # --- Compare and Decide ---
            # score_drop = abs(float(baseline_score) - float(ablated_score)) 
            # BEGIN: modified to take absolute value
            score_drop = float(baseline_score) - float(ablated_score)
          
            print(f"Score Drop: {score_drop:.2f}")

            if score_drop >= score_drop_threshold:
                print(f"DECISION: Score drop is significant. '{point_to_ablate}' is ESSENTIAL.")
                essential_key_points.append(point_to_ablate)
            else:
                print(f"DECISION: Score drop is not significant. '{point_to_ablate}' is considered non-essential or redundant.")
            return essential_key_points



    #     # --- b. Score the Ablated Hypothesis ---
    #     print("\nEvaluating the ablated hypothesis...")
    #     ablated_score = score_hypothesis(question, ablated_hypothesis, prompt_score_template)
    #     print(f"Score for ablated hypothesis: {ablated_score:.2f}")

    #     # --- c. Compare and Decide ---
    #     score_drop = baseline_score - ablated_score
    #     print(f"Score Drop: {score_drop:.2f}")

    #     if score_drop >= score_drop_threshold:
    #         print(f"DECISION: Score drop is significant. '{point_to_ablate}' is ESSENTIAL.")
    #         essential_key_points.append(point_to_ablate)
    #     else:
    #         print(f"DECISION: Score drop is not significant. '{point_to_ablate}' is considered non-essential or redundant.")

    # # --- 3. Final Output ---
    # print_header("ABLATION STUDY COMPLETE")
    # print("The following key points were identified as essential:")
    # for point in essential_key_points:
    #     print(f"- {point}")

    # return essential_key_points



def main():
    """
    Main function to run the three-step research design process.
    """
    # --- STEP 0: Load initial data ---
    
    chemical_question, technical_data = load_and_parse_initial_data(INITIAL_DATA_FILE)

    # --- STEP 1: DECONSTRUCTION & CATEGORIZATION ---
    print_header("STEP 1: DECONSTRUCTING INFORMATION")
    try:
        with open(PROMPT_1_FILE, 'r', encoding='utf-8') as f:
            prompt1_template = f.read()
    except FileNotFoundError:
        print(f"[ERROR] Prompt file not found: {PROMPT_1_FILE}")
        return

    prompt1_formatted = prompt1_template.format(
        chemical_question=chemical_question,
        key_points_of_hypothesis=technical_data
    )
    
    print(f"prompt1_formatted{prompt1_formatted}\n")
    step1_output = api_request(prompt1_formatted)

    if not step1_output:
        print("[ERROR] Step 1 failed. Aborting process.")
        return
    print("deconstructing information...\n")
    print(textwrap.fill(step1_output, width=100))
    # return


    list = ["789","Poly(ionic liquid) Matrix"]
    # --- STEP 2: KEY POINTS TO LIST ---
    print_header("STEP 2: KEY POINTS TO LIST")

    try:
        with open(PROMPT_2_FILE, 'r', encoding='utf-8') as f:
            prompt2_template = f.read()
    except FileNotFoundError:
        print(f"[ERROR] Prompt file not found: {PROMPT_2_FILE}")
        return
    prompt2_formatted = prompt2_template.format(
        previously_evaluated_key_points=list,
        pre_categorized_document=step1_output
    )

    print(f"prompt2_formatted{prompt2_formatted}\n")
    step2_output = api_request(prompt2_formatted)

    extract_list = validate_and_retry_list(step2_output, prompt2_formatted, api_request)

    if not step2_output:
        print("[ERROR] Step 2 failed. Aborting process.")
        return
    print("formulating hypothesis...\n")
    # print(textwrap.fill(step2_output, width=100))
    print(f"extract_list{extract_list}\n")
    # print(extract_list)
    # return
   
    # --- STEP 3: HYPOTHESIS ABLATION ---
    print_header("STEP 3: HYPOTHESIS ABLATION")

    source_hypothesis="We hypothesize that engineering a dual-crosslinked hierarchical polymer electrolyte system combining poly(ionic liquids) (PILs) and poly(vinyl alcohol) (PVA) will significantly enhance ionic conductivity and mechanical properties for thermoelectric applications. This will be achieved through a meticulously designed process involving salting-out, freeze-casting, and electrospinning techniques, integrated with the incorporation of thermogalvanic ions.\n\nMethodology:\n\n1. Material Preparation:\n   - Synthesize a PIL matrix via a chemical modification step that introduces sulfonate groups (—SO₃⁻) to the polymer backbone, enhancing ionic transport. This should be accomplished using a suitable solvent such as dimethylformamide (DMF) at 60°C for 3 hours under nitrogen conditions to prevent moisture contamination.\n   - Prepare a 10% (w/v) PVA solution in deionized water at 80°C, adding lithium salts (e.g., LiCl) at a concentration of 0.2 M to enhance ionic mobility across the polymer matrix.\n\n2. Salting-Out Process:\n   - Gradually introduce ammonium sulfate (0.2 M) to the PVA solution while stirring at a controlled rate of 300 RPM. Allow the solution to phase-separate at 25°C for 2 hours to induce the formation of porous microstructures, targeting the creation of a network conducive to ionic transport.\n\n3. Dual-Crosslinking and Hierarchical Structure Formation:\n   - Apply the synthesized PIL solution onto the phase-separated PVA layer using a spray-coating method to ensure uniform coverage. Crosslink the hybrid system using 0.05 M N,N'-methylenebisacrylamide under 254 nm UV irradiation for 10 minutes to form a robust interpenetrating network that enhances ionic pathways.\n   - Utilize electrospinning with parameters set at an applied voltage of 18 kV and a solution concentration of 12% (w/v). Collect aligned fibers on a rotating collector to integrate into the polymer matrix, followed by ice-templating, freezing the assembly with a rate of -2 °C/min to form homogeneous nanochannels.\n\n4. Incorporation of Thermogalvanic Ions:\n   - Integrate a redox couple (e.g., ferro/ferricyanide) at a concentration of 1-3 mol/L during the gelation phase to enhance electrochemical performance. Aim for homogenous dispersion through a gentle mixing process that maintains structural integrity.\n\n5. Mechanical Training Procedure:\n   - Conduct cyclic stretching of the resultant polymer electrolyte at strains of 20-30% for 500 cycles. This mechanical training aims to align the polymer chains and improve inter-fibrillar bonding, enhancing the material's fatigue resistance and overall mechanical strength.\n\n6. Characterization:\n   - Employ Scanning Electron Microscopy (SEM) to elucidate the microstructural characteristics, confirming the alignment of nanochannels and fibers. Measure ionic conductivity via Electrochemical Impedance Spectroscopy (EIS) at varying temperatures (20-80°C), ensuring targeted conductivity exceeds 10⁻³ S/m.\n   - Assess mechanical integrity through tensile tests following ASTM D638, aiming for mechanical toughness > 2500 J/m² and elongation at break beyond 300%.\n\n7. Device Integration:\n   - Lastly, incorporate the engineered polymer electrolyte into a prototype thermoelectric cell, evaluating essential parameters such as the Seebeck coefficient and output power density against established benchmarks. This step aims to validate the practical applicability of the developed hybrid polymer systems in next-generation thermoelectric devices.\n\nBy utilizing this comprehensive methodology, we anticipate overcoming the current limitations of polymer electrolytes, thereby significantly enhancing their ionic conductivity and mechanical resilience for thermoelectric applications."

    print(f"--------------------source_hypothesis---------\n{source_hypothesis}")

    baseline_score = 0.012890689144001
    input_path = INITIAL_DATA_FILE
    output_path = "./output0707_TEST1/"
    os.makedirs(output_path, exist_ok=True)
    essential_key_points = ablate_hypothesis(extract_list, chemical_question, source_hypothesis, baseline_score,input_path,output_path,score_drop_threshold=0.009)
    # ablate_hypothesis(extract_list, chemical_question, source_hypothesis)
    print(f"Essential Key Points: {essential_key_points}")


    return

    try:
        with open(PROMPT_3_FILE, 'r', encoding='utf-8') as f:
            prompt3_template = f.read()
    except FileNotFoundError:
        print(f"[ERROR] Prompt file not found: {PROMPT_3_FILE}")
        return

    prompt3_formatted = prompt3_template.format(
        chemical_question=chemical_question,
        analysis_from_step1=step1_output
    )
    print(f"prompt3_formatted{prompt3_formatted}\n")
    step3_output = api_request(prompt3_formatted)

    if not step3_output:
        print("[ERROR] Step 2 failed. Aborting process.")
        return
    print("formulating hypothesis...\n")
    print(textwrap.fill(step3_output, width=100))









    # --- STEP 3: VALIDATION PROTOCOL DESIGN ---
    print_header("STEP 3: DESIGNING VALIDATION PROTOCOL (FINAL OUTPUT)")
    try:
        with open(PROMPT_3_FILE, 'r', encoding='utf-8') as f:
            prompt3_template = f.read()
    except FileNotFoundError:
        print(f"[ERROR] Prompt file not found: {PROMPT_3_FILE}")
        return

    # prompt3_formatted = prompt3_template.format(
    #     hypothesis_from_step2=step2_output
    # )
    prompt3_formatted = prompt3_template.format(
        chemical_question=chemical_question,
        hypothesis_from_step2=step2_output,
    )
    print(f"prompt3_formatted{prompt3_formatted}\n")
    final_output = api_request(prompt3_formatted)

    if not final_output:
        print("[ERROR] Step 3 failed.")
        return
    print("designing validation protocol...\n")
    print(final_output)
    print("\n" + "="*80)
    print("// PROCESS COMPLETE //")
    print("="*80)

if __name__ == "__main__":
    main()