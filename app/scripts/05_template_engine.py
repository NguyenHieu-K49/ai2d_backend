import json
import os

INPUT_DIR = r'E:\NCKH\Coding\ai2d_project\data\03_graph_payloads'
OUTPUT_DIR = r'E:\NCKH\Coding\ai2d_project\data\04_final_payloads'


def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None


def get_node_name(uid, nodes):
    for n in nodes:
        if n['uid'] == uid:
            return n['name']
    return "doi tuong"


def generate_food_web_description(nodes, edges):
    sentences = []
    for edge in edges:
        src_name = get_node_name(edge['source'], nodes)
        tgt_name = get_node_name(edge['target'], nodes)
        sentences.append(f"{src_name} la nguon thuc an cho {tgt_name}.")

    if not sentences:
        return "So do nay mo ta cac moi quan he dinh duong."

    full_text = "Trong luoi thuc an nay: " + " ".join(sentences)
    return full_text


def generate_lifecycle_description(nodes, edges):
    sentences = []
    for edge in edges:
        src_name = get_node_name(edge['source'], nodes)
        tgt_name = get_node_name(edge['target'], nodes)
        sentences.append(f"Giai doan {src_name} phat trien thanh {tgt_name}.")

    if not sentences:
        return "So do nay mo ta cac giai doan phat trien."

    full_text = "Qua trinh phat trien nhu sau: " + " ".join(sentences)
    return full_text


def generate_generic_description(nodes, edges):
    entity_names = [n['name'] for n in nodes]
    names_str = ", ".join(entity_names)
    return f"So do nay bao gom: {names_str}. Cac thanh phan co moi lien he voi nhau."


def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
    print(f"Dang tao mo ta template cho {len(files)} file...")

    count = 0
    for f in files:
        data = load_json(os.path.join(INPUT_DIR, f))
        if not data: continue

        category = data['meta']['category']
        nodes = data['graph']['nodes']
        edges = data['graph']['edges']

        description = ""

        if category == 'foodChainsWebs':
            description = generate_food_web_description(nodes, edges)
        elif category == 'lifeCycles':
            description = generate_lifecycle_description(nodes, edges)
        else:
            description = generate_generic_description(nodes, edges)

        data['description'] = description

        out_path = os.path.join(OUTPUT_DIR, f)
        with open(out_path, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, indent=2, ensure_ascii=False)
        count += 1

    print(f"Hoan thanh. Ket qua tai: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()