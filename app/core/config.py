import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME = os.getenv("PROJECT_NAME", "AI2D API")
    API_V1_STR = os.getenv("API_V1_STR", "/api/v1")

    R2_BASE_URL = os.getenv("R2_BASE_URL", "https://pub-your-r2-domain.dev")

    MONGO_URL = os.getenv("MONGO_URL")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USER = os.getenv("NEO4J_USER")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

    POSTGRES_SERVER = os.getenv("POSTGRES_SERVER")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")


settings = Settings()