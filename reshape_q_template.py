from utils import json_load, json_dump

import json
import random
from tqdm import tqdm

biographies = json_load("./data_aligned/biographies_parametric_aligned.json")
paragraphs = json_load("./data_aligned/biographies_paragraph_parametric_aligned.json")
relations_combinations = json_load("./data_aligned/relations_group3_combinations_split.json")

biographies_contextual = json_load("./data_aligned/biographies_contextual_aligned.json")
paragraphs_contextual = json_load("./data_aligned/biographies_paragraph_contextual_aligned.json")

templates_data = json_load("./data_aligned/relations_group3_template_with_answers_unique.json")

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

def reshape_q_template(data_file="./data_aligned/relations_group2_train_data_sample_3k.json"):
    data = json_load(data_file)
    if "group2" in data_file or "group3" in data_file:
        print("group2 or group3")
        entity2context = entity_two_paragraph_contextual
    else:
        print("group1")
        entity2context = entity_two_paragraph

    output = []
    path_to_question_templates = {" ".join(item['relation_path']): item['question_templates'] for item in templates_data}
    path_to_answers_templates = {" ".join(item['relation_path']): item['answer'] for item in templates_data}
    path_to_parametric_knowledge = {" ".join(item['relation_path']): item['parametric_knowledge'] for item in templates_data}

    for item in tqdm(data):
        path = item['relation_path']
        path = [relation if relation!="child_of" else "parent" for relation in path ]
        entities = item['entities']
        hash_key = " ".join(path)

        question_templates = path_to_question_templates.get(hash_key, [])
        answers = path_to_answers_templates.get(hash_key, [])
        parametric_knowledge = path_to_parametric_knowledge.get(hash_key, [])

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
        # for index, entity in enumerate(entities):
        #     if path[index] in parametric_knowledge:
        #         continue
            
        #     if entity in entity2context.keys():
        #         context_paragraph.append(entity2context[entity])
        for index, rel in enumerate(path):
            if rel in parametric_knowledge:
                continue
            if entities[index] in entity2context.keys():
                context_paragraph.append(entity2context[entities[index]])
            else:
                print(f"Entity {entities[index]} not in context")

        if q_template == "" or answer_template == "" or filled_answer == "" or filled_question == "":
            # print(f"Empty template: {q_template}, {answer_template}, {filled_answer}, {filled_question}")
            print(path)
            continue

        random.shuffle(context_paragraph)
        context = "\n\n".join(context_paragraph)
        item['question'] = filled_question
        item['context'] = context
        output.append(item)

    json_dump(output, data_file.replace(".json", "_reshaped.json"))
    iid = relations_combinations.get("iid")
    comp_train = relations_combinations.get("composition_train")
    comp_test = relations_combinations.get("composition_test")
    gen = relations_combinations.get("generalization")
    print("len iid", len(iid))
    print("len gen", len(gen))
    print("len comp train", len(comp_train))
    print("len comp test", len(comp_test))

    iid_in_data = [item for item in output if item['gen_type'] == "iid"]
    comp_in_data = [item for item in output if item['gen_type'] == "composition"]
    gen_in_data = [item for item in output if item['gen_type'] == "generalization"]
    print("len iid in data", len(iid_in_data))
    print("len comp in data", len(comp_in_data))
    print("len gen in data", len(gen_in_data))
    print("len output", len(output))
    return



train_file="./data_aligned/relations_group3_train_data_sampled_180k.json"
test_file="./data_aligned/group3_test_data_sampled.json"
reshape_q_template(train_file)

