# backend/crud.py

# CRUD (Create, Read, Update, Delete) operations for interacting with the database
# These functions use SQLAlchemy sessions to perform database queries and modifications

from sqlalchemy.orm import Session
from . import models, schemas # Import SQLAlchemy models and Pydantic schemas
from fastapi import UploadFile
import os
import uuid # To generate unique filenames for uploaded images
import shutil # To save the uploaded file content

# Get the upload directory from environment variables, default to './uploads'
# Ensure this matches the UPLOAD_DIR in your .env file
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

# Ensure the upload directory exists when the application starts
# This is a simple check; more robust solutions might be needed in production
if not os.path.exists(UPLOAD_DIR):
    # Create the directory if it doesn't exist
    os.makedirs(UPLOAD_DIR)
    print(f"Created upload directory: {UPLOAD_DIR}") # Optional: log creation

# Function to save the uploaded image file to local disk
async def save_image_file(upload_file: UploadFile):
    # Get the file extension from the original filename
    file_extension = os.path.splitext(upload_file.filename)[1]

    # Generate a unique filename using UUID (Universally Unique Identifier)
    # This prevents filename collisions if multiple users upload files with the same name
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # Construct the full path where the file will be saved
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save the file content
    # Use 'wb' mode for writing in binary mode
    # Use shutil.copyfileobj for efficient file copying
    try:
        with open(file_path, "wb") as buffer:
            # Reset file pointer to the beginning in case it was read elsewhere
            await upload_file.seek(0)
            shutil.copyfileobj(upload_file.file, buffer)
    except Exception as e:
        # Log the error and re-raise
        print(f"Error saving file {upload_file.filename} to {file_path}: {e}")
        raise # Re-raise the exception to be handled by the caller

    # Return the unique filename that was generated and used
    return unique_filename

# Function to create a new image metadata record in the database
def create_image_metadata(db: Session, filename: str, original_filename: str, metadata: schemas.ImageMetadataCreate):
    # Create an instance of the SQLAlchemy model
    db_metadata = models.ImageMetadata(
        filename=filename, # The unique filename saved on disk
        original_filename=original_filename, # The original name from the user
        uploader_name=metadata.uploader_name, # Data from the Pydantic schema
        location=metadata.location # Data from the Pydantic schema
        # approval_status and rating are handled in later weeks
    )

    # Add the new object to the database session
    db.add(db_metadata)

    # Commit the transaction to save the changes to the database
    db.commit()

    # Refresh the instance to get any database-generated values (like the auto-incremented ID and default timestamp)
    db.refresh(db_metadata)

    # Return the newly created database object
    return db_metadata

# Function to retrieve a list of image metadata records from the database
def get_images_metadata(db: Session, skip: int = 0, limit: int = 100):
    # Query the ImageMetadata table
    # .offset(skip) skips a number of records (for pagination)
    # .limit(limit) limits the number of records returned (for pagination)
    # .all() executes the query and returns all results as a list
    # For MVP, we get all records. In later weeks, we'll filter by approval_status=True.
    return db.query(models.ImageMetadata).offset(skip).limit(limit).all()

# Function to retrieve a single image metadata record by its ID
def get_image_metadata(db: Session, image_id: int):
    # Query the ImageMetadata table and filter by the id column
    # .filter(models.ImageMetadata.id == image_id) adds a WHERE clause to the SQL query
    # .first() executes the query and returns the first result (or None if no match)
    return db.query(models.ImageMetadata).filter(models.ImageMetadata.id == image_id).first()

# TODO: Add functions for updating (e.g., approval status, rating) and deleting metadata for admin later
