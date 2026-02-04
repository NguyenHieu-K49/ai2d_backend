import json
import os

INPUT_DIR = r'E:\NCKH\Coding\ai2d_project\data\01_raw_biology'
RST_DIR = r'E:\NCKH\Coding\ai2d_project\data\ai2d_rst\data'
OUTPUT_DIR = r'E:\NCKH\Coding\ai2d_project\data\02_standardized'


def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


def process_file(filename):
    ai2d_path = os.path.join(INPUT_DIR, filename)
    rst_path = os.path.join(RST_DIR, filename)

    ai2d_data = load_json(ai2d_path)
    rst_data = load_json(rst_path)

    visual_objects = {
        "blobs": {},
        "texts": [],
        "arrows": {}
    }

    # Blobs
    for k, v in ai2d_data.get("blobs", {}).items():
        poly = v.get("polygon", [])
        if poly:
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            bbox = [min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)]
        else:
            bbox = [0, 0, 0, 0]
        visual_objects["blobs"][k] = {"id": k, "bbox": bbox}

    # Texts
    for k, v in ai2d_data.get("text", {}).items():
        visual_objects["texts"].append({
            "id": k,
            "content": v.get("value", ""),
            "bbox": v.get("rectangle", [0, 0, 0, 0])
        })

    # Arrows
    for k, v in ai2d_data.get("arrows", {}).items():
        poly = v.get("polygon", [])
        if poly:
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            bbox = [min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)]
        else:
            bbox = [0, 0, 0, 0]
        visual_objects["arrows"][k] = {"id": k, "bbox": bbox}

    connections = []

    # Lay relationship tu AI2D
    for rel in ai2d_data.get("relationships", {}).values():
        category = rel.get("category")
        if category == "interObjectLinkage":
            connections.append({
                "type": "connection",
                "from": rel.get("origin"),
                "to": rel.get("destination"),
                "via": rel.get("connector")
            })
        elif category == "intraObjectLabel":
            connections.append({
                "type": "labeling",
                "label": rel.get("origin"),
                "object": rel.get("destination")
            })

    return {
        "id": filename.replace(".json", ""),
        "visual_objects": visual_objects,
        "relationships": connections,
        "rst_source": bool(rst_data)
    }


def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
    print(f"Dang chuan hoa {len(files)} file...")

    for f in files:
        try:
            result = process_file(f)
            out_path = os.path.join(OUTPUT_DIR, f)
            with open(out_path, 'w', encoding='utf-8') as outfile:
                json.dump(result, outfile, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Loi file {f}: {e}")

    print("Hoan thanh Standardize.")


if __name__ == "__main__":
    main()