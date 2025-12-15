import random
import faker
from tqdm import tqdm
from relations import *
from utils import json_load, json_dump



def generate_human_biographies_group1(n, relation_group):
    fake = faker.Faker()
    faker.Faker.seed(42)
    random.seed(42)

    name_set = []
    # 生成 n 个 Synthetic 人物
    humans = []
    for _ in tqdm(range(int(n)), desc="Generating new humans"):
        human = {
            "name": fake.name(),
            "birth_date": fake.date_of_birth(minimum_age=20, maximum_age=100).strftime("%Y-%m-%d"),
            "occupation": fake.job(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "new": True  # 标记为新生成的人物
        }
        # 确保名字唯一
        while human["name"] in name_set:
            human["name"] = fake.name()
        name_set.append(human["name"])
        humans.append(human)

    # 生成 biographies
    biographies = []
    bio_dict = dict()
    for human in humans:
        bio_dict[human["name"]] = human

    for human in tqdm(humans):
        bio = []
        for rel in relation_group:
            template = random.choice(relationship_templates[rel])

            if bio_dict[human['name']].get(rel) is not None:
                bio.append(template.format(e1=human["name"], e2=bio_dict[human['name']][rel]))
                continue
            
            e2 = random.choice(humans)["name"]
            while e2 == human["name"]:  
                e2 = random.choice(humans)["name"]

            if rel in ['spouse', 'best_friend', "colleague", "sibling", "rival", "neighbor", "classmate", "roommate"]:
                bio_dict[e2][rel] = human["name"]
                
            elif rel == "child":
                while (e2 in bio_dict and bio_dict[e2].get("child_of") is not None) or e2 == human["name"]:
                    e2 = random.choice(humans)["name"]
                if "child_of" in relation_group:
                    bio_dict[e2]["child_of"] = human["name"]
            elif rel == "mentoring":
                while (e2 in bio_dict and bio_dict[e2].get("mentored_by") is not None) or e2 == human["name"]:
                    e2 = random.choice(humans)["name"]
                if "mentored_by" in relation_group:
                    bio_dict[e2]["mentored_by"] = human["name"]
            elif rel == "boss":
                while (e2 in bio_dict and bio_dict[e2].get("boss_of") is not None) or e2 == human["name"]:
                    e2 = random.choice(humans)["name"]
                if "boss_of" in relation_group:
                    bio_dict[e2]["boss_of"] = human["name"]
            elif rel == "influenced_by":
                while (e2 in bio_dict and bio_dict[e2].get("influence") is not None) or e2 == human["name"]:
                    e2 = random.choice(humans)["name"]
                if "influence" in relation_group:
                    bio_dict[e2]["influence"] = human["name"]
            elif rel == "child_of":
                while (e2 in bio_dict and bio_dict[e2].get("child") is not None)  or e2 == human["name"]:
                    e2 = random.choice(humans)["name"]
                if "child" in relation_group:
                    bio_dict[e2]["child"] = e2
            elif rel == "mentored_by":
                while (e2 in bio_dict and bio_dict[e2].get("mentoring") is not None) or e2 == human["name"]:
                    e2 = random.choice(humans)["name"]
                if "mentoring" in relation_group:
                    bio_dict[e2]["mentoring"] = e2
            elif rel == "boss_of":
                while (e2 in bio_dict and bio_dict[e2].get("boss") is not None )  or e2 == human["name"]:
                    e2 = random.choice(humans)["name"]
                if "boss" in relation_group:
                    bio_dict[e2]["boss"] = e2
            elif rel == "influence":
                while (e2 in bio_dict and bio_dict[e2].get("influenced_by") is not None)  or e2 == human["name"]:
                    e2 = random.choice(humans)["name"]
                if "influenced_by" in relation_group:
                    bio_dict[e2]["influenced_by"] = e2

            elif rel == "hobby":
                e2 = random.choice(["painting", "playing guitar", "chess", "hiking", "swimming", "reading", "writing", "cooking", "traveling"])
            elif rel == "pet":
                e2 = random.choice(["Buddy", "Milo", "Whiskers", "Luna", "Max", "Charlie", "Bella", "Lucy"])
            elif rel == "university":
                e2 = random.choice(["Harvard University", "Stanford University", "MIT", "Yale University", "Princeton University", "Columbia University", "University of Chicago", "California Institute of Technology", "University of Pennsylvania", "University of California, Berkeley", "University of Michigan", "University of California, Los Angeles", "University of Washington", "University of Toronto", "University of Oxford"])
            elif rel == "major":
                e2 = random.choice(["Computer Science", "Mathematics", "Physics", "Biology", "Chemistry", "Economics", "History", "Psychology", "Engineering", "Literature", "Philosophy", "Political Science", "Art History", "Sociology", "Environmental Science", "Business Administration", "Finance", "Marketing", "Nursing", "Education"])
            elif rel in ['leader_of', "worked_at"]:
                e2 = fake.company()
            elif rel in ["service", "philanthropy"]:
                e2 = random.choice(["Red Cross", "UNICEF", "World Wildlife Fund", "Doctors Without Borders", "Habitat for Humanity", "Amnesty International", "Greenpeace", "Oxfam", "Save the Children", "World Food Programme", "Make-A-Wish Foundation", "St. Jude Children's Research Hospital", "Feeding America", "The Nature Conservancy", "Human Rights Campaign"]) 
            elif rel in ["favorite_food"]:
                e2 = random.choice(["pizza", "sushi", "pasta", "tacos", "ice cream", "salad", "burger", "steak", "seafood", "chocolate", "fruit salad", "sandwich", "curry", "soup", "noodles", "dim sum", "barbecue", "cereal", "pancakes", "waffles"])               
            elif rel in ["first_language"]:
                e2 = random.choice(["English", "Spanish", "Mandarin", "French", "German", "Italian", "Russian", "Japanese", "Korean", "Portuguese", "Arabic", "Hindi", "Bengali", "Turkish", "Vietnamese", "Dutch", "Swedish", "Norwegian", "Danish", "Finnish"])
            elif rel in ["died_on"]:
                e2 = fake.date_between().strftime("%Y-%m-%d")
            elif rel in ["died_in", "lived_in"]:
                e2 = fake.city()
            elif rel in ["known_for"]:
                e2 = random.choice(["acting", "singing", "writing", "directing", "producing", "painting", "dancing", "athletics", "philanthropy", "politics"])
            elif rel in ["wrote"]:
                e2 = fake.sentence(nb_words=3).strip('.')
            else:
                e2 = human[rel]

            bio_dict[human["name"]][rel] = e2
            bio.append(template.format(e1=human["name"], e2=e2))

        random.shuffle(bio)
        biographies.append(" ".join(bio))
    
    return biographies, bio_dict


def generate_human_biographies_group2(n, relation_group):
    fake = faker.Faker()
    faker.Faker.seed(42)
    random.seed(42)


    parametric_dict = json_load('./data_aligned/biographies_parametric_aligned.json')
    used_name = list(parametric_dict.keys())
    name_set = used_name.copy()  # 用于确保名字唯一
    humans = []

    # 生成 n/2 个 新 人物
    for _ in tqdm(range(int(n/2)), desc="Generating new humans"):
        human = {
            "name": fake.name(),
            "birth_place": fake.city(),
            "nationality": fake.country(),
            "address": fake.address(),
            "awards": fake.word().capitalize() + " Award",
            "new": True  # 标记为新生成的人物
        }
        # 确保名字唯一
        while human["name"] in name_set:
            human["name"] = fake.name()

        name_set.append(human["name"])
        humans.append(human)

    name_set = [human['name'] for human in humans]   # 用于确保名字唯一
    # 生成 n/2 个 旧的 人物
    for _ in tqdm(range(int(n/2)), desc="Generating old humans"):
        name = random.choice(used_name)
        while name in name_set:
            name = random.choice(used_name)

        used_name.remove(name)  # 从已使用的名字中移除
        human = {
            "name": name,
            "birth_place": fake.city(),
            "nationality": fake.country(),
            "address": fake.address(),
            "awards": fake.word().capitalize() + " Award",
            "new": False  # 标记为旧人物
        }
        
        name_set.append(human["name"])
        humans.append(human)

    print("length of name_set", len([human['name'] for human in humans]), len(name_set))

    # 生成 biographies
    biographies = []
    bio_dict = dict()
    for human in humans:
        bio_dict[human["name"]] = human

    for name, property_dict in parametric_dict.items():
        for rel, value in property_dict.items():
            if rel in inverse_relations.keys():
                if value in name_set and inverse_relations[rel] in relation_group:
                    bio_dict[value][inverse_relations[rel]] = name


    print("length of biodict", len(bio_dict.keys()))
    for human in tqdm(humans):
        bio = []
        for rel in relation_group:
            template = random.choice(relationship_templates[rel])

            if bio_dict[human['name']].get(rel) is not None:
                bio.append(template.format(e1=human["name"], e2=bio_dict[human['name']][rel]))
                continue
            
            e2 = random.choice(humans)["name"]
            while e2 == human["name"]:  
                e2 = random.choice(humans)["name"]

            if rel in ['spouse', 'best_friend', "colleague", "sibling", "rival", "neighbor", "classmate", "roommate"]:
                bio_dict[e2][rel] = human["name"]
                
            elif rel == "child":
                while (e2 in bio_dict and bio_dict[e2].get("child_of") is not None) or e2 == human["name"]:
                    e2 = random.choice(humans)["name"]
                if "child_of" in relation_group:
                    bio_dict[e2]["child_of"] = human["name"]

            elif rel == "mentoring":
                while (e2 in bio_dict and bio_dict[e2].get("mentored_by") is not None) or e2 == human["name"]:
                    e2 = random.choice(humans)["name"]
                if "mentored_by" in relation_group:
                    bio_dict[e2]["mentored_by"] = human["name"]
            elif rel == "boss":
                while (e2 in bio_dict and bio_dict[e2].get("boss_of") is not None) or e2 == human["name"]:
                    e2 = random.choice(humans)["name"]
                if "boss_of" in relation_group:
                    bio_dict[e2]["boss_of"] = human["name"]
            elif rel == "influenced_by":
                while (e2 in bio_dict and bio_dict[e2].get("influence") is not None) or e2 == human["name"]:
                    e2 = random.choice(humans)["name"]
                if "influence" in relation_group:
                    bio_dict[e2]["influence"] = human["name"]
            elif rel == "child_of":
                while (e2 in bio_dict and bio_dict[e2].get("child") is not None)  or e2 == human["name"]:
                    e2 = random.choice(humans)["name"]
                if "child" in relation_group:
                    bio_dict[e2]["child"] = e2
            elif rel == "mentored_by":
                while (e2 in bio_dict and bio_dict[e2].get("mentoring") is not None) or e2 == human["name"]:
                    e2 = random.choice(humans)["name"]
                if "mentoring" in relation_group:
                    bio_dict[e2]["mentoring"] = e2
            elif rel == "boss_of":
                while (e2 in bio_dict and bio_dict[e2].get("boss") is not None )  or e2 == human["name"]:
                    e2 = random.choice(humans)["name"]
                if "boss" in relation_group:
                    bio_dict[e2]["boss"] = e2
            elif rel == "influence":
                while (e2 in bio_dict and bio_dict[e2].get("influenced_by") is not None)  or e2 == human["name"]:
                    e2 = random.choice(humans)["name"]
                if "influenced_by" in relation_group:
                    bio_dict[e2]["influenced_by"] = e2

            elif rel == "hobby":
                e2 = random.choice(["painting", "playing guitar", "chess", "hiking", "swimming", "reading", "writing", "cooking", "traveling"])
            elif rel == "pet":
                e2 = random.choice(["Buddy", "Milo", "Whiskers", "Luna", "Max", "Charlie", "Bella", "Lucy"])
            elif rel == "university":
                e2 = random.choice(["Harvard University", "Stanford University", "MIT", "Yale University", "Princeton University", "Columbia University", "University of Chicago", "California Institute of Technology", "University of Pennsylvania", "University of California, Berkeley", "University of Michigan", "University of California, Los Angeles", "University of Washington", "University of Toronto", "University of Oxford"])
            elif rel == "major":
                e2 = random.choice(["Computer Science", "Mathematics", "Physics", "Biology", "Chemistry", "Economics", "History", "Psychology", "Engineering", "Literature", "Philosophy", "Political Science", "Art History", "Sociology", "Environmental Science", "Business Administration", "Finance", "Marketing", "Nursing", "Education"])
            elif rel in ['leader_of', "worked_at"]:
                e2 = fake.company()
            elif rel in ["service", "philanthropy"]:
                e2 = random.choice(["Red Cross", "UNICEF", "World Wildlife Fund", "Doctors Without Borders", "Habitat for Humanity", "Amnesty International", "Greenpeace", "Oxfam", "Save the Children", "World Food Programme", "Make-A-Wish Foundation", "St. Jude Children's Research Hospital", "Feeding America", "The Nature Conservancy", "Human Rights Campaign"]) 
            elif rel in ["favorite_food"]:
                e2 = random.choice(["pizza", "sushi", "pasta", "tacos", "ice cream", "salad", "burger", "steak", "seafood", "chocolate", "fruit salad", "sandwich", "curry", "soup", "noodles", "dim sum", "barbecue", "cereal", "pancakes", "waffles"])               
            elif rel in ["first_language"]:
                e2 = random.choice(["English", "Spanish", "Mandarin", "French", "German", "Italian", "Russian", "Japanese", "Korean", "Portuguese", "Arabic", "Hindi", "Bengali", "Turkish", "Vietnamese", "Dutch", "Swedish", "Norwegian", "Danish", "Finnish"])
            elif rel in ["died_on"]:
                e2 = fake.date_between().strftime("%Y-%m-%d")
            elif rel in ["died_in", "lived_in"]:
                e2 = fake.city()
            elif rel in ["known_for"]:
                e2 = random.choice(["acting", "singing", "writing", "directing", "producing", "painting", "dancing", "athletics", "philanthropy", "politics"])
            elif rel in ["wrote"]:
                e2 = fake.sentence(nb_words=3).strip('.')
            else:
                e2 = human[rel]

            bio_dict[human["name"]][rel] = e2
            bio.append(template.format(e1=human["name"], e2=e2))

        random.shuffle(bio)
        biographies.append(" ".join(bio))
    
    return biographies, bio_dict



if __name__ == "__main__":
    n = 10000  # 示例：生成 5 个合成 biography
    relations = json_load('./data/relations_group2.json')['group']
    bios_paragraph, bios_dict = generate_human_biographies_group2(n, relations)
    for i, bio in enumerate(bios_paragraph):
        print(f"Biography {i+1}:\n{bio}\n")

    json_dump(bios_dict, './data_aligned/biographies_contextual_aligned.json')
    json_dump(bios_paragraph, './data_aligned/biographies_paragraph_contextual_aligned.json')