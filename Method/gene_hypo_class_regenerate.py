import os
import textwrap
from openai import OpenAI
from gpt_api import api_request
import json

# --- FILE PATHS ---

# Initial data file containing the question, hypothesis, and key points
INITIAL_DATA_FILE = "./output/0-1/filtered_dataset.json"
PROMPT_1_FILE = "./Simulator/prompt/mc4_prompt/classify.txt"
#./Simulator/prompt/mc4_prompt_v2/deconstruct_v2.txt

PROMPT_2_FILE = "./Simulator/prompt/mc4_prompt/generated_hypo.txt"
PROMPT_3_FILE = "./Simulator/prompt/mc4_prompt/experimental_design.txt"

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
        chemical_question, technical_data = load_and_parse_initial_data(input_path)
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
        analysis_from_step1=step1_output
    )
    print(f"prompt2_formatted{prompt2_formatted}\n")
    step2_output = api_request(prompt2_formatted)

    if not step2_output:
        print("[ERROR] Step 2 failed. Aborting process.")
        return
    print("formulating hypothesis...\n")
    print(textwrap.fill(step2_output, width=100))









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