# backend/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Ensure the DATABASE_URL is loaded
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

# Create the SQLAlchemy engine
# The connect_args are often needed for SQLite, but for PostgreSQL,
# the URL format handles most connection details.
# If you encounter issues, you might need specific args depending on your setup.
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
# sessionmaker is used to create SessionLocal class.
# Each instance of SessionLocal will be a database session.
# The class itself is not a database session yet.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# A base class that other models will inherit from.
# When we inherit from this Base class, we get database table objects.
Base = declarative_base()

# Dependency to get DB session
# This function is used by FastAPI's Depends system to inject a database session
# into your endpoint functions.
def get_db():
    db = SessionLocal()
    try:
        # Yield the database session
        yield db
    finally:
        # Close the database session in the finally block
        # to ensure it's always closed, even if errors occur.
        db.close()
