from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Auto-Selp API", version="1.0.0")

# CORS Setup
origins = [
    "http://localhost:3000", # React Frontend
    "http://localhost:5173", # Vite Default
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Auto-Selp API"}

from src.api.routers import jobs, prompts

app.include_router(jobs.router)
app.include_router(prompts.router)
