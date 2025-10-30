#!/usr/bin/env python3
"""
FastAPI backend for SwiftFab Quote System
"""

import os
import sys
import json
import uuid
import tempfile
import traceback
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add the backend directory to Python path for Vercel
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from config import config
from sqlalchemy import create_engine, Column, String, Text, DateTime, Float, Integer, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import requests
import urllib3

from shopify_integration import ShopifyIntegration
from shopify_oauth import ShopifyOAuth


# Database blob storage for Railway
from database_blob_storage import put, delete

# Import the STEP parser and price calculator
from simple_step_parser import SimplifiedStepParser
from final_price_calculator import FinalPriceCalculator

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize Shopify integration once
shopify_integration = ShopifyIntegration()

# Database setup
# Use PostgreSQL for Vercel serverless environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/swiftfab")
# Add SSL parameters for Supabase if not already present
if "supabase.co" in DATABASE_URL and "sslmode" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
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

# Helper functions
def safe_float_parse(value, default=0.0):
    """Safely parse a value to float with a default fallback"""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def calculate_part_price(part, body_data):
    """Calculate price for a single part using the advanced price calculator"""
    logger.debug(f"Calculating price for part {part.id if part else 'unknown'}")
    
    if part.custom_price:
        logger.debug(f"Using custom price for part {part.id}: {part.custom_price}")
        return part.custom_price
    
    try:
        # Extract part parameters with validation
        material_type = part.material_type
        material_grade = part.material_grade
        material_thickness = safe_float_parse(part.material_thickness, 0.125)
        finish = part.finish
        
        logger.debug(f"Part {part.id} parameters: material_type={material_type}, material_grade={material_grade}, thickness={material_thickness}, finish={finish}")
        
        # Validate required parameters - return 0 if missing
        if not material_type:
            logger.warning(f"Missing material_type for part {part.id}, returning 0")
            return 0
        
        if not material_grade:
            logger.warning(f"Missing material_grade for part {part.id}, returning 0")
            return 0
        
        if not finish:
            logger.warning(f"Missing finish for part {part.id}, returning 0")
            return 0
        
        # Extract part dimensions from body data with validation
        material_area = safe_float_parse(body_data.get('matUseSqin', 0), 0)
        num_cuts = int(safe_float_parse(body_data.get('numCuts', 0), 0))
        surface_area = safe_float_parse(body_data.get('surfAreaSqin', 0), 0)
        
        logger.debug(f"Part {part.id} dimensions: material_area={material_area}, num_cuts={num_cuts}, surface_area={surface_area}")
        
        # Calculate price using advanced calculator
        logger.debug(f"Calling price calculator for part {part.id}")
        price_result = price_calculator.calculate_price(
            material_type=material_type,
            material_grade=material_grade,
            finish=finish,
            material_area=material_area,
            thickness=material_thickness,
            num_cuts=num_cuts,
            surface_area=surface_area
        )
        
        price = float(price_result['price'])
        logger.debug(f"Calculated price for part {part.id}: {price}")
        return price
        
    except Exception as e:
        logger.error(f"Error calculating price for part {part.id if part else 'unknown'}: {str(e)}")
        logger.error(f"Part data: {part.__dict__ if part else 'No part data'}")
        logger.error(f"Body data: {body_data}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return 0.0

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the advanced price calculator
price_calculator = FinalPriceCalculator()

# FastAPI app
app = FastAPI(
    title="SwiftFab Quote System API",
    description="API for parsing STEP files and managing quotes",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class PartUpdate(BaseModel):
    name: Optional[str] = None
    material_type: Optional[str] = None
    material_grade: Optional[str] = None
    material_thickness: Optional[str] = None
    finish: Optional[str] = None
    quantity: Optional[int] = None
    custom_price: Optional[float] = None

class QuoteResponse(BaseModel):
    id: str
    created_at: datetime
    file_name: str
    status: str
    total_price: float
    parts: List[Dict[str, Any]]

class CheckoutRequest(BaseModel):
    None

# API Routes

@app.get("/")
async def root():
    return {"message": "SwiftFab Quote System API", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    """Simple health check endpoint to test Lambda runtime"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/createQuote")
async def create_quote(file: UploadFile = File(...), session_id: str = Form(...), db: Session = Depends(get_db)):
    """
    Parse STEP file and create a new quote
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.step', '.stp')):
            raise HTTPException(status_code=400, detail="Only STEP/STP files are supported")
        
        # Read file content
        content = await file.read()
        
        # Upload to Vercel Blob storage
        file_extension = Path(file.filename).suffix
        blob_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Upload to Vercel Blob
        blob_response = put(blob_filename, content, options={"addRandomSuffix": "true"})
        file_url = blob_response.get("url")
        
        # Also create a temporary file for parsing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.step') as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Parse STEP file
            parser = SimplifiedStepParser()
            parsed_data = parser.parse_step_content(tmp_file_path)
            
            if not parsed_data or not isinstance(parsed_data, list) or len(parsed_data) == 0:
                raise HTTPException(status_code=400, detail="Failed to parse STEP file or no parts found")
            
            # Extract quote data
            quote_data = parsed_data[0]['result']['data']['json']
            quote_id = quote_data['id']
            
            # Create quote record
            db_quote = Quote(
                id=quote_id,
                file_name=file.filename,
                file_url=file_url,
                file_content=json.dumps(parsed_data),
                status="parsed",
                session_id=session_id
            )
            db.add(db_quote)
            
            # Create part records
            for i, part_data in enumerate(quote_data['assemblies'][0]['parts']):
                quantity = part_data.get('quantity', 1)
                custom_price = part_data.get('customPrice')
                
                # Calculate prices for the part
                # Create a temporary part object for price calculation
                temp_part = type('TempPart', (), {
                    'id': part_data['id'],  # Add id attribute
                    'material_type': part_data.get('materialType'),
                    'material_grade': part_data.get('materialGrade'),
                    'material_thickness': part_data.get('materialThickness'),
                    'finish': part_data.get('finish'),
                    'custom_price': custom_price
                })()
                
                part_price = calculate_part_price(temp_part, part_data['body'])
                
                # Use custom price if available, otherwise use calculated price
                unit_price = custom_price if custom_price is not None else part_price
                total_price = unit_price * quantity
                
                db_part = Part(
                    id=part_data['id'],
                    quote_id=quote_id,
                    part_index=i,
                    name=part_data.get('name', f"Part {i + 1}"),
                    material_type=part_data.get('materialType'),
                    material_grade=part_data.get('materialGrade'),
                    material_thickness=part_data.get('materialThickness'),
                    finish=part_data.get('finish'),
                    quantity=quantity,
                    custom_price=custom_price,
                    unit_price=unit_price,
                    total_price=total_price,
                    body_data=json.dumps(part_data['body'])
                )
                db.add(db_part)
            
            db.commit()
            
            return {
                "success": True,
                "quote_id": quote_id,
                "file_name": file.filename,
                "parts_count": len(quote_data['assemblies'][0]['parts']),
                "message": "Quote created successfully"
            }
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
    except Exception as e:
        db.rollback()
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error processing STEP file: {str(e)}")
        logger.error(f"Stack trace: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error processing STEP file: {str(e)}")


@app.put("/api/updatePart/{part_id}")
async def update_part(
    part_id: str, 
    updates: PartUpdate, 
    session_id: str = Header(..., alias="X-Session-ID"),
    db: Session = Depends(get_db)
):
    """
    Update a single part with new material/finish settings and recalculate pricing
    """
    try:
        # Get part and verify session ownership through quote
        part = db.query(Part).filter(Part.id == part_id).first()
        if not part:
            raise HTTPException(status_code=404, detail="Part not found")
        
        # Verify session ownership through quote
        quote = db.query(Quote).filter(Quote.id == part.quote_id, Quote.session_id == session_id).first()
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found or access denied")
        
        # Update part
        if updates.name is not None:
            part.name = updates.name
        if updates.material_type is not None:
            part.material_type = updates.material_type
        if updates.material_grade is not None:
            part.material_grade = updates.material_grade
        if updates.material_thickness is not None:
            part.material_thickness = updates.material_thickness
        if updates.finish is not None:
            part.finish = updates.finish
        if updates.quantity is not None:
            part.quantity = updates.quantity
        if updates.custom_price is not None:
            part.custom_price = updates.custom_price
        
        # Recalculate part prices if material/finish/quantity/custom_price changed
        if (updates.material_type is not None or updates.material_grade is not None or 
            updates.material_thickness is not None or updates.finish is not None or 
            updates.quantity is not None or updates.custom_price is not None):
            
            # Get body data for price calculation
            body_data = json.loads(part.body_data) if part.body_data else {}
            
            # Calculate new unit price
            if part.custom_price is not None:
                part.unit_price = part.custom_price
            else:
                part.unit_price = calculate_part_price(part, body_data)
            
            # Calculate new total price
            part.total_price = part.unit_price * part.quantity
        
        db.commit()
        
        # Calculate new pricing for the entire quote
        total_price = await calculate_quote_pricing(part.quote_id, db)
        
        # Update quote total
        quote.total_price = total_price
        db.commit()
        
        # Return the complete quote state
        return await get_quote_details(part.quote_id, session_id, db)
        
    except Exception as e:
        db.rollback()
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error updating part: {str(e)}")
        logger.error(f"Stack trace: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error updating part: {str(e)}")

@app.get("/api/quoteDetails/{quote_id}")
async def get_quote_details(quote_id: str, session_id: str = Header(None, alias="X-Session-ID"), db: Session = Depends(get_db)):
    """
    Get detailed quote information including latest pricing
    """
    logger.info(f"Getting quote details for quote_id: {quote_id}, session_id: {session_id}")
    
    try:
        # Validate input parameters
        if not quote_id or not quote_id.strip():
            logger.error(f"Invalid quote_id: '{quote_id}'")
            raise HTTPException(status_code=400, detail="Quote ID cannot be empty")
        
        # Get quote - if session_id is provided, verify ownership; otherwise allow public access
        logger.info(f"Querying database for quote: {quote_id}")
        if session_id and session_id.strip():
            # Session-based access - verify ownership
            quote = db.query(Quote).filter(Quote.id == quote_id, Quote.session_id == session_id).first()
        else:
            # raise error
            logger.error(f"Session ID is required for quote details")
            raise HTTPException(status_code=400, detail="Session ID is required for quote details")
        
        if not quote:
            logger.warning(f"Quote not found: quote_id={quote_id}, session_id={session_id}")
            # Return a simple JSON response instead of raising HTTPException to avoid Lambda issues
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": "Quote not found or access denied",
                    "quote_id": quote_id
                }
            )
        
        logger.info(f"Found quote: {quote.id}, file_name: {quote.file_name}")
        
        # Get all parts for this quote
        logger.info(f"Querying parts for quote: {quote_id}")
        parts = db.query(Part).filter(Part.quote_id == quote_id).order_by(Part.part_index).all()
        logger.info(f"Found {len(parts)} parts for quote {quote_id}")
        
        # Format parts data with individual pricing
        parts_data = []
        for i, part in enumerate(parts):
            try:
                logger.info(f"Processing part {i+1}/{len(parts)}: part_id={part.id}, part_index={part.part_index}")
                
                # Parse body_data with error handling
                body_data = {}
                if part.body_data:
                    try:
                        body_data = json.loads(part.body_data)
                        logger.debug(f"Successfully parsed body_data for part {part.id}")
                    except json.JSONDecodeError as decode_err:
                        logger.error(f"JSON decode error for part {part.id}: {decode_err}")
                        logger.error(f"Problematic body_data: {part.body_data[:200]}...")
                        # Use empty dict as fallback
                        body_data = {}
                else:
                    logger.warning(f"Empty body_data for part {part.id}")
                
                # Use stored prices from database
                logger.debug(f"Using stored prices for part {part.id}: unit_price={part.unit_price}, total_price={part.total_price}")
                
                # Validate part data before adding
                if part.quantity is None or part.quantity <= 0:
                    logger.warning(f"Invalid quantity for part {part.id}: {part.quantity}")
                    part.quantity = 1  # Default to 1 if invalid
                
                parts_data.append({
                    "id": part.id,
                    "part_name": part.name,
                    "part_index": part.part_index,
                    "material_type": part.material_type,
                    "material_grade": part.material_grade,
                    "material_thickness": part.material_thickness,
                    "finish": part.finish,
                    "quantity": part.quantity,
                    "custom_price": part.custom_price,
                    "unit_price": round(part.unit_price or 0.0, 2),
                    "total_price": round(part.total_price or 0.0, 2),
                    "body": body_data
                })
                
            except Exception as part_err:
                logger.error(f"Error processing part {part.id if part else 'unknown'}: {str(part_err)}")
                logger.error(f"Part data: {part.__dict__ if part else 'No part data'}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                # Continue processing other parts instead of failing completely
                continue
        
        logger.info(f"Successfully processed {len(parts_data)} parts")
        
        # Create response
        response = {
            "success": True,
            "quote": {
                "id": quote.id,
                "created_at": quote.created_at.isoformat() if quote.created_at else None,
                "file_name": quote.file_name,
                "status": quote.status,
                "total_price": quote.total_price,
                "parts": parts_data
            }
        }
        
        # Log response size for debugging
        response_size = len(json.dumps(response))
        logger.info(f"Response size: {response_size} bytes")
        
        if response_size > 6 * 1024 * 1024:  # 6MB limit
            logger.warning(f"Response size ({response_size} bytes) is large, may cause Lambda issues")
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log detailed error information
        error_msg = f"Unexpected error getting quote details for quote_id: {quote_id}, session_id: {session_id}"
        logger.error(error_msg)
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Return JSONResponse instead of raising HTTPException to avoid Lambda issues
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Error getting quote details: {str(e)}",
                "error_type": type(e).__name__,
                "quote_id": quote_id
            }
        )

@app.post("/api/checkout/{quote_id}")
async def create_checkout(
    quote_id: str,
    checkout_request: CheckoutRequest,
    session_id: str = Header(..., alias="X-Session-ID"),
    db: Session = Depends(get_db)
):
    """
    Create a Shopify cart, checkout, or order for a quote using Storefront API
    """
    try:
        # Verify quote ownership
        quote = db.query(Quote).filter(Quote.id == quote_id, Quote.session_id == session_id).first()
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found or access denied")
        
        # Use the global Shopify integration instance
        
        # Get parts for the quote
        parts = db.query(Part).filter(Part.quote_id == quote_id).order_by(Part.part_index).all()
        
        # Format parts data to match quoteDetails API structure
        parts_data = []
        for part in parts:
            # Parse body_data with error handling
            body_data = {}
            if part.body_data:
                try:
                    body_data = json.loads(part.body_data)
                except json.JSONDecodeError:
                    logger.error(f"JSON decode error for part {part.id}")
                    body_data = {}
            
            # Validate part data
            if part.quantity is None or part.quantity <= 0:
                part.quantity = 1  # Default to 1 if invalid
            
            parts_data.append({
                "id": part.id,
                "part_name": part.name,
                "part_index": part.part_index,
                "material_type": part.material_type,
                "material_grade": part.material_grade,
                "material_thickness": part.material_thickness,
                "finish": part.finish,
                "quantity": part.quantity,
                "custom_price": part.custom_price,
                "unit_price": round(part.unit_price or 0.0, 2),
                "total_price": round(part.total_price or 0.0, 2),
                "body": body_data
            })
        
        # Prepare quote data to match quoteDetails API structure
        quote_data = {
            'id': quote.id,
            'file_name': quote.file_name,
            'file_path': quote.file_path,
            'status': quote.status,
            'total_price': quote.total_price,
            'created_at': quote.created_at.isoformat() if quote.created_at else None,
            'parts': parts_data
        }
  
        
        # Create checkout redirect URL
        result = shopify_integration.create_checkout_redirect_url(quote_data)
        
        if result:
            return {
                "success": True,
                "data": result
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create checkout")
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error creating checkout: {str(e)}")
        logger.error(f"Stack trace: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error creating checkout: {str(e)}")

@app.get("/api/downloadFile/{quote_id}")
async def download_file(
    quote_id: str, 
    admin_key: str = Query(None, description="Admin key to bypass session check"),
    session_id: str = Header(None, alias="X-Session-ID"), 
    db: Session = Depends(get_db)
):
    """
    Download the original uploaded file for a quote
    Can be accessed with session authentication or admin key
    """
    try:
        # Get admin key from configuration
        security_config = config.config.get_security_config()
        ADMIN_KEY = security_config['admin_key']
        
        # Check if admin key is provided and valid
        if admin_key and admin_key == ADMIN_KEY:
            # Admin access - bypass session check
            quote = db.query(Quote).filter(Quote.id == quote_id).first()
            if not quote:
                raise HTTPException(status_code=404, detail="Quote not found")
        else:
            # Regular user access - require session authentication
            if not session_id:
                raise HTTPException(status_code=401, detail="Session ID required or valid admin key")
            
            quote = db.query(Quote).filter(Quote.id == quote_id, Quote.session_id == session_id).first()
            if not quote:
                raise HTTPException(status_code=404, detail="Quote not found or access denied")
        
        # Check if file URL exists
        if not quote.file_url:
            raise HTTPException(status_code=404, detail="File not found")
        
        # For blob URLs, return a redirect or the URL
        # In a production setup, you might want to proxy the file or return the URL
        return JSONResponse({
            "success": True,
            "file_url": quote.file_url,
            "file_name": quote.file_name,
            "message": "File available at the provided URL"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")


@app.get("/api/quotes")
async def list_quotes(session_id: str = Header(..., alias="X-Session-ID"), db: Session = Depends(get_db)):
    """
    List quotes for a specific session
    """
    try:
        quotes = db.query(Quote).filter(Quote.session_id == session_id).order_by(Quote.created_at.desc()).all()
        return {
            "success": True,
            "quotes": [
                {
                    "id": quote.id,
                    "created_at": quote.created_at.isoformat() if quote.created_at else None,
                    "file_name": quote.file_name,
                    "status": quote.status,
                    "total_price": quote.total_price
                }
                for quote in quotes
            ]
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error listing quotes: {str(e)}")
        logger.error(f"Stack trace: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error listing quotes: {str(e)}")

@app.get("/api/materials")
async def get_materials():
    """
    Get available material configurations
    """
    try:
        # Load materials from JSON file
        materials_file = Path(__file__).parent / "../data/materials.json"
        
        if not materials_file.exists():
            raise HTTPException(status_code=404, detail="Materials file not found")
        
        with open(materials_file, 'r') as f:
            materials_data = json.load(f)
        
        # Extract unique material configurations
        materials = []
        seen_combinations = set()
        finishes = []
        
        for item in materials_data:
            if 'result' in item and 'data' in item['result'] and 'json' in item['result']['data']:
                json_data = item['result']['data']['json']
                
                # Extract materials
                if 'materials' in json_data:
                    material_list = json_data['materials']
                    for material in material_list:
                        # Create a unique key for each material type/grade/thickness combination
                        key = f"{material['type']}|{material['grade']}|{material['thickness']}"
                        
                        if key not in seen_combinations:
                            seen_combinations.add(key)
                            materials.append({
                                "type": material['type'],
                                "grade": material['grade'],
                                "thickness": material['thickness'],
                                "thicknessToleranceIn": material.get('thicknessToleranceIn'),
                                "minFeatureSizeIn": material.get('minFeatureSizeIn'),
                                "minPartLengthIn": material.get('minPartLengthIn'),
                                "minPartWidthIn": material.get('minPartWidthIn'),
                                "maxPartLengthIn": material.get('maxPartLengthIn'),
                                "maxPartWidthIn": material.get('maxPartWidthIn')
                            })
                
                # Extract finishes
                if 'finishes' in json_data and not finishes:
                    finish_list = json_data['finishes']
                    for finish in finish_list:
                        finishes.append({
                            "name": finish['name'],
                            "type": finish.get('type', ''),
                            "displayOrder": finish.get('displayOrder', 0),
                            "colorHex": finish.get('colorHex', ''),
                            "colorString": finish.get('colorString', ''),
                            "vendorColorCode": finish.get('vendorColorCode', ''),
                            "notes": finish.get('notes', '')
                        })
        
        # Sort materials by type, then grade, then thickness
        materials.sort(key=lambda x: (x['type'], x['grade'], float(x['thickness'])))
        
        # Sort finishes by display order
        finishes.sort(key=lambda x: x['displayOrder'])
        
        return {
            "success": True,
            "materials": materials,
            "finishes": finishes
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error loading materials: {str(e)}")
        logger.error(f"Stack trace: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error loading materials: {str(e)}")

async def calculate_quote_pricing(quote_id: str, db: Session) -> float:
    """
    Calculate total pricing for a quote using stored part prices
    """
    try:
        parts = db.query(Part).filter(Part.quote_id == quote_id).all()
        total_price = 0.0
        
        for part in parts:
            # Use stored total_price from database
            total_price += part.total_price or 0.0
        
        return round(total_price, 2)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error calculating pricing for quote {quote_id}: {str(e)}")
        logger.error(f"Stack trace: {error_details}")
        return 0.0


if __name__ == "__main__":
    import uvicorn
    # Use PORT environment variable with fallback to config or 8000
    port = int(os.getenv("PORT", config.get("port", 8000, "app")))
    host = os.getenv("HOST", config.get("host", "0.0.0.0", "app"))
    uvicorn.run(app, host=host, port=port)
