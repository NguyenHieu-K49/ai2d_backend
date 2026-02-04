import psycopg2
from psycopg2 import pool
from pymongo import MongoClient
from neo4j import GraphDatabase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.mongo_client = None
        self.neo4j_driver = None
        self.pg_pool = None # Doi sang dung Pool

    def connect(self):
        # 1. MongoDB
        try:
            self.mongo_client = MongoClient(settings.MONGO_URL)
            self.mongo_client.admin.command('ping')
            print(">>> Connected to MongoDB")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")

        # 2. Neo4j
        try:
            self.neo4j_driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            self.neo4j_driver.verify_connectivity()
            print(">>> Connected to Neo4j")
        except Exception as e:
            print(f"Error connecting to Neo4j: {e}")

        # 3. PostgreSQL (Connection Pool)
        try:
            self.pg_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=20, # Toi da 20 ket noi cung luc
                host=settings.POSTGRES_SERVER,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                dbname=settings.POSTGRES_DB,
                port=settings.POSTGRES_PORT,
                sslmode="require"
            )
            print(">>> Connected to PostgreSQL (Pool)")
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")

    def close(self):
        if self.mongo_client:
            self.mongo_client.close()
        if self.neo4j_driver:
            self.neo4j_driver.close()
        if self.pg_pool:
            self.pg_pool.closeall()
        print("All database connections closed.")

    def get_mongo_db(self):
        return self.mongo_client[settings.MONGO_DB_NAME]

    def get_neo4j_session(self):
        return self.neo4j_driver.session()

    # Ham moi de lay ket noi tu Pool an toan hon
    def get_postgres_conn(self):
        return self.pg_pool.getconn()

    def put_postgres_conn(self, conn):
        self.pg_pool.putconn(conn)

db = DatabaseManager()