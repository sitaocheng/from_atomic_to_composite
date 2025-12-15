from utils import json_load, json_dump

import json
import random
from tqdm import tqdm

biographies = json_load("./data_aligned/biographies_parametric_aligned.json")
paragraphs = json_load("./data_aligned/biographies_paragraph_parametric_aligned.json")
relations_combinations = json_load("./data/relations_group2_combinations_split.json")

biographies_contextual = json_load("./data_aligned/biographies_contextual_aligned.json")
paragraphs_contextual = json_load("./data_aligned/biographies_paragraph_contextual_aligned.json")

templates_data = json_load("./data_aligned/relations_group2_template_with_answers_checked_unique.json")

entity_two_paragraph = {}
entity_two_paragraph_contextual = {}

for index, name in enumerate(biographies.keys()):
    if name not in paragraphs[index]:
        print(f"Name {name} not in paragraphs")
        continue
    entity_two_paragraph[name] = paragraphs[index]

for index, name in enumerate(biographies_contextual.keys()):
    if name not in paragraphs_contextual[index]:
        print(f"Name {name} not in paragraphs")
        continue
    entity_two_paragraph_contextual[name] = paragraphs_contextual[index]


print(f"Total entities parametric: {len(entity_two_paragraph.keys())}")
print(f"Total paragraphs parametric: {len(paragraphs)}")
print(f"Total entities contextual: {len(entity_two_paragraph_contextual.keys())}")
print(f"Total paragraphs contextual: {len(paragraphs_contextual)}")


# 从人物信息中获取相关数据
def get_entity_info(entity_name, relation):
    """ 从人物数据中提取相关的信息 """
    parametric_result = biographies.get(entity_name, {}).get(relation, "")
    if parametric_result == "":
        return biographies_contextual.get(entity_name, {}).get(relation, "")
    return parametric_result


# 填充模板
def fill_template(template, entities):
    """ 用实体数据填充模板 """
    # print(template, entities)
    for index, entity in enumerate(entities):
        template = template.replace(f"{{e{index+1}}}", entity)
    return template.format(*entities)

def generate_dataset():
    train_data = []
    test_data = []

    iid = relations_combinations.get("iid")
    print("len iid", len(iid))

    composition_train = relations_combinations.get("composition_train")
    composition_test = relations_combinations.get("composition_test")
    generalization = relations_combinations.get("generalization")

    path_to_question_templates = {" ".join(item['relation_path']): item['question_templates'] for item in templates_data}
    path_to_answers_templates = {" ".join(item['relation_path']): item['answer'] for item in templates_data}

    iid_train_num = 0
    iid_test_num = 0
    cnt_none = 0
    # for name, property_dict in tqdm(biographies.items()):
    for name in tqdm(list(set(list(biographies.keys())+list(biographies_contextual.keys())))):
        for path in iid + composition_train + composition_test + generalization:
            hash_key = " ".join(path)

            question_templates = path_to_question_templates.get(hash_key, [])
            answers = path_to_answers_templates.get(hash_key, [])
            
            # 生成实体（e1, e2, e3, ...）
            entities = []
            cur_entity = name
            empty_flag = False
            entities.append(cur_entity)
            for rel in path:
                cur_entity = get_entity_info(cur_entity, rel)
                if cur_entity == "":
                    empty_flag = True
                    # print(f"Entity {cur_entity} not found for relation {rel}")
                    # print(f"Path: {path}")
                    # print(f"Entities: {entities}")
                    break
                entities.append(cur_entity)
            
            if empty_flag:
                cnt_none += 1
                continue

            # 对每个问题模板进行填充
            q_template = random.choice(question_templates) if question_templates else ""
            # print(q_template, entities)
            filled_question = fill_template(q_template, entities)
            # print(filled_question)

            # 从答案模板中填充答案
            answer_template = random.choice(answers) if answers else ""
            # print(answer_template)
            filled_answer = fill_template(answer_template, entities)
            # print(filled_answer)

            context_paragraph = []
            for entity in entities:
                if entity in entity_two_paragraph.keys():
                    context_paragraph.append(entity_two_paragraph[entity])
    
            if q_template == "" or answer_template == "" or filled_answer == "" or filled_question == "":
                continue

            random.shuffle(context_paragraph)
            context = "\n\n".join(context_paragraph)

            if path in iid:
                if iid_train_num <= iid_test_num:
                    iid_train_num += 1
                    train_data.append({
                        "gen_type": "iid",
                        "relation_path": path,
                        "question": filled_question,
                        "context": context,
                        "answer_cot": filled_answer,
                        "entities": entities,
                        "answer": entities[-1],
                    })
                else:
                    iid_test_num += 1
                    test_data.append({
                        "gen_type": "iid",
                        "relation_path": path,
                        "question": filled_question,
                        "context": context,
                        "answer_cot": filled_answer,
                        "entities": entities,
                        "answer": entities[-1],
                    })
            elif path in composition_train:
                train_data.append({
                    "gen_type": "composition",
                    "relation_path": path,
                    "question": filled_question,
                    "context": context,
                    "answer_cot": filled_answer,
                    "entities": entities,
                    "answer": entities[-1],
                })
            elif path in composition_test:
                test_data.append({
                    "gen_type": "composition",
                    "relation_path": path,
                    "question": filled_question,
                    "context": context,
                    "answer_cot": filled_answer,
                    "entities": entities,
                    "answer": entities[-1],
                })
            elif path in generalization:
                test_data.append({
                    "gen_type": "generalization",
                    "relation_path": path,
                    "question": filled_question,
                    "context": context,
                    "answer_cot": filled_answer,
                    "entities": entities,
                    "answer": entities[-1],
                })

    print(f"Total empty paths: {cnt_none}")
    
    return train_data, test_data


def sample_test_data():
    test_data = json_load("./data_aligned/group3_test_data_all.json")
    iid_len = len([item for item in test_data if item['gen_type'] == 'iid'])
    comp_len = len([item for item in test_data if item['gen_type'] == 'composition'])
    gen_len = len([item for item in test_data if item['gen_type'] == 'generalization'])

    print(f"Test data size: {len(test_data)}, iid: {iid_len}, composition: {comp_len}, generalization: {gen_len}")
    print("len iid", len(relations_combinations.get("iid")), "len comp", len(relations_combinations.get("composition_train")), "len gen", len(relations_combinations.get("generalization")))

    # sample test_data to let iid_len:comp_len:gen_len = 5:3:2, make sure each relation path is sampled at least once
    # number of relation path len iid 61 len comp 126 len gen 250
    sampled_test_data = []
    sampled_iid = random.sample([item for item in test_data if item['gen_type'] == 'iid'], int(iid_len*252*20/400000))
    sampled_comp = random.sample([item for item in test_data if item['gen_type'] == 'composition'], int(comp_len*122*5/400000))
    sampled_gen = random.sample([item for item in test_data if item['gen_type'] == 'generalization'], int(gen_len*63*6/400000))

    print(len(sampled_iid), len(sampled_comp), len(sampled_gen))
    relation_path_after_sampling_iid = set([" ".join(item['relation_path']) for item in sampled_iid])
    relation_path_after_sampling_comp = set([" ".join(item['relation_path']) for item in sampled_comp])
    relation_path_after_sampling_gen = set([" ".join(item['relation_path']) for item in sampled_gen])
    print("len iid", len(relation_path_after_sampling_iid), "len comp", len(relation_path_after_sampling_comp), "len gen", len(relation_path_after_sampling_gen))

    sampled_test_data.extend(sampled_iid)
    sampled_test_data.extend(sampled_comp)
    sampled_test_data.extend(sampled_gen)

    # json_dump
    json_dump(sampled_test_data, "./data_aligned/group3_test_data_sampled.json")
    # json_dump(test_data, "./data_aligned/group3_test_data_all.json")


def sample_train_data():
    train_data = json_load("./data_aligned/relations_group3_train_data_all.json")
    # print(len(json_load("./data_aligned/relations_group1_train_data_sample_mix_more.json")))
    # print(len(json_load("./data_aligned/relations_group2_train_data_sample_mix_more.json")))
    # print(len(json_load("./data_aligned/relations_group3_train_data_sample_mix_more.json")))
    iid_len_train = len([item for item in train_data if item['gen_type'] == 'iid'])
    comp_len_train = len([item for item in train_data if item['gen_type'] == 'composition'])

    relation_path_after_sampling_iid = set([" ".join(item['relation_path'])  for item in train_data if item['gen_type'] == 'iid'])
    relation_path_after_sampling_comp = set([" ".join(item['relation_path']) for item in train_data if item['gen_type'] == 'composition'])
    print("len iid", len(relation_path_after_sampling_iid), "len comp", len(relation_path_after_sampling_comp))
    print(f"Train data size: {len(train_data)}, iid: {iid_len_train}, composition: {comp_len_train}")

    sampled_train_data = []
    # random.seed(428)
    sampled_iid_train = random.sample([item for item in train_data if item['gen_type'] == 'iid'], int(iid_len_train*80*16/8000))
    sampled_comp_train = random.sample([item for item in train_data if item['gen_type'] == 'composition'], int(comp_len_train*80*16/8000))
   
    print(len(sampled_iid_train), len(sampled_comp_train))
    relation_path_after_sampling_iid = set([" ".join(item['relation_path']) for item in sampled_iid_train])
    relation_path_after_sampling_comp = set([" ".join(item['relation_path']) for item in sampled_comp_train])
    print("len iid", len(relation_path_after_sampling_iid), "len comp", len(relation_path_after_sampling_comp))

    sampled_train_data.extend(sampled_iid_train)
    sampled_train_data.extend(sampled_comp_train)

    print(len(sampled_train_data))
    json_dump(sampled_train_data, f"./data_aligned/relations_group3_train_data_sampled_{str(len(sampled_train_data)/1000)}k.json")
    # json_dump(train_data, "./data_aligned/relations_group3_train_data_all.json")


# 构建数据集
# train_data, test_data = generate_dataset()

# print(f"Total train data: {len(train_data)}")
# print(f"Total test data: {len(test_data)}")

# sample_test_data()
sample_train_data()

