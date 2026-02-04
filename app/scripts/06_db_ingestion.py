import os
import json
import psycopg2
from pymongo import MongoClient
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = r'E:\NCKH\Coding\ai2d_project\data\04_final_payloads'

MONGO_URI = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_AUTH = (os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))

POSTGRES_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_SERVER"),
    "port": os.getenv("POSTGRES_PORT"),
    "sslmode": "require"
}


def load_mongo(data, client):
    try:
        db = client[MONGO_DB_NAME]
        coll = db["diagrams_inventory"]
        coll.replace_one({"id": data["id"]}, data, upsert=True)
        return True
    except Exception as e:
        print(f"Mongo Error: {e}")
        return False


def load_neo4j(data, driver):
    try:
        image_id = data["id"]
        nodes = data["graph"]["nodes"]
        edges = data["graph"]["edges"]

        with driver.session() as session:
            session.run("MERGE (d:Diagram {id: $id})", id=image_id)

            for n in nodes:
                label = n.get("type", "Entity")
                session.run(f"MERGE (n:Entity:{label} {{uid: $uid}}) SET n.name = $name, n.diagram_id = $did",
                            uid=n["uid"], name=n["name"], did=image_id)

                session.run("MATCH (d:Diagram {id: $did}), (n:Entity {uid: $uid}) MERGE (d)-[:CONTAINS]->(n)",
                            did=image_id, uid=n["uid"])

            for e in edges:
                session.run("MATCH (src:Entity {uid: $src}), (tgt:Entity {uid: $tgt}) MERGE (src)-[:LINKED_TO]->(tgt)",
                            src=e["source"], tgt=e["target"])
        return True
    except Exception as e:
        print(f"Neo4j Error: {e}")
        return False


def load_postgres(data, cursor):
    try:
        diagram_id = data["id"]
        category = data["meta"]["category"]
        description = data.get("description", "")

        query = """
        INSERT INTO diagram_captions (diagram_id, category, description)
        VALUES (%s, %s, %s) 
        ON CONFLICT (diagram_id) 
        DO UPDATE SET description = EXCLUDED.description;
        """
        cursor.execute(query, (diagram_id, category, description))
        return True
    except Exception as e:
        print(f"Postgres Error: {e}")
        return False


def init_postgres_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diagram_captions(
            diagram_id VARCHAR(50) PRIMARY KEY,
            category VARCHAR(50),
            description TEXT
        );
    """)


def main():
    print("Bat dau nap du lieu (UTF-8)...")

    try:
        mongo_client = MongoClient(MONGO_URI)
        neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
        pg_conn = psycopg2.connect(**POSTGRES_CONFIG)
        pg_conn.autocommit = True
        pg_cursor = pg_conn.cursor()

        init_postgres_table(pg_cursor)
        print("Ket noi Database thanh cong.")
    except Exception as e:
        print(f"Loi ket noi: {e}")
        return

    if not os.path.exists(DATA_DIR):
        print(f"Khong tim thay thu muc: {DATA_DIR}")
        return

    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    print(f"Tim thay {len(files)} file...")

    count = 0
    for f in files:
        filepath = os.path.join(DATA_DIR, f)

        # Doc UTF-8
        try:
            with open(filepath, 'r', encoding='utf-8') as file_in:
                data = json.load(file_in)
        except Exception as e:
            print(f"Bo qua file loi {f}: {e}")
            continue

        ok_mongo = load_mongo(data, mongo_client)
        ok_neo4j = load_neo4j(data, neo4j_driver)
        ok_pg = load_postgres(data, pg_cursor)

        if ok_mongo and ok_neo4j and ok_pg:
            count += 1
            if count % 20 == 0:
                print(f"-> Da nap xong {count} file...")

    mongo_client.close()
    neo4j_driver.close()
    pg_cursor.close()
    pg_conn.close()

    print(f"Hoan tat. Da nap thanh cong {count}/{len(files)} file.")


if __name__ == "__main__":
    main()