from simulation_validation import feedback_score
from gene_hypo import regenerate_from_filtered_data
import os
import json
# from dataset import extract_and_save_key_points

def read_and_filter_json(file_path, score_threshold=0.001):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    dataset = []
    dataset.append(data[0])  # Add question to dataset
    dataset.append(data[1])  # Add gdth_hypothesis to dataset
    dataset_key_point = []  # Initialize list for key points
    for i in range(len(data[2])):
        if float(data[2][i][-1]) > score_threshold:
            print(f"Processing data point {i} with value {data[2][i][-1]}")
            dataset_key_point.append(data[2][i][1])
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


def iterative_process(initial_hypotheses_file, index, correction_factor, output_dir, num_iterations=10):

    current_hypotheses_file = initial_hypotheses_file

    for i in range(num_iterations):
        iteration_num = i + 1
        print(f"\n--- Iteration {iteration_num}/{num_iterations} ---")

        # define the output directory for this iteration
        iteration_output_dir = os.path.join(output_dir, f"iteration_{iteration_num}")
        os.makedirs(iteration_output_dir, exist_ok=True)

        # define the output file paths for this iteration
        key_points_path = os.path.join(iteration_output_dir, f"key_points_{iteration_num}.json")
        regenerated_hypotheses_path = os.path.join(iteration_output_dir, f"regenerated_hypotheses_{iteration_num}.json")

        # simulation_validation input: hypotheses_file 
        filtered_data_path = feedback_score(
            hypotheses_file=current_hypotheses_file, 
            index=index, 
            correction_factor=correction_factor, 
            output_dir=iteration_output_dir  # input directory for feedback_score 
        )

        # extract_and_save_key_points input: filtered_data_path
        extract_and_save_key_points(
            input_path=filtered_data_path, # use the output from feedback_score
            output_file_path=key_points_path, 
            score_threshold=0.001
        )

        with open(key_points_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data[2]==[]:
            print(f"[ERROR] No key points found in iteration {iteration_num}. Ending process.")
            break

        # regenerate hypotheses from filtered data
        regenerate_from_filtered_data(
            input_path=key_points_path,
            output_path=regenerated_hypotheses_path,
            num=5  # Number of hypotheses to regenerate
        )

        # Update the current hypotheses file for the next iteration
        current_hypotheses_file = regenerated_hypotheses_path

    print(f"\n✅ Iterative process completed. Check the '{output_dir}' directory.")


# Main function to run the iterative process
if __name__ == '__main__':
    main_output_directory = "./process_results4"
    initial_file = "./Data_experiment/i-TE/0/0.json"


    # Run the iterative process with the specified parameters
    iterative_process(
        initial_hypotheses_file=initial_file,
        index=1, 
        correction_factor=1,
        output_dir=main_output_directory,
        num_iterations=3
    )
