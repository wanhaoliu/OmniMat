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
INITIAL_DATA_FILE = "./filtered_dataset.json"
PROMPT_1_FILE = "./Simulator/prompt/mc4_prompt/classify.txt"
PROMPT_2_FILE = "./Simulator/prompt/mc4_prompt/key_points_list.txt"
PROMPT_3_FILE = "./Simulator/prompt/mc4_prompt/prompt_ablation.text"
PROMPT_4_FILE = "./Simulator/prompt/mc4_prompt/generated_hypo.txt"
PROMPT_5_FILE = "./Simulator/prompt/mc4_prompt/experimental_design.txt"
# add inspire paper
PROMPT_6_FILE = "./Simulator/prompt/mc4_prompt/experimental_design_inspired_paper.txt"
# add expert 
PROMPT_7_FILE = "./Simulator/prompt/mc4_prompt/experimental_design_expert.txt"

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

# refine_hypo_class_regenerate.py
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
      



def ablate_hypothesis(key_points_to_ablate, question, source_hypothesis, baseline_score,input_path,output_file_dir,score_drop_threshold=0.08):
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
        point_to_ablate_path = point_to_ablate.replace('/', '_')
        output_dir = f"{output_file_dir}/ablated_hypothesis_{point_to_ablate_path}"
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        ablated_hypothesis_file = f"{output_dir}/ablated_hypothesis_{point_to_ablate_path}.json"

        with open(ablated_hypothesis_file, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, indent=4)
        # output_dir = f"{output_dir}/ablated_hypothesis_{i+1}"
        # Ensure the output directory exists
        # os.makedirs(output_dir, exist_ok=True)
        essential_key_points = evaluate_ablated_hypothesis(ablated_hypothesis_file, i+1, baseline_score, score_drop_threshold, point_to_ablate, essential_key_points,output_dir)
    return essential_key_points


def evaluate_ablated_hypothesis(ablated_hypothesis_file, index, baseline_score, score_drop_threshold, point_to_ablate, essential_key_points, output_dir):
            # --- Score the Ablated Hypothesis ---
            correction_factor = 1
            sore_data_path = feedback_score(ablated_hypothesis_file, index, correction_factor, output_dir)
            
            with open(sore_data_path, 'r') as file:
                score_data = json.load(file)
            print(f"Baseline Score: {baseline_score}")
            print(f"Processing data point with value {score_data[2][-1][-1]}")
            ablated_score = score_data[2][-1][-1]
            
            # --- Compare and Decide ---
            # score_drop = abs(float(baseline_score) - float(ablated_score)) 
            # BEGIN: modified to take absolute value
            score_drop = float(baseline_score) - float(ablated_score)
          
            print(f"Score Drop: {score_drop:.5f}")

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

def regenerate_from_list_data(chemical_question_gdth_hypothese,ssential_key_points, output_dir,num=3):
    """
    Regenerates the dataset from the filtered data file.

    """
    chemical_question = chemical_question_gdth_hypothese[0]
    # Initialize the list to store formatted data
    # formatted_data = []
    # Initialize the list to store regenerated data
    regenerate_data = []
    for i in range(num):
        
        # --- HYPOTHESIS FORMULATION ---
        print_header("FORMULATING HYPOTHESIS")
        try:
            with open(PROMPT_4_FILE, 'r', encoding='utf-8') as f:
                prompt4_template = f.read()
        except FileNotFoundError:
            print(f"[ERROR] Prompt file not found: {PROMPT_4_FILE}")
            return

        prompt4_formatted = prompt4_template.format(
            chemical_question=chemical_question,
            list_of_chemicals_and_techniques=ssential_key_points,
           history_of_hypotheses = regenerate_data
        )
        print(f"prompt4_formatted{prompt4_formatted}\n")
        step4_output = api_request(prompt4_formatted)

        if not step4_output:
            print("[ERROR] generate failed. Aborting process.")
            return
        print("formulating hypothesis...\n")
        print(textwrap.fill(step4_output, width=100))
        regenerate_data.append(step4_output) 

    #add the regenerated data to the formatted data
    # formatted_data.append(regenerate_data)
    # Add the question and hypothesis to the formatted data
    chemical_question_gdth_hypothese.append(regenerate_data)
    # Save to output path
    output_path = os.path.join(output_dir, "regenerated_data.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(chemical_question_gdth_hypothese, f, indent=4)
        
    print(f"Regenerated dataset saved to: {output_path}")
    return output_path

def extract_lsit(chemical_question, technical_data, previously_evaluated_list):

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


    # --- STEP 2: KEY POINTS TO LIST ---
    print_header("STEP 2: KEY POINTS TO LIST")

    try:
        with open(PROMPT_2_FILE, 'r', encoding='utf-8') as f:
            prompt2_template = f.read()
    except FileNotFoundError:
        print(f"[ERROR] Prompt file not found: {PROMPT_2_FILE}")
        return
    prompt2_formatted = prompt2_template.format(
        previously_evaluated_key_points=previously_evaluated_list,
        pre_categorized_document=step1_output
    )

    print(f"prompt2_formatted{prompt2_formatted}\n")
    step2_output = api_request(prompt2_formatted)

    extract_list = validate_and_retry_list(step2_output, prompt2_formatted, api_request)

    if not step2_output:
        print("[ERROR] Step 2 failed. Aborting process.")
        return
    # print("formulating hypothesis...\n")
    # print(textwrap.fill(step2_output, width=100))
    print(f"extract_list{extract_list}\n")
    # previously_evaluated_list.append(extract_list)
    # print(f"previously_evaluated_list{previously_evaluated_list}\n")
    # return previously_evaluated_list
    return extract_list

# def design_experimental_protocol(input_path):
#     with open(input_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#     chemical_question = data[0]
    
#     try:
#         with open(PROMPT_5_FILE, 'r', encoding='utf-8') as f:
#             prompt5_template = f.read()
#     except FileNotFoundError:
#         print(f"[ERROR] Prompt file not found: {PROMPT_5_FILE}")
#     designing_experiment = []
#     for i in range(len(data[2])):
#         step2_output = data[2][i]
#         prompt5_formatted = prompt5_template.format(
#         chemical_question=chemical_question,
#         hypothesis_from_step2=step2_output,
#     )
#         print(f"prompt5_formatted{prompt5_formatted}\n")
#         final_output = api_request(prompt5_formatted)
#         print("designing validation protocol...\n")
#         print(final_output)
#         designing_experiment.append(final_output)
#     # Save the final output to the output path
#     directory = os.path.dirname(input_path)
#     new_filename = os.path.basename(input_path).replace('.json', '_experimental_protocol.json')
#     output_path = os.path.join(directory, new_filename)
    
#     with open(output_path, 'w', encoding='utf-8') as f:
#         json.dump(designing_experiment, f, indent=4)

def design_experimental_protocol(input_path,inspire_paper_path):
    with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    chemical_question = data[0]
    with open(inspire_paper_path, 'r', encoding='utf-8') as f:
            inspire_paper_data = json.load(f)
            inspire_paper =  inspire_paper_data
    
    try:
        with open(PROMPT_6_FILE, 'r', encoding='utf-8') as f:
            prompt5_template = f.read()
    except FileNotFoundError:
        print(f"[ERROR] Prompt file not found: {PROMPT_5_FILE}")
    designing_experiment = []
    for i in range(len(data[2])):
        step2_output = data[2][i]
        prompt5_formatted = prompt5_template.format(
        chemical_question=chemical_question,
        hypothesis_from_step2=step2_output,
        additional_reference_protocols = inspire_paper
    )
        print(f"prompt5_formatted{prompt5_formatted}\n")
        final_output = api_request(prompt5_formatted)
        print("designing validation protocol...\n")
        print(final_output)
        designing_experiment.append(final_output)
    # Save the final output to the output path
    directory = os.path.dirname(input_path)
    new_filename = os.path.basename(input_path).replace('.json', '_experimental_protocol.json')
    output_path = os.path.join(directory, new_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(designing_experiment, f, indent=4)
    return output_path

def design_interation_expert_experimental_protocol(input_path,experimental_path,expert_suggestions,experimental_results):
    with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    chemical_question = data[0]
    with open(experimental_path, 'r', encoding='utf-8') as f:
           experimental_data = json.load(f)
            # experimental =  experimental_data
    
    try:
        with open(PROMPT_7_FILE, 'r', encoding='utf-8') as f:
            prompt5_template = f.read()
    except FileNotFoundError:
        print(f"[ERROR] Prompt file not found: {PROMPT_7_FILE}")
    designing_experiment = []

    for i in range(len(experimental_data)):
        experimental_output = experimental_data[i]
        prompt5_formatted = prompt5_template.format(
        chemical_question=chemical_question,
        experimental_scheme = experimental_output,
        experimental_results = experimental_results,
        expert_suggestions = expert_suggestions[i]
    )
        print(f"prompt5_formatted{prompt5_formatted}\n")
        final_output = api_request(prompt5_formatted)
        print("designing validation protocol...\n")
        print(final_output)
        designing_experiment.append(final_output)
    # Save the final output to the output path
    directory = os.path.dirname(input_path)
    new_filename = os.path.basename(input_path).replace('.json', '_experimental_expert_protocol.json')
    output_path = os.path.join(directory, new_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(designing_experiment, f, indent=4)
    return output_path



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


    list = ["Poly(ionic liquid) Matrix"]
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

    
    # input_path = INITIAL_DATA_FILE
    # output_path = "./output0708_TEST2/"
    # os.makedirs(output_path, exist_ok=True)
    # essential_key_points = ablate_hypothesis(extract_list, chemical_question, source_hypothesis, baseline_score,input_path,output_path,score_drop_threshold=0.01)
    # # ablate_hypothesis(extract_list, chemical_question, source_hypothesis)
    # # essential_key_points = [ "Poly(vinyl alcohol) (PVA)", "Freeze-casting","Ferro/Ferricyanide Redox Couple" ]
    # print(f"Essential Key Points: {essential_key_points}")

    # regenerate_from_list_data(chemical_question,essential_key_points, output_path,num=3)


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