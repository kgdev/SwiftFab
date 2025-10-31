"""
Database configuration, models, and operations for SwiftFab Quote System
"""

import os
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, Column, String, Text, DateTime, Float, Integer
from sqlalchemy.orm import sessionmaker, Session, declarative_base

logger = logging.getLogger(__name__)

# Database setup
# Use PostgreSQL for Railway/cloud environments
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/swiftfab")

# Enhanced connection pool settings for Railway
# Prevents "connection reset by peer" errors in cloud environments
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,           # Verify connections before using
    pool_recycle=180,              # Recycle connections after 3 minutes (reduced from 5)
    pool_size=3,                   # Smaller pool size for Railway (reduced from 5)
    max_overflow=5,                # Reduced overflow (from 10)
    pool_timeout=30,               # Timeout for getting connection from pool
    echo_pool=False,               # Don't log pool checkouts/checkins
    connect_args={
        "connect_timeout": 10,     # Connection timeout in seconds
        "options": "-c statement_timeout=30000 -c idle_in_transaction_session_timeout=60000",  # Statement and idle timeouts
        "keepalives": 1,           # Enable TCP keepalives
        "keepalives_idle": 30,     # Start sending keepalives after 30s
        "keepalives_interval": 10, # Send keepalives every 10s
        "keepalives_count": 5,     # Drop connection after 5 failed keepalives
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database Models
class Quote(Base):
    __tablename__ = "quotes"
    
    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    file_name = Column(String)
    file_url = Column(String)  # URL to the blob storage
    file_content = Column(Text)  # JSON string of parsed data
    status = Column(String, default="created")
    total_price = Column(Float, default=0.0)
    session_id = Column(String, index=True)  # Session ID for user isolation


class Part(Base):
    __tablename__ = "parts"
    
    id = Column(String, primary_key=True, index=True)
    quote_id = Column(String, index=True)
    part_index = Column(Integer)
    name = Column(String)  # Part name
    material_type = Column(String)
    material_grade = Column(String)
    material_thickness = Column(String)
    finish = Column(String)
    quantity = Column(Integer, default=1)
    custom_price = Column(Float)
    unit_price = Column(Float, default=0.0)  # Calculated unit price
    total_price = Column(Float, default=0.0)  # Calculated total price (unit_price * quantity)
    body_data = Column(Text)  # JSON string of body data


# Create tables
Base.metadata.create_all(bind=engine)


# Database dependency for FastAPI
def get_db():
    """FastAPI dependency for database sessions"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


# Database helper functions
def safe_float_parse(value, default=0.0):
    """Safely parse a value to float with a default fallback"""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default

