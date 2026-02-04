import json
import os
import shutil

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Cac file input
CATEGORIES_FILE = os.path.join(DATA_DIR, 'ai2d', 'categories.json')
ANNOTATIONS_DIR = os.path.join(DATA_DIR, 'ai2d', 'annotations')
RST_DIR = os.path.join(DATA_DIR, 'ai2d_rst', 'data')
# Output
OUTPUT_DIR = os.path.join(DATA_DIR, '01_raw_biology')

TARGET_CATEGORIES = [
    'foodChainsWebs',
    'lifeCycles',
    'photosynthesisRespiration'
]


def filter_data():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Doc file categories bang UTF-8
    try:
        with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
            categories = json.load(f)
    except Exception as e:
        print(f"Loi doc file categories: {e}")
        return

    if os.path.exists(RST_DIR):
        rst_files = set(os.listdir(RST_DIR))
    else:
        print("Khong tim thay thu muc RST ")
        rst_files = set()

    count = 0
    print("Bat dau loc du lieu...")

    for image_id_raw, category in categories.items():
        if category in TARGET_CATEGORIES:
            image_id = image_id_raw.strip()

            filename = f"{image_id}.json"

            # Logic kiem tra ton tai
            has_rst = True
            if rst_files and filename not in rst_files:
                has_rst = False

            # Chi lay neu thoa man
            if has_rst:
                src_path = os.path.join(ANNOTATIONS_DIR, filename)
                dst_path = os.path.join(OUTPUT_DIR, filename)

                if os.path.exists(src_path):
                    try:
                        # Doc va ghi lai de dam bao UTF-8 chuan
                        with open(src_path, 'r', encoding='utf-8') as f_in:
                            data = json.load(f_in)

                        with open(dst_path, 'w', encoding='utf-8') as f_out:
                            json.dump(data, f_out, indent=2, ensure_ascii=False)

                        count += 1
                    except Exception as e:
                        print(f"Loi file {filename}: {e}")

    print(f"Hoan thanh. Da loc {count} file vao: {OUTPUT_DIR}")


if __name__ == "__main__":
    filter_data()