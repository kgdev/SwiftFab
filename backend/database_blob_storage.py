"""
Database-based blob storage for Railway deployment
Replaces Vercel Blob storage with PostgreSQL database storage
"""

import os
import base64
import uuid
import logging
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, Column, String, Text, DateTime, LargeBinary, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timezone

# Configure logging
logger = logging.getLogger(__name__)

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
            pool_recycle=180,              # Recycle connections after 3 minutes
            pool_size=3,                   # Smaller pool size for Railway
            max_overflow=5,                # Reduced overflow
            pool_timeout=30,               # Timeout for getting connection from pool
            echo_pool=False,               # Don't log pool checkouts/checkins
            connect_args={
                "connect_timeout": 10,     # Connection timeout in seconds
                "options": "-c statement_timeout=30000 -c idle_in_transaction_session_timeout=60000",  # Timeouts
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
        start_time = datetime.now(timezone.utc)
        data_size = len(data)
        
        logger.info(f"[BLOB PUT] Starting upload: filename={filename}, size={data_size} bytes, content_type={content_type}")
        
        db = self.SessionLocal()
        try:
            # Create blob record
            blob = BlobStorage(
                filename=filename,
                content_type=content_type,
                size=data_size,
                data=data,
                metadata_json=metadata if metadata else None
            )
            
            db.add(blob)
            db.commit()
            db.refresh(blob)
            
            # Return blob URL (we'll use the blob ID as the URL)
            blob_url = f"blob://{blob.id}"
            
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(f"[BLOB PUT] Success: blob_id={blob.id}, url={blob_url}, elapsed={elapsed:.3f}s")
            
            return blob_url
            
        except Exception as e:
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.error(f"[BLOB PUT] Failed: filename={filename}, size={data_size}, error={str(e)}, elapsed={elapsed:.3f}s")
            db.rollback()
            raise
        finally:
            db.close()
    
    def get(self, blob_url: str) -> Optional[bytes]:
        """
        Retrieve file data from database
        """
        start_time = datetime.now(timezone.utc)
        blob_id = blob_url.replace("blob://", "")
        
        logger.info(f"[BLOB GET] Starting retrieval: blob_id={blob_id}, url={blob_url}")
        
        db = self.SessionLocal()
        try:
            blob = db.query(BlobStorage).filter(BlobStorage.id == blob_id).first()
            
            if blob:
                data_size = len(blob.data) if blob.data else 0
                elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
                logger.info(f"[BLOB GET] Success: blob_id={blob_id}, filename={blob.filename}, size={data_size} bytes, elapsed={elapsed:.3f}s")
                return blob.data
            else:
                elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
                logger.warning(f"[BLOB GET] Not found: blob_id={blob_id}, elapsed={elapsed:.3f}s")
                return None
                
        except Exception as e:
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.error(f"[BLOB GET] Failed: blob_id={blob_id}, error={str(e)}, elapsed={elapsed:.3f}s")
            return None
        finally:
            db.close()
    
    def delete(self, blob_url: str) -> bool:
        """
        Delete file data from database
        """
        start_time = datetime.now(timezone.utc)
        blob_id = blob_url.replace("blob://", "")
        
        logger.info(f"[BLOB DELETE] Starting deletion: blob_id={blob_id}, url={blob_url}")
        
        db = self.SessionLocal()
        try:
            blob = db.query(BlobStorage).filter(BlobStorage.id == blob_id).first()
            
            if blob:
                filename = blob.filename
                size = blob.size
                db.delete(blob)
                db.commit()
                
                elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
                logger.info(f"[BLOB DELETE] Success: blob_id={blob_id}, filename={filename}, size={size} bytes, elapsed={elapsed:.3f}s")
                return True
            else:
                elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
                logger.warning(f"[BLOB DELETE] Not found: blob_id={blob_id}, elapsed={elapsed:.3f}s")
                return False
                
        except Exception as e:
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.error(f"[BLOB DELETE] Failed: blob_id={blob_id}, error={str(e)}, elapsed={elapsed:.3f}s")
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_metadata(self, blob_url: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a blob
        """
        start_time = datetime.now(timezone.utc)
        blob_id = blob_url.replace("blob://", "")
        
        logger.info(f"[BLOB METADATA] Starting retrieval: blob_id={blob_id}, url={blob_url}")
        
        db = self.SessionLocal()
        try:
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
                elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
                logger.info(f"[BLOB METADATA] Success: blob_id={blob_id}, filename={blob.filename}, size={blob.size} bytes, elapsed={elapsed:.3f}s")
                return metadata
            else:
                elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
                logger.warning(f"[BLOB METADATA] Not found: blob_id={blob_id}, elapsed={elapsed:.3f}s")
                return None
                
        except Exception as e:
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.error(f"[BLOB METADATA] Failed: blob_id={blob_id}, error={str(e)}, elapsed={elapsed:.3f}s")
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
