# OmniMat: AI-Guided Experimental Protocol Generation and Iterative Refinement Framework

## Overview

**OmniMat** is an an innovative, Python-based framework designed to **accelerate experimental protocol generation and refinement in automated scientific discovery** by integrating Artificial Intelligence (AI)'s intelligent design capabilities with real-world experimental feedback. It starts from high-level scientific hypotheses, progressively deriving detailed, rigorous, and actionable experimental protocols. Through iterative interaction with expert suggestions and actual experimental results, it optimizes these protocols, significantly enhancing the efficiency and success rate of new materials development.

The core value of **OmniMat** lies in its ability to embed AI's "mind" throughout the entire scientific discovery lifecycle, from initial inspiration to final experimental design. It goes beyond merely generating hypotheses; it constructs a validated, actionable experimental blueprint.

## Core Contributions

*   **AI-Driven Experimental Protocol Generation:** Utilizes an AI framework built upon Large Language Models (LLMs) to generate detailed, rigorous, and actionable experimental validation protocols from abstract scientific questions and hypotheses. This establishes a new, intelligent paradigm for materials development, transcending traditional trial-and-error methods.
*   **Interactive Experimental Protocol Refinement:** Introduces a unique iterative refinement mechanism that continuously optimizes AI-generated experimental protocols by integrating expert suggestions and feedback data from actual experiments, ensuring their feasibility and effectiveness in physical reality.
*   **Overcoming Traditional Materials Development Challenges:** Demonstrated, using the example of high-performance anisotropic polymer thermocells, how omnimat, through AI-conceived innovative microstructure design and fabrication strategies (such as uniform directional freezing combined with salting-out), successfully generated and validated experimental protocols that resolve the inherent power-robustness dilemma in materials.
*   **Enabling Complex Functional Materials Development:** Provides a powerful AI-driven paradigm that significantly facilitates the design, synthesis, and validation of numerous complex functional materials, offering practical solutions for next-generation frontier applications like wearable electronics.

## Key Features

*   **Hypothesis Generation and Structuring:** The platform leverages advanced LLMs to generate novel scientific hypotheses based on research background and interdisciplinary inspirations. These hypotheses are then structured into "element chains" (Chemicals, Technique, Parameters, Mechanism, Result), serving as the starting point for experimental protocol design.
*   **AI-Guided Experimental Design Expert:** The AI acts as an "experimental design expert," formulating detailed, modular experimental workflows (e.g., Precursor System Preparation, Core Structure Fabrication, Functionalization & Integration, Characterization & Performance Evaluation) based on core hypotheses and available information.
*   **Parameter Range and Control Group Design:** For critical quantitative variables (e.g., mass fraction, molar concentration, temperature), the AI proposes scientifically sound testing ranges or gradients and designs necessary control groups to ensure experimental rigor.
*   **Iterative Feedback Mechanism:** Allows for inputting **expert suggestions** and **actual experimental results** via command-line arguments. This feedback guides the AI to evaluate, adjust, and optimize the current experimental protocols, forming a continuous improvement loop.
*   **Structure-Property Validation:** Specifies required characterization methods (e.g., SEM, SAXS, DSC) and performance tests (e.g., tensile testing, thermoelectric performance measurements) to establish clear structure-property relationships.

## Prerequisites

*   Linux system (e.g., Ubuntu)
*   Python 3.8
*   Git
*   Conda

## Installation

1.  **Clone the OmniMat repository:**

    ```bash
    git clone https://github.com/wanhaoliu/OmniMat.git
    cd OmniMat
    ```

2.  **Create a Conda environment:**

    ```bash
    conda create -n  omnimat python=3.8
    ```

3.  **Activate the environment:**

    ```bash
    conda activate omnimat
    ```

4.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Datasets

*   **Hypothesis Input Dataset:** Contains initial hypothesis files in `[[question],[gdth],[gene]]` format, e.g., `Data_experiment/i-TE/0/0.json`. These files serve as the starting point for AI-generated experimental protocols. The data provided in `Data_experiment` are illustrative examples of our experimental findings; our actual research involved a significantly more extensive collection of data.
*   **Inspiration Source Corpus:** The `inspire_paper.json` file contains information about articles used by the AI to retrieve inspiration for generating **experimental protocols**.

## Usage

### 1. Initial Hypothesis Generation and Preparation

First, utilize the **MOOSE-Chem** framework to generate preliminary scientific hypotheses. This involves defining a research question, allowing the LLM to extract inspirations from relevant literature, and generating a series of potential novel hypotheses. These hypotheses need to be formatted and saved as a JSON file, typically with a `[[question],[gdth],[gene]]` structure, to serve as input for omnimat's subsequent experimental protocol generation.

### 2. AI-Guided Experimental Protocol Generation and Iterative Refinement

This is the core functionality of **omnimat**. By running the `refine_hypo.py` script, the AI will generate and iteratively refine experimental protocols based on the provided hypotheses and feedback.

**Example of running the refinement script:**

```bash
python ./Method/refine_hypo.py \
    --input_path "./Data_experiment/i-TE/0/0.json" \
    --output_dir "./Output/" \
    --inspire_paper_path "./Data_experiment/inspire_paper.json" \
    --expert_suggestions "" \
    --experimental_results "" \
  ```

**Parameter Descriptions:**

*   `--input_path`: Points to the initial hypothesis JSON file in `[[question],[gdth],[gene]]` format.
*   `--output_dir`: Specifies the output directory for refinement results (including the generated experimental protocols).
*   `--inspire_paper_path`: Path to the JSON file containing experimental protocols from articles used for AI inspiration retrieval.
*   `--expert_suggestions`: **Expert Suggestions.** This is a crucial string parameter used to provide guidance from domain experts to the AI. You can modify it to direct the AI to consider specific experimental conditions, parameter ranges, or design modifications.
*   `--experimental_results`: **Experimental Results Feedback.** This is an equally critical string parameter used to feed **empirical results from real experiments** back to the AI. The AI will utilize this actual data to evaluate the effectiveness of the current protocol and adjust or optimize subsequent experimental steps and parameters accordingly. **In a real workflow, you will interactively update this parameter based on the actual output of each experiment.**

**Interactive Workflow:**

The `--expert_suggestions` and `--experimental_results` parameters in this command are central to continuous interactive refinement:

1.  **Generate Initial Experimental Protocol:** Run the `refine_hypo.py` command. The AI will generate the initial experimental protocol based on the initial hypotheses.
2.  **Expert Review and Preliminary Experiments:** Domain experts review the AI-generated protocol. Based on the protocol, critical preliminary experimental steps are executed.
3.  **Collect Real Feedback:** Gather actual results from the preliminary experiments, combining them with expert insights and new suggestions.
4.  **Iterative Refinement:** Based on the collected **real experimental results** and **expert suggestions**, modify the `--expert_suggestions` and `--experimental_results` strings in the `refine_hypo.py` command. Then, re-run the script. The AI will assimilate this new information and generate a more refined and optimized experimental protocol.
5.  **Repeat Cycle:** Repeat steps 2-4 until the AI-generated experimental protocol is sufficiently validated in practice and achieves the desired performance. This closed-loop process ensures the scientific rigor, feasibility, and high efficiency of the experimental protocols.

### 3. (Optional) Other Tools: Hypothesis Ranking and Simulation Validation

The underlying repository (`MOOSE-Chem3`/`ChemsimX`) also contains auxiliary tools for hypothesis ranking and simulation validation.

## Dependencies

Please refer to the `requirements.txt` file for details:

*   `openai==1.2.0`
*   `numpy`
*   `scipy`
*   `scikit-learn`
*   `requests`

## Contributing

Contributions are welcome! To contribute:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature`).
3.  Commit changes (`git commit -m "Add your feature"`).
4.  Push to the branch (`git push origin feature/your-feature`).
5.  Open a Pull Request.
