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
    file_path = './output/0-1/hypotheses_final_score_output_0.json'  # Update with your JSON file path
    filtered_data = read_and_filter_json(file_path)
    # print("Filtered dataset:", filtered_data)
    output_file_path = './output/0-1/filtered_dataset.json'  # Update with your desired output file path
    save_dataset_to_json(filtered_data, output_file_path)

if __name__ == "__main__":
    main()

"""
 ["###Chemical Key Points###\n1. **Poly(Ionic Liquids) (PILs)**\n   Role and Function: The incorporation of poly(ionic liquids) into the polymer electrolyte system introduces sulfonate groups (—SO₃⁻) that enhance ionic transport. The presence of these ionic groups increases the mobility of ions within the polymer matrix, which is crucial for improving ionic conductivity. The chemical modification of the polymer backbone facilitates better ion dissociation and transport pathways, directly addressing the need for enhanced ionic conductivity in thermoelectric applications.\n\n2. **10% (w/v) Poly(Vinyl Alcohol) (PVA)**\n   Role and Function: PVA serves as a structural backbone for the polymer electrolyte, providing mechanical integrity and flexibility. The addition of lithium salts (e.g., LiCl) at a concentration of 0.2 M further enhances ionic mobility by increasing the number of charge carriers available for conduction. The combination of PVA and lithium salts creates a conducive environment for ionic transport, which is essential for achieving the desired thermoelectric performance.\n\n3. **Ammonium Sulfate (0.2 M)**\n   Role and Function: Ammonium sulfate is used in the salting-out process to induce phase separation in the PVA solution, leading to the formation of porous microstructures. This phase separation is critical for creating a network that facilitates ionic transport by increasing the surface area and creating pathways for ion movement. The resulting porous structure enhances the overall ionic conductivity of the polymer electrolyte.\n\n4. **N,N'-Methylenebisacrylamide (0.05 M)**\n   Role and Function: This crosslinking agent is essential for forming a robust interpenetrating network within the hybrid polymer system. By crosslinking the PIL and PVA, it enhances the mechanical properties and stability of the electrolyte while also improving the ionic pathways. The crosslinked structure allows for better retention of ionic mobility and mechanical strength, which are vital for thermoelectric applications.\n\n5. **Ferro/Ferricyanide Redox Couple (1-3 mol/L)**\n   Role and Function: The incorporation of this redox couple during the gelation phase enhances the electrochemical performance of the polymer electrolyte. The redox reactions facilitate charge transfer processes, which are crucial for improving the thermoelectric properties of the system. The presence of these ions increases the overall conductivity and efficiency of the thermoelectric cell.\n\n6. **Electrospinning Technique**\n   Role and Function: Electrospinning is employed to create aligned fibers that integrate into the polymer matrix, enhancing the structural organization and ionic pathways. The alignment of fibers improves the mechanical properties and facilitates better ionic transport due to the increased surface area and connectivity within the polymer electrolyte. This technique is critical for achieving the hierarchical structure necessary for high-performance thermoelectric applications.\n\n7. **Cyclic Stretching (Mechanical Training)**\n   Role and Function: The mechanical training procedure aligns the polymer chains and improves inter-fibrillar bonding, which enhances the material's fatigue resistance and overall mechanical strength. This process is essential for ensuring that the polymer electrolyte can withstand operational stresses while maintaining its ionic conductivity and mechanical integrity.\n\n###End Chemical Key Points###", '###Chemical Key Points###\n1. **Poly(ionic liquid) (PIL) Matrix**  \n   Role and Function: The poly(ionic liquid) serves as the foundational polymer matrix due to its inherent ionic conductivity. The chemical modification with sulfate (—SO₃⁻) functional groups enhances solubility and ionic transport by creating ionic motifs that facilitate the movement of ions through the polymer network. This modification is crucial for improving ionic conductivity, which directly addresses the scientific question of enhancing ionic conductivity in quasi-solid-state polymer electrolytes.\n\n2. **Electrospinning and Ice-Templating Techniques**  \n   Role and Function: The combination of electrospinning and ice-templating is employed to fabricate a hierarchical structure characterized by aligned nanochannels and fibrillar architectures. Electrospinning generates aligned polymer fibers, while ice-templating creates uniform nanochannels that significantly reduce tortuosity, thereby enhancing ionic conductivity. This structural engineering is essential for improving both ionic transport and mechanical performance, directly contributing to the objectives outlined in the scientific question.\n\n3. **Ferro/Ferricyanide Redox Couple**  \n   Role and Function: The integration of the ferro/ferricyanide redox couple into the polymer matrix enhances electrochemical performance by facilitating redox reactions that improve ionic transport. The optimization of its concentration (1-3 mol/L) during the gelation phase ensures a homogeneous distribution, which is critical for maintaining mechanical stability while enhancing the overall ionic conductivity of the polymer electrolyte. This directly supports the goal of improving thermoelectric performance in high-performance thermal batteries.\n\n4. **Mechanical Training Regimen**  \n   Role and Function: The bespoke mechanical training regimen, involving cyclic stretching at 20-30% strain, is designed to enhance the mechanical properties of the structured polymer electrolyte. This process aligns polymer chains and improves inter-fibrillar interactions, leading to increased toughness and elasticity. By addressing mechanical performance, this key point contributes to the overall goal of enhancing the performance of quasi-solid-state polymer electrolytes in thermal batteries.\n\n5. **Electrochemical Impedance Spectroscopy (EIS)**  \n   Role and Function: EIS is utilized to quantify ionic conductivity across a range of temperatures (20-80 °C) and to assess the performance of the polymer electrolyte. By focusing on obtaining Nyquist plots, this method provides critical data on ionic transport properties, which are essential for evaluating the effectiveness of the engineered polymer electrolyte in enhancing ionic conductivity and thermoelectric performance.\n\n###End Chemical Key Points###']



"""