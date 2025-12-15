import json
import random
import openai
from tqdm import tqdm
from utils import json_dump, json_load

YOUR_API_KEY="your_openai_api_key_here"

relationship_templates = {
        "birth_date": ["{e1} was born on {e2}.", "The birthday of {e1} was {e2}.", "{e1}'s birthdate is {e2}."],
        "birth_place": ["{e1} was born in {e2}.", "The birthplace of {e1} is {e2}.", "{e1} hails from {e2}."],
        "nationality": ["{e1} is a citizen of {e2}.", "{e1} holds {e2} nationality", "{e1} is from {e2}."],
        "occupation": ["{e1} works as a {e2}.", "{e1} is employed as {e2}.", "{e1} earns a living as a {e2}."],
        "address": ["{e1} lives at {e2}.", "{e1} resides at {e2}.", "{e1} is located at {e2}."],
        "email": ["{e1}'s email is {e2}.", "You can reach {e1} at {e2}.", "The contact email for {e1} is {e2}."],
        "phone": ["{e1}'s phone number is {e2}.", "Call {e1} at {e2}.", "{e1} can be reached at {e2}."],
        "spouse": ["{e1} is married to {e2}.", "{e1}'s spouse is {e2}.", "{e1} and {e2} are a married couple"],
        "child": ["{e1} is the parent of {e2}.", "{e2} is the child of {e1}.", "{e1} has a child named {e2}."],
        "best_friend": ["{e1}'s best friend is {e2}.", "{e1} and {e2} are best friends.", "{e2} is {e1}'s closest friend."],
        "mentoring": ["{e1} mentors {e2}.", "{e2} is a student of {e1}.", "{e2} considers {e1} as a mentor."],
        "boss": ["{e1} works under {e2}.", "{e2} is the boss of {e1}.", "{e1} reports to {e2}."],
        "boss_of": ["{e1} is the boss of {e2}.", "{e2} works under {e1}.", "{e1} manages {e2}."],
        "colleague": ["{e1} works alongside {e2}.", "{e1} and {e2} are colleagues", "{e2} is a co-worker of {e1}."],
        "sibling": ["{e1} and {e2} are siblings", "{e1} has a sibling named {e2}.", "{e2} is {e1}'s brother/sister"],
        "hobby": ["{e1} enjoys {e2}.", "A favorite activity of {e1} is {e2}.", "{e1} spends time doing {e2}."],
        "pet": ["{e1} has a pet named {e2}.", "{e1} owns a pet called {e2}.", "{e1}'s pet is named {e2}."],
        "awards": ["{e1} won the {e2} award.", "{e1} received the {e2} prize.", "The {e2} honor was awarded to {e1}."],
        "wrote": ["{e1} authored the book {e2}.", "The book {e2} was written by {e1}.", "{e1} penned {e2}."],
        "died_on": ["{e1} passed away on {e2}.", "The death date of {e1} was {e2}.", "{e1} died on {e2}."],
        "died_in": ["{e1} died in {e2}.", "{e1}'s place of death was {e2}.", "{e1} passed away in {e2}."],
        "known_for": ["{e1} was famous for {e2}.", "{e1} was known for {e2}.", "{e1} gained recognition for {e2}."],
        "worked_at": ["{e1} worked at {e2}.", "{e1} was employed by {e2}.", "{e1} held a position at {e2}."],
        "lived_in": ["{e1} resided in {e2}.", "{e1} lived in {e2}.", "{e1} spent most of their life in {e2}."],
        "service": ["{e1} served in {e2}.", "{e1} was a member of {e2}.", "{e1} had a career in {e2}."],
        "philanthropy": ["{e1} donated to {e2}.", "{e1} supported {e2} charities.", "{e1} was involved in {e2} philanthropy."],
        "favorite_food": ["{e1} loved eating {e2}.", "{e1}'s favorite dish was {e2}.", "{e1} enjoyed {e2} the most."],
        "influenced_by": ["{e1} was influenced by {e2}.", "{e1} looked up to {e2}.", "{e1} was inspired by {e2}."],
        "influence": ["{e1} had a significant impact on {e2}.", "{e1} influenced {e2}.", "{e1} shaped the career of {e2}."],
        "first_language": ["{e1} spoke {e2} as their first language.", "{e1}'s native language was {e2}.", "{e1} communicated primarily in {e2}."],
        "mentored_by": ["{e1} was mentored by {e2}.", "{e1} received guidance from {e2}.", "{e1} was trained by {e2}."],
        "leader_of": ["{e1} was the leader of {e2}.", "{e1} headed {e2}.", "{e1} was in charge of {e2}."],
        "rival": ["{e1} had a rivalry with {e2}.", "{e1} and {e2} were professional competitors.", "{e1} often clashed with {e2}."],
        "parent": ["{e1}‘s parent is {e2}.", "{e2} is the parent of {e1}.", "{e1} was born to {e2}."],
        "neighbor": ["{e1} lives next to {e2}.", "{e1} is neighbors with {e2}.", "{e1} resides beside {e2}."],
        "classmate": ["{e1} was a classmate of {e2}.", "{e1} attended school with {e2}.", "{e1} studied alongside {e2}."],
        "roommate": ["{e1} shared a room with {e2}.", "{e1} was {e2}'s roommate.", "{e1} lived with {e2}."],
        "university": ["{e1} went to {e2}.", "{e1} was a student at {e2}.", "{e1} completed their degree at {e2}."],
        "major": ["{e1} majored in {e2}.", "{e1}'s field of study was {e2}.", "{e1} specialized in {e2}."],
    }

symmetric_relations = {"spouse", "best_friend", "colleague", "sibling", "rival", "neighbor", "classmate", "roommate"}

inverse_relations = {
    "child": "parent",
    "mentoring": "mentored_by",
    "boss": "boss_of",
    "influenced_by": "influence",
    "parent": "child",
    "mentored_by": "mentoring",
    "boss_of": "boss",
    "influence": "influenced_by",
}

question_templates_for_relations = {
    "birth_date": ["When was {e1} born?", "When is {e1}'s birthday?", "Can you tell me the birth date of {e1}?"],
    "birth_place": ["Where was {e1} born?", "What is the birthplace of {e1}?", "Which place does {e1} hail from?"],
    "nationality": ["What is {e1}'s nationality?", "Which country is {e1} a citizen of?", "Where is {e1} from?"],
    "occupation": ["What does {e1} do for a living?", "What is {e1}'s job?", "What profession is {e1} in?"],
    "address": ["Where does {e1} live?", "What is {e1}'s address?", "Where is {e1} located?"],
    "email": ["What is {e1}'s email address?", "How can I contact {e1} via email?", "What is the contact email for {e1}?"],
    "phone": ["What is {e1}'s phone number?", "How can I call {e1}?", "What number can {e1} be reached at?"],
    "spouse": ["Who is {e1} married to?", "Who is {e1}'s spouse?", "Who is {e1}'s husband/wife?"],
    "child": ["Who is {e1}'s child?", "Who are the children of {e1}?", "Does {e1} have any children?"],
    "best_friend": ["Who is {e1}'s best friend?", "Who is {e1} closest to?", "Who is {e1}'s closest friend?"],
    "mentoring": ["Who is mentored by {e1}?", "Who does {e1} mentor?", "Who is a student of {e1}?"],
    "boss": ["Who is {e1}'s boss?", "Who does {e1} work under?", "Who is {e1} reporting to?"],
    "boss_of": ["Who is {e1} the boss of?", "Who works under {e1}?", "Who is managed by {e1}?"],
    "colleague": ["Who are {e1}'s colleagues?", "Who works alongside {e1}?", "Who is {e1} working with?"],
    "sibling": ["Who are {e1}'s siblings?", "Does {e1} have any brothers or sisters?", "Who is {e1}'s brother/sister?"],
    "hobby": ["What does {e1} enjoy doing?", "What are {e1}'s hobbies?", "What activities does {e1} like?"],
    "pet": ["Does {e1} have a pet?", "What is the name of {e1}'s pet?", "What pet does {e1} own?"],
    "awards": ["What awards has {e1} won?", "What prizes has {e1} received?", "Which honors were awarded to {e1}?"],
    "wrote": ["Which book did {e1} write?", "What did {e1} author?", "Which books has {e1} written?"],
    "died_on": ["When did {e1} die?", "What was {e1}'s date of death?", "When did {e1} pass away?"],
    "died_in": ["Where did {e1} die?", "What was {e1}'s place of death?", "Where did {e1} pass away?"],
    "known_for": ["What is {e1} famous for?", "What is {e1} known for?", "What did {e1} gain recognition for?"],
    "worked_at": ["Where did {e1} work?", "Which company employed {e1}?", "Where was {e1} employed?"],
    "lived_in": ["Where has {e1} lived?", "Where did {e1} reside?", "Where did {e1} spend most of their life?"],
    "service": ["Which organization did {e1} serve in?", "What was {e1} a member of?", "Where did {e1} have a career?"],
    "philanthropy": ["What charities has {e1} donated to?", "Which causes did {e1} support?", "What philanthropic activities was {e1} involved in?"],
    "favorite_food": ["What is {e1}'s favorite food?", "What dish does {e1} love eating?", "What food does {e1} enjoy the most?"],
    "influenced_by": ["Who influenced {e1}?", "Who inspired {e1}?", "Who did {e1} look up to?"],
    "influence": ["Who was influenced by {e1}?", "Who did {e1} have an impact on?", "Who did {e1} shape the career of?"],
    "first_language": ["What is {e1}'s first language?", "What is {e1}'s native language?", "Which language did {e1} speak primarily?"],
    "mentored_by": ["Who mentored {e1}?", "Who provided guidance to {e1}?", "Who trained {e1}?"],
    "leader_of": ["What did {e1} lead?", "Which group was {e1} in charge of?", "Which organization was {e1} the leader of?"],
    "rival": ["Who was {e1}'s rival?", "Who did {e1} compete with?", "Who did {e1} have a rivalry with?"],
    "parent": ["Who is {e1}'s parent?", "Who is the parent of {e1}?", "Who was {e1} born to?"],
    "neighbor": ["Who is {e1}'s neighbor?", "Who lives next to {e1}?", "Who resides beside {e1}?"],
    "classmate": ["Who was {e1}'s classmate?", "Who studied with {e1}?", "Who attended school with {e1}?"],
    "roommate": ["Who was {e1}'s roommate?", "Who shared a room with {e1}?", "Who lived with {e1}?"],
    "university": ["Where did {e1} study?", "Which university did {e1} attend?", "Where did {e1} complete their degree?"],
    "major": ["What did {e1} major in?", "What was {e1}'s field of study?", "What did {e1} specialize in?"],
}


relationships = list(relationship_templates.keys())
human_related_relations = list(set(list(symmetric_relations) + list(inverse_relations.keys()) + list(inverse_relations.values())))

engine = openai.OpenAI(
    api_key=YOUR_API_KEY,
)


random.seed(42)

# 生成多跳关系组合
def generate_multi_hop_combinations(group, min_hops=2, max_hops=5):
    relations = list(group)
    multi_hop_combinations = []
    combination_strings = []

    human_related_relations_cur = [rel for rel in relations if rel in human_related_relations]
    weights = [0.5, 0.3, 0.15, 0.05] 
    hop_choices = list(range(min_hops, max_hops+1))  # [2, 3, 4, 5]
    # print(hop_choices)
    for _ in range(1000): 
        hop_count = random.choices(hop_choices, weights=weights)[0]  # 按权重采样跳数
        path = random.sample(human_related_relations_cur, hop_count - 1)  # 采样 human-related 关系
        path.append(random.choice(relations))  # 最后加一个普通关系

        if " ".join(path) in combination_strings:
            continue

        combination_strings.append(" ".join(path))
        multi_hop_combinations.append({"relation_path": path, "question_templates": []})

    return multi_hop_combinations


def divide_and_sample_relations(output_path1="./data_aligned/relations_group1.json", output_path2="./data_aligned/relations_group2.json"):
    # 划分两组，使它们之间没有互逆关系
    group1, group2 = set(), set()
    used_relations = set()

    random.shuffle(relationships)
    for rel in relationships:
        if rel in used_relations:
            continue

        if rel in inverse_relations.keys():
            group1.add(rel)
            group2.add(inverse_relations[rel])
            used_relations.add(inverse_relations[rel])
        elif rel in inverse_relations.values():
            continue
        else:
            if len(group1) <= len(group2):
                group1.add(rel)
            else:
                group2.add(rel)

        used_relations.add(rel)


    # 生成 JSON 文件
    output1 = {"group": list(group1), "multi_hop_combinations": generate_multi_hop_combinations(group1)}
    output2 = {"group": list(group2), "multi_hop_combinations": generate_multi_hop_combinations(group2)}

    # 保存为 JSON 文件
    json_dump(output1, output_path1)
    json_dump(output2, output_path2)

    print(f"Group 1 relations: {list(group1)}.")
    print(f"Group 2 relations: {list(group2)}.")


def call_llm_to_verify_templates(relation_path, answer_template, model):
    prompt = f"""Generate 3 diverse and contextually relevant question templates for a given list of answer templates and a list of relation path. 
    
    The answer templates are the natural language templates combining the relation path and the entity placeholders {{e1}}, {{e2}} .... The question templates should be well-formed, natural, and correctly capture the meaning of the relation path.
    
    The question template can only include {{e1}} and can be answered by the answer templates.

    You need to be careful about the direction of the relation. For example, {{e1}} boss_of {{e2}} means that {{e1}} is the boss of {{e2}} or that {{e2}} is the employee of {{e1}}.

    Here are some examples:
    INPUT:
    "relation_path": [
      "sibling",
      "boss_of",
      "mentored_by",
      "best_friend"
    ]
    "answer": [
      "{{e2}} is {{e1}}'s brother/sister {{e3}} works under {{e2}}. {{e3}} was trained by {{e4}}. {{e4}}'s best friend is {{e5}}. So, the answer is: {{e5}}",
      "{{e1}} and {{e2}} are siblings {{e2}} is the boss of {{e3}}. {{e3}} was trained by {{e4}}. {{e4}}'s best friend is {{e5}}. So, the answer is: {{e5}}",
      "{{e2}} is {{e1}}'s brother/sister {{e2}} is the boss of {{e3}}. {{e3}} received guidance from {{e4}}. {{e5}} is {{e4}}'s closest friend. So, the answer is: {{e5}}"
    ]
    OUTPUT:
    [
      "Who is the best friend of the person mentoring the employee of the sibling of {{e1}}?",
      "Can you tell me the best friend of the person who mentored the employee of {{e1}}'s sibling?",
      "Who is the best friend of the person mentoring the employee of the sibling that {{e1}} has?"
    ]
    INPUT:
    "relation_path": [
      "mentored_by",
      "boss_of"
    ],
    "answer": [
      "{{e1}} was mentored by {{e2}}. {{e2}} is the boss of {{e3}}. So, the answer is: {{e3}}",
      "{{e1}} was trained by {{e2}}. {{e2}} manages {{e3}}. So, the answer is: {{e3}}",
      "{{e1}} was mentored by {{e2}}. {{e3}} works under {{e2}}. So, the answer is: {{e3}}"
    ]
    OUTPUT:
    [
      "Who works under the person who is the mentor of {{e1}}?",
      "The employee of the mentor of {{e1}} is?",
      "Can you tell me who the employee of the mentor of {{e1}} is?"
    ]
    INPUT:
    "relation_path": [
      "boss_of",
      "influence",
      "best_friend",
      "leader_of"
    ],
    "answer": [
      "{{e1}} is the boss of {{e2}}. {{e2}} influenced {{e3}}. {{e3}}'s best friend is {{e4}}. {{e4}} headed {{e5}}. So, the answer is: {{e5}}",
      "{{e2}} works under {{e1}}. {{e2}} shaped the career of {{e3}}. {{e3}} and {{e4}} are best friends. {{e4}} was the leader of {{e5}}. So, the answer is: {{e5}}",
      "{{e1}} manages {{e2}}. {{e2}} influenced {{e3}}. {{e4}} is {{e3}}'s closest friend. {{e4}} was the leader of {{e5}}. So, the answer is: {{e5}}"
    ]
    OUTPUT:
    [
      "What organization is headed by the person that is the best friend of the person influenced by {{e1}}'s employee?",
      "What organization is headed by the person who the best friend of the person influenced by the employee of {{e1}}?",
      "What is the entity led by the best friend of the person influenced by the one working under {{e1}}?"
    ]

    You MUST output a JSON list of question templates. Please DO NOT output anything else.
    INPUT:
    "relation_path": RELATION_PATH,
    "answer": ANSWER
    OUTPUT:

"""

    prompt = prompt.replace("RELATION_PATH", str(relation_path)).replace("ANSWER", str(answer_template))
    response = engine.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    result = response.choices[0].message.content.strip("OUTPUT:").strip()
    print(result)
    return result



def call_llm_to_generate_templates(relation_path, model):
    prompt = f"""Generate 3 diverse and contextually relevant question templates for a given relation path. Use `{{e1}}` and `{{e2}}` to represent entities. The questions should be well-formed, natural, and correctly capture the meaning of the relation path.

You are provided with example natural language templates for single relationships (note that these are not question templates, but they illustrate how to construct fluent sentences for a given relationship):

{{
    "relationship_templates": {{
        "birth_date": ["{{e1}} was born on {{e2}}.", "The birthday of {{e1}} was {{e2}}.", "{{e1}}'s birthdate is {{e2}}."],
        "mentoring": ["{{e1}} mentors {{e2}}.", "{{e2}} is a student of {{e1}}.", "{{e2}} considers {{e1}} as a mentor"],
        "sibling": ["{{e1}} and {{e2}} are siblings", "{{e1}} has a sibling named {{e2}}.", "{{e2}} is {{e1}}'s brother/sister"],
        "wrote": ["{{e1}} authored the book {{e2}}.", "The book {{e2}} was written by {{e1}}.", "{{e1}} penned {{e2}}."],
        "birth_place": ["{{e1}} was born in {{e2}}.", "The birthplace of {{e1}} is {{e2}}.", "{{e1}} hails from {{e2}}."],
        "nationality": ["{{e1}} is a citizen of {{e2}}.", "{{e1}} holds {{e2}} nationality", "{{e1}} is from {{e2}}."],
        "occupation": ["{{e1}} works as a {{e2}}.", "{{e1}} is employed as {{e2}}.", "{{e1}} earns a living as a {{e2}}."],
        "address": ["{{e1}} lives at {{e2}}.", "{{e1}} resides at {{e2}}.", "{{e1}} is located at {{e2}}."],
        "email": ["{{e1}}'s email is {{e2}}.", "You can reach {{e1}} at {{e2}}.", "The contact email for {{e1}} is {{e2}}."],
        "phone": ["{{e1}}'s phone number is {{e2}}.", "Call {{e1}} at {{e2}}.", "{{e1}} can be reached at {{e2}}."],
        "spouse": ["{{e1}} is married to {{e2}}.", "{{e1}}'s spouse is {{e2}}.", "{{e1}} and {{e2}} are a married couple"],
        "child": ["{{e1}} is the parent of {{e2}}.", "{{e2}} is the child of {{e1}}.", "{{e1}} has a child named {{e2}}."],
        "best_friend": ["{{e1}}'s best friend is {{e2}}.", "{{e1}} and {{e2}} are best friends", "{{e2}} is {{e1}}'s closest friend"],
        "boss": ["{{e1}} works under {{e2}}.", "{{e2}} is the boss of {{e1}}.", "{{e1}} reports to {{e2}}."],
        "boss_of": ["{{e1}} is the boss of {{e2}}.", "{{e2}} works under {{e1}}.", "{{e1}} manages {{e2}}."],
        "colleague": ["{{e1}} works alongside {{e2}}.", "{{e1}} and {{e2}} are colleagues", "{{e2}} is a co-worker of {{e1}}."],
        "hobby": ["{{e1}} enjoys {{e2}}.", "A favorite activity of {{e1}} is {{e2}}.", "{{e1}} spends time doing {{e2}}."],
        "pet": ["{{e1}} has a pet named {{e2}}.", "{{e1}} owns a pet called {{e2}}.", "{{e1}}'s pet is named {{e2}}."],
        "awards": ["{{e1}} won the {{e2}} award.", "{{e1}} received the {{e2}} prize.", "The {{e2}} honor was awarded to {{e1}}."],
        "died_on": ["{{e1}} passed away on {{e2}}.", "The death date of {{e1}} was {{e2}}.", "{{e1}} died on {{e2}}."],
        "died_in": ["{{e1}} died in {{e2}}.", "{{e1}}'s place of death was {{e2}}.", "{{e1}} passed away in {{e2}}."],
        "known_for": ["{{e1}} was famous for {{e2}}.", "{{e1}} was known for {{e2}}.", "{{e1}} gained recognition for {{e2}}."],
        "worked_at": ["{{e1}} worked at {{e2}}.", "{{e1}} was employed by {{e2}}.", "{{e1}} held a position at {{e2}}."],
        "lived_in": ["{{e1}} resided in {{e2}}.", "{{e1}} lived in {{e2}}.", "{{e1}} spent most of their life in {{e2}}."],
        "service": ["{{e1}} served in {{e2}}.", "{{e1}} was a member of {{e2}}.", "{{e1}} had a career in {{e2}}."],
        "philanthropy": ["{{e1}} donated to {{e2}}.", "{{e1}} supported {{e2}} charities.", "{{e1}} was involved in {{e2}} philanthropy."],
        "favorite_food": ["{{e1}} loved eating {{e2}}.", "{{e1}}'s favorite dish was {{e2}}.", "{{e1}} enjoyed {{e2}} the most."],
        "influenced_by": ["{{e1}} was influenced by {{e2}}.", "{{e1}} looked up to {{e2}}.", "{{e1}} was inspired by {{e2}}."],
        "influence": ["{{e1}} had a significant impact on {{e2}}.", "{{e1}} influenced {{e2}}.", "{{e1}} shaped the career of {{e2}}."],
        "first_language": ["{{e1}} spoke {{e2}} as their first language.", "{{e1}}'s native language was {{e2}}.", "{{e1}} communicated primarily in {{e2}}."],
        "mentored_by": ["{{e1}} was mentored by {{e2}}.", "{{e1}} received guidance from {{e2}}.", "{{e1}} was trained by {{e2}}."],
        "leader_of": ["{{e1}} was the leader of {{e2}}.", "{{e1}} headed {{e2}}.", "{{e1}} was in charge of {{e2}}."],
        "rival": ["{{e1}} had a rivalry with {{e2}}.", "{{e1}} and {{e2}} were professional competitors.", "{{e1}} often clashed with {{e2}}."],
        "parent": ["{{e1}}'s parent is {{e2}}.", "{{e2}} is the parent of {{e1}}.", "{{e1}} was born to {{e2}}."],
        "neighbor": ["{{e1}} lives next to {{e2}}.", "{{e1}} is neighbors with {{e2}}.", "{{e1}} resides beside {{e2}}."],
        "classmate": ["{{e1}} was a classmate of {{e2}}.", "{{e1}} attended school with {{e2}}.", "{{e1}} studied alongside {{e2}}."],
        "roommate": ["{{e1}} shared a room with {{e2}}.", "{{e1}} was {{e2}}'s roommate.", "{{e1}} lived with {{e2}}."],
        "university": ["{{e1}} went to {{e2}}.", "{{e1}} was a student at {{e2}}.", "{{e1}} completed their degree at {{e2}}."],
        "major": ["{{e1}} majored in {{e2}}.", "{{e1}}'s field of study was {{e2}}.", "{{e1}} specialized in {{e2}}."],
    }}
}}

For a given relation path, such as `["mentoring", "classmate"]`, a valid question template could be:
"Who is the classmate of the person who considers {{e1}} as a mentor?"

Your response should be formatted as a JSON list, for example:
Output:
[
    "Who is the classmate of the person who considers {{e1}} as a mentor?",
    "The classmate of the student of {{e1}} is?",
    "Can you tell me the classmate of the person mentored by {{e1}}?"
]

Note that it is guaranteed that the relation path starts from a person {{e1}}.

If the given relation path is not meaningful or cannot be converted into a question template, return an empty list.
For example, given ['university', 'philanthropy', 'major'], {{e1}} studied in a university, but the university does not have a philanthropy, so the output should be an empty list.

Ensure that the generated questions maintain natural fluency and accurately represent the meaning of the relation path.

You must not output anything other than the JSON list of question templates!

Now, generate 3 question templates for the following relation path: `{relation_path}`.
Output:
"""
    # print(prompt)
    response = engine.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    result = response.choices[0].message.content.strip("Output:").strip()
    print(result)
    return result


def split_iid_composition_gen(input_file="./data_aligned/relations_group2.json", output_file="./data_aligned/relations_group2_combinations_split.json"):
    relations=json_load("./data_aligned/relations_group2.json")
    group = relations['group']
    combinations = [i["relation_path"] for i in relations['multi_hop_combinations']]
    all_combinations_dict = dict()

    test_ratios=(0.2, 0.7, 0.1)
    iid_size, comp_size, gen_size = len(group)*test_ratios[0], len(group)*test_ratios[1], len(group)*test_ratios[2]
    random.shuffle(group)
    iid_relations, comp_relations, gen_relations = group[:int(iid_size)], group[int(iid_size):int(iid_size+comp_size)], group[int(iid_size+comp_size):]

    print(gen_relations)
    print(combinations[0])

    generalization = [p for p in combinations if any(r in gen_relations for r in p)]
    iid = [p for p in combinations if any(r in iid_relations for r in p) and not any(r in gen_relations for r in p)]

    composition_train = []
    composition_test = []

    for p in combinations:
        if any(r in iid or p in generalization for r in p):
            continue

        # if all relation in p are in composition, this p can either be used for train or test
        if all(r in comp_relations for r in p):
            if len(composition_train) < len(composition_test):
                composition_train.append(p)
            else:
                composition_test.append(p)

    print(f"iid size: {len(iid_relations)}, composition size: {len(comp_relations)}, generalization size: {len(gen_relations)}.")
    print(f"iid combinations: {len(iid)}, composition train: {len(composition_train)}, composition test: {len(composition_test)}, generalization: {len(generalization)}.")

    all_combinations_dict['iid'] = iid
    all_combinations_dict['composition_train'] = composition_train
    all_combinations_dict['composition_test'] = composition_test
    all_combinations_dict['generalization'] = generalization

    # save the combinations to json
    json_dump(all_combinations_dict, "./data_aligned/relations_group2_combinations_split.json")


def path_to_template_gen(input_file="./data_aligned/relations_group1_template.json", output_file="./data_aligned/relations_group1_template_dict.json"):
    path_to_template = dict()
    relation_path_template = json_load(input_file)

    for p in relation_path_template:
        path_to_template[" ".join(p['relation_path'])] = p['question_templates']

    # save the path to template to json
    json_dump(path_to_template, "./data_aligned/relations_group1_template_dict.json")



def verify_question_template(input_file="./data_aligned/relations_group2_template_with_answers.json", output_file="./data_aligned/relations_group2_template_with_answers_checked.json"):
    combinations1 = json_load(input_file)
    output1 = []
    skip=0
    for combination in tqdm(combinations1):
        relation_path = combination["relation_path"]
        answer_template = combination["answer"]

        print(relation_path)    
        if "parent" not in relation_path and "mentored_by" not in relation_path and "boss_of" not in relation_path and "leader_of" not in relation_path:
            output1.append(combination)
            skip+=1
            continue
        
        result = call_llm_to_verify_templates(relation_path, answer_template, "gpt-4o-mini")
        
        if len(result) > 0 and result != "[]":
            try:
                combination["question_templates"] = json.loads(result)
                output1.append(combination)
            except Exception as e:
                print(f"Error processing {relation_path}: {e}.")
                continue

    print(f"skip {skip} relation path.")

    json_dump(output1, output_file)



def generate_template(input_file="./data_aligned/relations_group2_template.json", output_file="./data_aligned/relations_group2_template.json"):
    combinations1 = json_load(input_file)
    output1 = []

    for combination in tqdm(combinations1):
        relation_path = combination["relation_path"]
        print(relation_path)
      
        if "parent" not in relation_path:
            output1.append(combination)
            continue

        result = call_llm_to_generate_templates(relation_path, "gpt-4o-mini")
        
        if len(result) > 0 and result != "[]":
            try:
                combination["question_templates"] = json.loads(result)
                output1.append(combination)
            except Exception as e:
                print(f"Error processing {relation_path}: {e}.")
                continue

    json_dump(output1, output_file)


def sample_relations_from_both_groups(min_hops=2, max_hops=5):
    group1_iid_path = json_load("./data_aligned/relations_group1_combinations_split.json")['iid']
    group1 = list(set([i for rp in group1_iid_path for i in rp] ))# knowledge inside
    group2 = json_load("./data_aligned/relations_group2.json")['group'] # knowledge outside
    all_relations = list(group1+group2)
    print("length of all relations:", len(all_relations))
    multi_hop_combinations = []

    human_related_relations_cur = [rel for rel in all_relations if rel in human_related_relations]
    weights = [0.5, 0.3, 0.15, 0.05] 
    hop_choices = list(range(min_hops, max_hops+1))  # [2, 3, 4, 5]

    current_path = []
    for _ in range(1000): 
        hop_count = random.choices(hop_choices, weights=weights)[0]  # 按权重采样跳数
        path = random.sample(human_related_relations_cur, hop_count - 1)  # 采样 human-related 关系
        if all(rel in group1 for rel in path):
            path.append(random.choice(group2))  
        elif all(rel in group2 for rel in path):
            path.append(random.choice(group1))
        else:
            path.append(random.choice(all_relations))

        if " ".join(path) not in current_path:
            current_path.append(" ".join(path))
            parametric_knowledge = []
            contextual_knowledge = []
            for rel in path:
                if rel in group1:
                    parametric_knowledge.append(rel)
                else:
                    contextual_knowledge.append(rel)

            multi_hop_combinations.append({"relation_path": path, "question_templates": [], "parametric_knowledge": parametric_knowledge, "contextual_knowledge": contextual_knowledge})

    print(f"Sampled {len(multi_hop_combinations)} multi-hop combinations.")

    json_dump(multi_hop_combinations, "./data_aligned/relations_group3.json")
    return multi_hop_combinations


def build_single_hop_question_answer_pair(output_dir):
    bio_dict = json_load("data/biographies_parametric.json")
    qa_pairs = []
    name_list = []
    for name, properties in bio_dict.items():
        name_list.append(name)
        for property, value in properties.items():
            if property in question_templates_for_relations.keys():
                template = random.choice(question_templates_for_relations[property])
                question = template.format(e1=name)
                answer = value

                qa_pairs.append({
                    "question": question,
                    "answer_cot": answer,
                    "answer": answer,
                    "instruction": "ANSWER THE QUESTION. ",
                })
        if len(name_list) > 4000:
            break
    print(len(qa_pairs))
    json_dump(qa_pairs, f"{output_dir}/group1_single_hop_qa_pairs.json")


if __name__ == "__main__":
    # call_llm_to_generate_templates("[\"child\"]", "meta-llama/Llama-3.1-70B-Instruct")
    # build_single_hop_question_answer_pair("./data_aligned/")
    # path_to_template_gen()
    # generate_template()
    verify_question_template()