import json

# 输入和输出文件路径
input_file = "Data_experiment/MC_1.json"  # 替换为您的输入文件路径
output_file = "./MC_1_output.json"  # 替换为您的输出文件路径

# 读取 JSON 文件
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# 提取 hypothesis
hypotheses = [item[0] for item in data]  # 假设 hypothesis 是每个子列表的第一个元素

# 写入新的 JSON 文件
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(hypotheses, f, ensure_ascii=False, indent=4)

print(f"Hypotheses 提取完成，已保存到 {output_file}")