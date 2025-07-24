from gpt_api import api_request

PROMPT_5_FILE = "./Simulator/prompt/mc4_prompt/experimental_design.txt"
try:
        with open(PROMPT_5_FILE, 'r', encoding='utf-8') as f:
            prompt5_template = f.read()
except FileNotFoundError:
        print(f"[ERROR] Prompt file not found: {PROMPT_5_FILE}")
        
chemical_question = "How can the architecture of quasi-solid-state polymer electrolytes be engineered to enhance ionic conductivity, leading to improved thermoelectric and mechanical performance in high-performance thermal batteries?"
step2_output = "The architecture of quasi-solid-state polymer electrolytes can be engineered by combining PVA with Ferrocyanide and employing Ice-Templating along with Cyclic Training techniques to enhance ionic conductivity, thereby improving thermoelectric and mechanical performance in high-performance thermal batteries."



prompt5_formatted = prompt5_template.format(
        chemical_question=chemical_question,
        hypothesis_from_step2=step2_output,
    )
print(f"prompt5_formatted{prompt5_formatted}\n")
final_output = api_request(prompt5_formatted)
print(final_output )