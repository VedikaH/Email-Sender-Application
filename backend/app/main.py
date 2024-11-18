from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import csv, email, analytics
from .database import Database
from .config import  print_settings, settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    print_settings()
    try:
        await Database.connect_db()
        print("Database connected successfully.")
    except Exception as e:
        print(f"Database connection failed: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    await Database.close_db()

app.include_router(csv.router, prefix="/csv", tags=["CSV"])
app.include_router(email.router, prefix="/email", tags=["Email"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
