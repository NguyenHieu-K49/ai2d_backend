from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import db
from app.core.config import settings
from app.api.endpoints import router as api_router

app = FastAPI(title=settings.PROJECT_NAME)

# Cau hinh CORS (De Frontend goi duoc API ma khong bi chan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cho phep moi nguon (Dev mode)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    print(">>> KHOI DONG SERVER...")
    db.connect()

@app.on_event("shutdown")
def shutdown_event():
    print(">>> DANG TAT SERVER...")
    db.close()

# Dang ky cac duong dan API
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "AI2D Knowledge Graph API is RUNNING!"}