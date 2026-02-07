from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from app.core.config import settings
from app.db.session import engine, Base
from app.models.user import User  # IMPORT MODEL HERE to register it with Base
from app.models.session import AnalysisSession

# Create Tables (For dev simplicity, use Alembic in prod)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)   

# Ensure static dir exists
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to Smart Sprint Training System API"}

# Include Routers (will add later)
from app.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)
