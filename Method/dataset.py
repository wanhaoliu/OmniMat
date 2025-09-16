import json
import os
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

# This script reads a JSON file, filters the data based on a condition,
def main():
    file_path = './hypotheses_final_score_output_0.json'  # Update with your JSON file path
    filtered_data = read_and_filter_json(file_path)
    # print("Filtered dataset:", filtered_data)
    output_file_path = './filtered_dataset.json'  # Update with your desired output file path
    save_dataset_to_json(filtered_data, output_file_path)

if __name__ == "__main__":
    main()