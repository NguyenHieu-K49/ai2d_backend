import pandas as pd
import os

OUTPUT_FILE = r'E:\NCKH\Coding\ai2d_project\Biology_Mapping_Rules.xlsx'

def create_mapping_excel():
    data = [
        {
            "category": "foodChainsWebs",
            "stem_domain": "Biology",
            "node_label": "Organism",
            "description": "Sinh vat trong chuoi thuc an"
        },
        {
            "category": "lifeCycles",
            "stem_domain": "Biology",
            "node_label": "Stage",
            "description": "Giai doan phat trien"
        },
        {
            "category": "photosynthesisRespiration",
            "stem_domain": "Biology",
            "node_label": "Component",
            "description": "Thanh phan cua qua trinh"
        }
    ]

    df = pd.DataFrame(data)
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"Da tao file mapping: {OUTPUT_FILE}")

if __name__ == "__main__":
    create_mapping_excel()