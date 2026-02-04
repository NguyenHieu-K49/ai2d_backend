import json
import os
import pandas as pd

INPUT_DIR = r'E:\NCKH\Coding\ai2d_project\data\02_standardized'
MAPPING_FILE = r'E:\NCKH\Coding\ai2d_project\Biology_Mapping_Rules.xlsx'
OUTPUT_DIR = r'E:\NCKH\Coding\ai2d_project\data\03_graph_payloads'
CATEGORIES_FILE = r'E:\NCKH\Coding\ai2d_project\data\ai2d\categories.json'


def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None


def get_context(image_id, categories, mapping_df):
    cat = categories.get(image_id, "other")
    try:
        row = mapping_df[mapping_df['category'] == cat].iloc[0]
        return {
            "category": cat,
            "domain": row['stem_domain'],
            "label": row['node_label']
        }
    except:
        return {"category": cat, "domain": "Biology", "label": "Entity"}


def process_logic(data, context):
    image_id = data['id']
    default_label = context['label']

    nodes = []
    edges = []
    id_map = {}

    label_map = {}
    processed_texts = set()

    for rel in data.get('relationships', []):
        if rel['type'] == 'labeling':
            label_map[rel['object']] = rel['label']
            processed_texts.add(rel['label'])

    blobs = data['visual_objects'].get('blobs', {})
    texts = data['visual_objects'].get('texts', [])

    for b_id, b_info in blobs.items():
        uid = f"{image_id}_{b_id}"
        id_map[b_id] = uid

        node_name = b_id
        components = [b_id]

        if b_id in label_map:
            t_id = label_map[b_id]
            t_obj = next((t for t in texts if t['id'] == t_id), None)
            if t_obj:
                node_name = t_obj['content']
                components.append(t_id)
                id_map[t_id] = uid

        nodes.append({
            "uid": uid,
            "name": node_name,
            "type": default_label,
            "components": components
        })

    for t in texts:
        if t['id'] not in processed_texts:
            uid = f"{image_id}_{t['id']}"
            id_map[t['id']] = uid
            nodes.append({
                "uid": uid,
                "name": t['content'],
                "type": default_label,
                "components": [t['id']]
            })

    for rel in data.get('relationships', []):
        if rel['type'] == 'connection':
            src = id_map.get(rel['from'])
            tgt = id_map.get(rel['to'])

            if src and tgt and src != tgt:
                edges.append({
                    "source": src,
                    "target": tgt,
                    "relation": "LINKED_TO",
                    "via": rel.get("via")
                })

    return nodes, edges


def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    categories = load_json(CATEGORIES_FILE)
    mapping_df = pd.read_excel(MAPPING_FILE)

    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
    print(f"Dang xu ly logic cho {len(files)} file...")

    for f in files:
        data = load_json(os.path.join(INPUT_DIR, f))
        if not data: continue

        image_id = data['id']
        context = get_context(image_id, categories, mapping_df)

        nodes, edges = process_logic(data, context)

        payload = {
            "id": image_id,
            "meta": context,
            "graph": {
                "nodes": nodes,
                "edges": edges
            },
            "raw": data['visual_objects']
        }

        out_path = os.path.join(OUTPUT_DIR, f)
        with open(out_path, 'w', encoding='utf-8') as outfile:
            json.dump(payload, outfile, indent=2, ensure_ascii=False)

    print("Hoan thanh xu ly Graph.")


if __name__ == "__main__":
    main()