# backend/schemas.py

# Pydantic models for data validation and serialization
# These define the structure of data expected in requests and sent in responses

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Schema for data expected when creating new image metadata (from the upload form)
class ImageMetadataCreate(BaseModel):
    # Optional fields that might come from the form
    uploader_name: Optional[str] = None
    location: Optional[str] = None
    # Note: filename, upload_timestamp, original_filename are handled by the backend logic, not expected directly in the request body

# Schema for data returned when displaying image metadata
class ImageMetadataDisplay(BaseModel):
    # Fields that will be returned from the database
    id: int
    filename: str # The unique filename on the server
    original_filename: str # The original name from the user's file
    uploader_name: Optional[str]
    upload_timestamp: datetime
    location: Optional[str]
    # rating: int = 0 # For later weeks

    # Pydantic's Config class allows configuring model behavior
    class Config:
        # from_attributes = True enables ORM mode
        # This tells Pydantic to read data from SQLAlchemy ORM models (which have attributes)
        # instead of just dictionary keys.
        from_attributes = True
