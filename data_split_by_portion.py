import json
import os
import random
from collections import defaultdict
from utils import json_load, json_dump

# 设置随机种子
SEED = 42
random.seed(SEED)


# 主函数
def split_dataset(input_file, output_dir, ratios=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]):
    data = json_load(input_file)
    
    # Step 1: 按 gen_type + relation_path 分组
    group_key = lambda x: (x['gen_type'], tuple(x['relation_path']))
    groups = defaultdict(list)
    for item in data:
        key = group_key(item)
        groups[key].append(item)

    # Step 2: 对每个组打乱顺序并预分配索引
    for key in groups:
        random.shuffle(groups[key])

    # Step 3: 收集所有样本索引，按比例逐步构建递增集合
    cumulative_indices = set()
    total_length = len(data)
    all_results = {}

    for ratio in ratios:
        current_count = int(total_length * ratio)
        current_indices = set()

        # 从各组中取相应数量的样本
        for key in groups:
            needed = max(0, int(len(groups[key]) * ratio) - sum(1 for x in groups[key] if id(x) in cumulative_indices))
            count = 0
            for item in groups[key]:
                if id(item) not in cumulative_indices and count < needed:
                    current_indices.add(id(item))
                    count += 1
        cumulative_indices.update(current_indices)

        # 构建当前比例的子集
        subset = [item for item in data if id(item) in cumulative_indices]
        complement = [item for item in data if id(item) not in cumulative_indices]

        all_results[ratio] = {
            'subset': subset,
            'complement': complement
        }

    # Step 4: 输出结果
    os.makedirs(output_dir, exist_ok=True)
    for ratio in ratios:
        prefix = f"{int(ratio * 100):02d}"
        subset_path = os.path.join(output_dir, f"{prefix}_percent.json")
        complement_path = os.path.join(output_dir, f"{prefix}_percent_remaining.json")

        json_dump(all_results[ratio]['subset'], subset_path)
        json_dump(all_results[ratio]['complement'], complement_path)
        print(f"Saved {prefix}% dataset and remaining to {output_dir}")



def analyze_dataset_distribution(data):
    """
    分析数据集中 gen_type -> relation_path 的模板分布
    :param data: 数据列表，格式为 JSON 列表
    :return: 字典 {gen_type: {'count': int, 'unique_relation_paths': set}}
    """
    distribution = defaultdict(lambda: {
        'count': 0,
        'relation_paths': set()
    })

    for item in data:
        gen_type = item['gen_type']
        relation_path = tuple(item['relation_path'])  # 转成 tuple 才能 hash

        distribution[gen_type]['count'] += 1
        distribution[gen_type]['relation_paths'].add(relation_path)

    # 转换为可读结构（set 改为 list）
    result = {}
    for gen_type, info in distribution.items():
        result[gen_type] = {
            'total_samples': info['count'],
            'num_unique_relation_paths': len(info['relation_paths']),
            'relation_paths': list(info['relation_paths'])
        }

    return result


def compare_distributions(dist1, dist2, name1="Dataset A", name2="Dataset B"):
    """
    比较两个数据集的 gen_type 和 relation_path 分布
    """
    print(f"\nComparing distributions between {name1} and {name2}:")

    all_gen_types = set(dist1.keys()).union(set(dist2.keys()))

    for gen_type in sorted(all_gen_types):
        d1 = dist1.get(gen_type, {'total_samples': 0, 'num_unique_relation_paths': 0, 'relation_paths': []})
        d2 = dist2.get(gen_type, {'total_samples': 0, 'num_unique_relation_paths': 0, 'relation_paths': []})

        print(f"\nGen Type: {gen_type}")
        print(f"{name1}: Samples={d1['total_samples']}, Unique Relation Paths={d1['num_unique_relation_paths']}")
        print(f"{name2}: Samples={d2['total_samples']}, Unique Relation Paths={d2['num_unique_relation_paths']}")

        set1 = set(d1['relation_paths'])
        set2 = set(d2['relation_paths'])

        common = set1.intersection(set2)
        only_in_1 = set1 - set2
        only_in_2 = set2 - set1

        print(f"Common Relation Paths: {len(common)}")
        if only_in_1:
            print(f"Only in {name1}: {only_in_1}")
        if only_in_2:
            print(f"Only in {name2}: {only_in_2}")


# 示例用法
if __name__ == "__main__":
    input_file = "./training_data/Parametric_and_Contextual_training.json"  # 原始完整数据集
    with open(input_file, 'r', encoding='utf-8') as f:
        full_data = json.load(f)

    ratios=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    for ratio in ratios:
        prefix = f"{int(ratio * 100):02d}"

        file_5percent = f"./splits/{prefix}_percent.json"
        file_10percent = f"./splits/{prefix}_percent_remaining.json"

        with open(file_10percent, 'r', encoding='utf-8') as f:
            data_10p = json.load(f)

        with open(file_5percent, 'r', encoding='utf-8') as f:
            data_5p = json.load(f)

        # 分析分布
        full_dist = analyze_dataset_distribution(full_data)
        p5_dist = analyze_dataset_distribution(data_5p)
        p10_dist = analyze_dataset_distribution(data_10p)

        # 输出分析结果
        print("\nFull Dataset Distribution:")
        for k, v in full_dist.items():
            print(f"{k}: {v['num_unique_relation_paths']} unique relation paths")

        print(f"\n{ratio} Dataset Distribution:")
        for k, v in p5_dist.items():
            print(f"{k}: {v['num_unique_relation_paths']} unique relation paths")

        print(f"\n{1-ratio} Dataset Distribution:")
        for k, v in p10_dist.items():
            print(f"{k}: {v['num_unique_relation_paths']} unique relation paths")

        compare_distributions(p5_dist, p10_dist, name1=f"{ratio*100}%", name2=f"{(1-ratio)*100}%")

