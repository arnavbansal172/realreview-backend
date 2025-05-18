# backend/models.py

from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from .database import Base # Import Base from the local database module
import datetime

# Define the SQLAlchemy ORM model for image metadata
# This maps to a table in your PostgreSQL database
class ImageMetadata(Base):
    # Define the table name in the database
    __tablename__ = "image_metadata"

    # Define columns
    # id: Primary key, auto-incrementing integer
    id = Column(Integer, primary_key=True, index=True)

    # filename: The unique filename stored on the server/storage
    # Indexed for faster lookups, must be unique, cannot be null
    filename = Column(String, unique=True, index=True, nullable=False)

    # original_filename: The name of the file when it was uploaded by the user
    original_filename = Column(String, nullable=False)

    # uploader_name: Name of the user who uploaded (optional for MVP)
    uploader_name = Column(String, nullable=True)

    # upload_timestamp: When the image was uploaded
    # server_default=func.now() sets the default value to the current database time
    upload_timestamp = Column(DateTime, server_default=func.now(), nullable=False)

    # location: Location information provided by the user (optional for MVP)
    location = Column(String, nullable=True)

    # approval_status: Boolean to indicate if the image is approved by admin (for later weeks)
    # approval_status = Column(Boolean, default=False)

    # rating: Integer for image rating (for later weeks)
    # rating = Column(Integer, default=0)

    # Optional: __repr__ method for a helpful string representation when debugging
    def __repr__(self):
        return f"<ImageMetadata(id={self.id}, filename='{self.filename}', location='{self.location}')>"
