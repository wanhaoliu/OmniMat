from simulation_validation import feedback_score
from gene_hypo import extract_lsit,print_header,ablate_hypothesis,regenerate_from_list_data,design_experimental_protocol,design_interation_expert_experimental_protocol
import os
import json
import argparse
# from dataset import extract_and_save_key_points

def read_and_filter_json(file_path, score_threshold=0.001):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    dataset = []
    dataset.append(data[0])  # Add question to dataset
    dataset.append(data[1])  # Add gdth_hypothesis to dataset
    dataset_key_point = []  # Initialize list for key points
    for i in range(len(data[2])):
        # data_score = []
        if float(data[2][i][-1]) > score_threshold:
            print(f"Processing data point {i} with value {data[2][i][-1]}")
            # dataset_key_point.append(data[2][i][1])

            # data_score.append(data[2][i])
            # dataset_key_point.append(data_score)  # Append the filtered key point
            dataset_key_point.append(data[2][i])  # Append the filtered key point
    dataset.append(dataset_key_point)  # Add key points to dataset
    return dataset

def save_dataset_to_json(dataset, output_file_path):
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    # Save the dataset to a JSON file
    with open(output_file_path, 'w') as outfile:
        json.dump(dataset, outfile)

def extract_and_save_key_points(input_path, output_file_path,score_threshold=0.001):
    """
    Extracts key points from a JSON file based on a score threshold and saves them to a new JSON file.
    
    Parameters:
    - input_path (str): Path to the input JSON file.
    - output_file_path (str): Path to save the output JSON file.
    - score_threshold (float): Minimum score to include a key point.
    """
    filtered_data = read_and_filter_json(input_path, score_threshold)
    save_dataset_to_json(filtered_data, output_file_path)


def iterative_process(initial_hypotheses_file, index,num, correction_factor, output_dir, num_iterations=3):
    current_hypotheses_file = initial_hypotheses_file
    iteration_num = num
    iteration_output_dir = os.path.join(output_dir, f"iteration_{iteration_num}")

    # simulator hypotheses feedback_score
    filtered_data_path = feedback_score(
            hypotheses_file=current_hypotheses_file, 
            index=index, 
            correction_factor=correction_factor, 
            output_dir=iteration_output_dir  # input directory for feedback_score 
        )
    
    key_points_path = os.path.join(iteration_output_dir, f"key_points_{iteration_num}.json")
    # extract key points from filtered data
    extract_and_save_key_points(
            input_path=filtered_data_path, # use the output from feedback_score
            output_file_path=key_points_path, 
            score_threshold=0.015  # threshold for key points extraction
        )
    # Check if the key points file exists and is not empty
    with open(key_points_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    if data[2]==[]:
        print(f"[ERROR] No key points found in iteration {iteration_num}. Ending process.")
        return
    previously_evaluated_list = []
    chemical_question = data[0]
    for i in range(len(data[2])):
        technical_data = data[2][i][1] # extract the key points
        # Extract the list of simulated hypotheses from the technical data except the previously_evaluated_list
        extract_list = extract_lsit(chemical_question, technical_data, previously_evaluated_list)
    # Get the source hypothesis from the data\
        source_hypothesis = data[2][i][0]  # source hypothesis
        baseline_score = data[2][i][-1]  # baseline score
    # ---STEP 3: HYPOTHESIS ABLATION ---
        print_header("STEP 3:HYPOTHESIS ABLATION")
    # Get the source hypothesis from the data
        ablate_output_dir = os.path.join(iteration_output_dir, f"ablation_{i+1}")
        os.makedirs(ablate_output_dir, exist_ok=True)  # Ensure the directory exists
        essential_key_points = ablate_hypothesis(extract_list, chemical_question, source_hypothesis, baseline_score,initial_hypotheses_file,ablate_output_dir,score_drop_threshold=0.010)#0.01

        print(f"Essential Key Points: {essential_key_points}")

        # previously_evaluated_list.append(essential_key_points)
        previously_evaluated_list.extend(essential_key_points)  # Append the essential key points to the list

    chemical_question_gdth_hypothses = [data[0], data[1]]  # Update the chemical question with the new hypotheses
    new_path = regenerate_from_list_data(chemical_question_gdth_hypothses,previously_evaluated_list, iteration_output_dir,num_iterations)

    print(f"\n✅ Iterative process completed. Check the '{output_dir}' directory.")
    return new_path

def main():
    
    parser = argparse.ArgumentParser(
        description="Design an experimental protocol based on input data, expert suggestions, and experimental results."
    )

    parser.add_argument(
        '--input_path',
        type=str,
        required=True,
        help="Path to the input JSON file containing hypotheses or data"
    )
    
    parser.add_argument(
        '--output_dir',
        type=str,
        required=True,
        help="Path to the output directory where the generated experimental protocol JSON file will be saved (e.g., './Method/0818_output/')"
    )


    parser.add_argument(
    '--inspire_paper_path',
    type=str,
    required=True,
    help="Path to the JSON file containing the experimental protocol of the inspiring paper (e.g., './Data_experiment/inspire_paper.json')"
)



    parser.add_argument(
        '--expert_suggestions',
        type=str,
        nargs='*',
        default=["none", "none"],
        help="List of expert suggestions to guide the experimental protocol (default: ['none', 'none']). Provide as space-separated strings."
    )
    
    parser.add_argument(
        '--experimental_results',
        type=str,
        default="none",
        help="Description of experimental results to inform the protocol design (default: 'none')."
    )



    args = parser.parse_args()




    main_output_directory = args.output_dir
    initial_file = args.input_path
    inspire_paper_path = args.inspire_paper_path


    # Run the iterative process with the specified parameters
    path = initial_file
    for i  in range(3):
        print(f"\n\n--- Iteration {i} ---")
        iter_path = iterative_process(
        initial_hypotheses_file=path,
        index=1, num=i,
        correction_factor=1,
        output_dir=main_output_directory,
        num_iterations=15
        )
        path = iter_path


    print(f"\n\nhypotheses saved to: {path}")

    #construct the experimental protocol based on the hypotheses and the inspire paper
    output_path = design_experimental_protocol(path,inspire_paper_path)
    print(f"\n\nexperimental protocol saved to: {output_path}")

    print_header("Designing Experimental Protocol based on Expert Suggestions and Experimental Results")
    
    path = "./Data_experiment/Output/test/regenerated_data.json"
    output_path = "./Data_experiment/Output/test/regenerated_data_experimental_protocol.json"


    # Call the function to design the experimental protocol
    path_experimental_protocol=design_interation_expert_experimental_protocol(
        input_path=path,
        experimental_path=output_path,
        expert_suggestions=args.expert_suggestions,
        experimental_results=args.experimental_results
    )
    # main_output_directory = args.input_path

    print(f"\n\nExperimental protocol finished. Check the '{path_experimental_protocol}' directory for results.")

if __name__ == '__main__':
    main()









