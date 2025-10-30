"""
Database-based blob storage for Railway deployment
Replaces Vercel Blob storage with PostgreSQL database storage
"""

import os
import base64
import uuid
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, Column, String, Text, DateTime, LargeBinary, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timezone

Base = declarative_base()

class BlobStorage(Base):
    """Database table for storing file blobs"""
    __tablename__ = "blob_storage"
    
    id = Column(String, primary_key=True, default=lambda: f"blob_{uuid.uuid4().hex[:8]}")
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=True)
    size = Column(Integer, nullable=False)
    data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    metadata_json = Column(Text, nullable=True)  # JSON metadata as text

class DatabaseBlobStorage:
    """Database-based blob storage implementation"""
    
    def __init__(self, database_url: str):
        # Enhanced connection pool settings for Railway
        # Prevents "connection reset by peer" errors in cloud environments
        self.engine = create_engine(
            database_url,
            pool_pre_ping=True,           # Verify connections before using
            pool_recycle=300,              # Recycle connections after 5 minutes
            pool_size=5,                   # Maximum number of connections to keep
            max_overflow=10,               # Maximum overflow connections
            pool_timeout=30,               # Timeout for getting connection from pool
            echo_pool=False,               # Don't log pool checkouts/checkins
            connect_args={
                "connect_timeout": 10,     # Connection timeout in seconds
                "options": "-c statement_timeout=30000",  # 30 second statement timeout
                "keepalives": 1,           # Enable TCP keepalives
                "keepalives_idle": 30,     # Start sending keepalives after 30s
                "keepalives_interval": 10, # Send keepalives every 10s
                "keepalives_count": 5,     # Drop connection after 5 failed keepalives
            }
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=self.engine)
    
    def put(self, filename: str, data: bytes, content_type: str = "application/octet-stream", metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store file data in database and return blob URL
        """
        db = self.SessionLocal()
        try:
            # Create blob record
            blob = BlobStorage(
                filename=filename,
                content_type=content_type,
                size=len(data),
                data=data,
                metadata_json=metadata if metadata else None
            )
            
            db.add(blob)
            db.commit()
            db.refresh(blob)
            
            # Return blob URL (we'll use the blob ID as the URL)
            blob_url = f"blob://{blob.id}"
            return blob_url
            
        except Exception as e:
            db.rollback()
            print(f"Error storing blob: {e}")
            raise
        finally:
            db.close()
    
    def get(self, blob_url: str) -> Optional[bytes]:
        """
        Retrieve file data from database
        """
        db = self.SessionLocal()
        try:
            # Extract blob ID from URL
            blob_id = blob_url.replace("blob://", "")
            
            blob = db.query(BlobStorage).filter(BlobStorage.id == blob_id).first()
            
            if blob:
                return blob.data
            else:
                return None
                
        except Exception as e:
            print(f"Error retrieving blob: {e}")
            return None
        finally:
            db.close()
    
    def delete(self, blob_url: str) -> bool:
        """
        Delete file data from database
        """
        db = self.SessionLocal()
        try:
            # Extract blob ID from URL
            blob_id = blob_url.replace("blob://", "")
            
            blob = db.query(BlobStorage).filter(BlobStorage.id == blob_id).first()
            
            if blob:
                db.delete(blob)
                db.commit()
                return True
            else:
                return False
                
        except Exception as e:
            db.rollback()
            print(f"Error deleting blob: {e}")
            return False
        finally:
            db.close()
    
    def get_metadata(self, blob_url: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a blob
        """
        db = self.SessionLocal()
        try:
            # Extract blob ID from URL
            blob_id = blob_url.replace("blob://", "")
            
            blob = db.query(BlobStorage).filter(BlobStorage.id == blob_id).first()
            
            if blob:
                metadata = {
                    "id": blob.id,
                    "filename": blob.filename,
                    "content_type": blob.content_type,
                    "size": blob.size,
                    "created_at": blob.created_at.isoformat() if blob.created_at else None,
                    "metadata": blob.metadata_json
                }
                return metadata
            else:
                return None
                
        except Exception as e:
            print(f"Error getting blob metadata: {e}")
            return None
        finally:
            db.close()

# Global instance
_blob_storage = None

def get_blob_storage() -> DatabaseBlobStorage:
    """Get the global blob storage instance"""
    global _blob_storage
    if _blob_storage is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        _blob_storage = DatabaseBlobStorage(database_url)
    return _blob_storage

# Convenience functions that match Vercel Blob API
def put(filename: str, data: bytes, content_type: str = "application/octet-stream", metadata: Optional[Dict[str, Any]] = None) -> str:
    """Store file data and return blob URL"""
    return get_blob_storage().put(filename, data, content_type, metadata)

def delete(blob_url: str) -> bool:
    """Delete file data"""
    return get_blob_storage().delete(blob_url)

def get(blob_url: str) -> Optional[bytes]:
    """Retrieve file data"""
    return get_blob_storage().get(blob_url)
