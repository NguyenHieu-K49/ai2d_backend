import subprocess
import sys
import time

# DANH SACH CAC SCRIPTS CAN CHAY
# Muon bo qua buoc nao, ban hay comment (them dau #) vao dau dong do
SCRIPTS = [
    # "app/scripts/01_filter_biology.py",  # Buoc 1: Loc va lam sach du lieu
    # "app/scripts/02_create_mapping.py",  # Buoc 2: Tao file Excel mapping
    # "app/scripts/03_standardize_json.py",  # Buoc 3: Chuan hoa cau truc JSON
    # "app/scripts/04_process_graph.py",  # Buoc 4: Xu ly logic Do thi (Node/Edge)
    # "app/scripts/05_template_engine.py",  # Buoc 5: Sinh mo ta tu dong
    "app/scripts/06_db_ingestion.py",  # Buoc 6: Nap vao Database
]


def run_pipeline():
    python_exe = sys.executable  # Lay duong dan Python dang kich hoat (venv)
    total_start = time.time()

    print(f"--- BAT DAU CHAY PIPELINE ({len(SCRIPTS)} buoc) ---")

    for script in SCRIPTS:
        print(f"\n[Dang chay]: {script} ...")
        start_time = time.time()

        try:
            # Goi lenh chay script con
            result = subprocess.run([python_exe, script], check=True)

            elapsed = time.time() - start_time
            print(f"[Xong]: {script} (Mat {elapsed:.2f}s)")

        except subprocess.CalledProcessError:
            print(f"\n[LOI]: Script {script} gap su co. Dung pipeline.")
            return
        except Exception as e:
            print(f"\n[LOI]: Khong tim thay file hoac loi he thong: {e}")
            return

    total_time = time.time() - total_start
    print(f"\n--- HOAN TAT TOAN BO PIPELINE sau {total_time:.2f}s ---")


if __name__ == "__main__":
    run_pipeline()