from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Handle special characters in password
if DATABASE_URL:
    # SQLAlchemy requires URL encoding for special characters
    engine = create_engine(DATABASE_URL)
else:
    # Fallback to local database
    DATABASE_URL = "postgresql://localhost:5432/propvivo_meeting_scheduler"
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
