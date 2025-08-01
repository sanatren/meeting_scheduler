from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.database import engine, Base
from app.routes import messages, schedule, meetings, auth

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Creating the tables when the start up happensz.
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="PropVivo Meeting Scheduler",
    description="AI-powered group chat with meeting scheduling",
    version="1.0.0",
    lifespan=lifespan
)

#cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(messages.router, prefix="/api", tags=["messages"])
app.include_router(schedule.router, prefix="/api", tags=["schedule"])
app.include_router(meetings.router, prefix="/api", tags=["meetings"])

@app.get("/")
async def root():
    return {"message": "PropVivo Meeting Scheduler API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
