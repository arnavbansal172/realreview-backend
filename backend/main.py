# backend/main.py

# Main FastAPI application file
# This is where you define your API endpoints (routes)

from fastapi import FastAPI, Depends, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles # To serve static files (uploaded images)
from sqlalchemy.orm import Session # For database session dependency
from typing import List, Optional # For type hinting

from . import models, schemas, crud # Import local modules
from .database import engine, get_db, Base # Import database components
import os

# Get the upload directory from environment variable, default to './uploads'
# Ensure this matches the UPLOAD_DIR in your .env file
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

# Create database tables (simple approach for MVP)
# This will create tables based on the models defined in models.py
# if they don't already exist in the database.
# In a real application, you might use database migrations (e.g., Alembic).
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created (if they didn't exist).")


# Initialize the FastAPI application
app = FastAPI()

# Mount static files directory so uploaded images can be served
# Requests to /uploads/your-image.jpg will be served from the directory specified by UPLOAD_DIR
# The 'name' parameter is optional but useful for generating URLs
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# Define the API endpoint for uploading images and metadata
# HTTP Method: POST
# Path: /upload
# response_model: Specifies the schema for the response body (Pydantic model)
@app.post("/upload", response_model=schemas.ImageMetadataDisplay)
# Define the function that handles the request
# It takes the uploaded file, form data, and a database session as dependencies
async def upload_image_and_metadata(
    # UploadFile is a special type for file uploads in FastAPI
    upload_file: UploadFile = File(...), # ... indicates this is a required parameter

    # Use Form for fields that come from form data (like text inputs in an HTML form)
    uploader_name: Optional[str] = Form(None),
    location: Optional[str] = Form(None),

    # Get a database session using the dependency defined in database.py
    db: Session = Depends(get_db)
):
    """
    Uploads an image file and its associated metadata.

    - Saves the image file locally.
    - Creates a record in the database with metadata and the saved filename.
    - Returns the created metadata object.
    """
    # Log the received file and metadata (optional)
    print(f"Received upload: filename={upload_file.filename}, uploader_name={uploader_name}, location={location}")

    # 1. Save the image file locally using the crud function
    try:
        unique_filename = await crud.save_image_file(upload_file)
        print(f"File saved successfully with unique filename: {unique_filename}")
    except Exception as e:
        # If saving fails, raise an HTTP exception with a 500 status code
        print(f"Error during file saving: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save image file: {e}")

    # 2. Create metadata in the database using the crud function
    try:
        # Create a Pydantic schema instance for the metadata
        metadata_create = schemas.ImageMetadataCreate(
            uploader_name=uploader_name,
            location=location
        )
        # Call the CRUD function to create the database record
        db_metadata = crud.create_image_metadata(
            db=db,
            filename=unique_filename, # Pass the unique filename generated during saving
            original_filename=upload_file.filename, # Pass the original filename
            metadata=metadata_create # Pass the metadata schema instance
        )
        print(f"Metadata created successfully for filename: {unique_filename}")
    except Exception as e:
        # If database operation fails, raise an HTTP exception
        # You might want to add more specific error handling here (e.g., for DB errors)
        print(f"Error during metadata creation: {e}")
        # TODO: Consider cleaning up the saved file if metadata creation fails
        raise HTTPException(status_code=500, detail=f"Failed to create image metadata: {e}")


    # Return the created metadata object (which matches the response_model schema)
    return db_metadata

# Define the API endpoint to list all image metadata
# HTTP Method: GET
# Path: /images/
# response_model: Specifies the schema for the response body (a list of Pydantic models)
@app.get("/images/", response_model=List[schemas.ImageMetadataDisplay])
# Define the function that handles the request
# It takes optional skip/limit parameters for pagination and a database session
def list_images_metadata(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves a list of all image metadata records.
    Supports basic pagination with skip and limit parameters.
    """
    print(f"Fetching image metadata: skip={skip}, limit={limit}")
    # Call the CRUD function to get the list of images
    images = crud.get_images_metadata(db, skip=skip, limit=limit)
    print(f"Found {len(images)} images.")
    # Return the list of image metadata objects
    return images

# Define the API endpoint to get metadata for a single image by ID
# HTTP Method: GET
# Path: /images/{image_id} - {image_id} is a path parameter
# response_model: Specifies the schema for the response body (a single Pydantic model)
@app.get("/images/{image_id}", response_model=schemas.ImageMetadataDisplay)
# Define the function that handles the request
# It takes the image_id from the path and a database session
def get_image_metadata_by_id(image_id: int, db: Session = Depends(get_db)):
    """
    Retrieves metadata for a specific image by its ID.

    - Returns the metadata if found.
    - Returns 404 Not Found if the image ID does not exist.
    """
    print(f"Fetching metadata for image ID: {image_id}")
    # Call the CRUD function to get the image metadata by ID
    db_image = crud.get_image_metadata(db, image_id=image_id)

    # Check if an image was found
    if db_image is None:
        # If not found, raise an HTTP exception with a 404 status code
        print(f"Image with ID {image_id} not found.")
        raise HTTPException(status_code=404, detail="Image not found")

    print(f"Found image metadata for ID {image_id}.")
    # Return the found image metadata object
    return db_image

# Note: API to rate an image and Admin APIs are for future weeks.
# The "show image with all its metadata and rating information" is covered by the GET endpoints,
# though rating info won't be present in MVP. The image itself is accessed via the static files endpoint /uploads/{filename}.

# Basic root endpoint to confirm the app is running
@app.get("/")
def read_root():
    """
    Basic root endpoint. Returns a welcome message.
    """
    return {"message": "Welcome to RealReview Backend MVP"}

# To run this application locally:
# 1. Make sure you are in the backend/ directory.
# 2. Activate your virtual environment (`source venv/bin/activate` or `.\venv\Scripts\activate`).
# 3. Run: `uvicorn main:app --reload`
# 4. Access the API docs at http://127.0.0.1:8000/docs
