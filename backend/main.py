#!/usr/bin/env python3
"""
FastAPI backend for SwiftFab Quote System
"""

import os
import json
import uuid
import tempfile
import traceback
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Text, DateTime, Float, Integer, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import requests
import urllib3
from shopify_integration import ShopifyIntegration

# Import the STEP parser and price calculator
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts', 'parser'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts', 'analyze'))
from simple_step_parser import SimplifiedStepParser
from final_price_calculator import FinalPriceCalculator

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./quotes.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Quote(Base):
    __tablename__ = "quotes"
    
    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    file_name = Column(String)
    file_content = Column(Text)  # JSON string of parsed data
    status = Column(String, default="created")
    total_price = Column(Float, default=0.0)
    session_id = Column(String, index=True)  # Session ID for user isolation

class Part(Base):
    __tablename__ = "parts"
    
    id = Column(String, primary_key=True, index=True)
    quote_id = Column(String, index=True)
    part_index = Column(Integer)
    material_type = Column(String)
    material_grade = Column(String)
    material_thickness = Column(String)
    finish = Column(String)
    quantity = Column(Integer, default=1)
    custom_price = Column(Float)
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

class CustomerInfo(BaseModel):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

class ShippingAddress(BaseModel):
    first_name: str
    last_name: str
    address1: str
    address2: Optional[str] = None
    city: str
    province: str
    country: str = "US"
    zip: str
    phone: Optional[str] = None

class CheckoutRequest(BaseModel):
    customer_info: CustomerInfo
    shipping_address: ShippingAddress
    checkout_type: str = "checkout"  # "checkout" or "order"

# API Routes

@app.get("/")
async def root():
    return {"message": "SwiftFab Quote System API", "version": "1.0.0"}

@app.post("/api/createQuote")
async def create_quote(file: UploadFile = File(...), session_id: str = Form(...), db: Session = Depends(get_db)):
    """
    Parse STEP file and create a new quote
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.step', '.stp')):
            raise HTTPException(status_code=400, detail="Only STEP/STP files are supported")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.step') as tmp_file:
            content = await file.read()
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
                file_content=json.dumps(parsed_data),
                status="parsed",
                session_id=session_id
            )
            db.add(db_quote)
            
            # Create part records
            for i, part_data in enumerate(quote_data['assemblies'][0]['parts']):
                db_part = Part(
                    id=part_data['id'],
                    quote_id=quote_id,
                    part_index=i,
                    material_type=part_data.get('materialType'),
                    material_grade=part_data.get('materialGrade'),
                    material_thickness=part_data.get('materialThickness'),
                    finish=part_data.get('finish'),
                    quantity=part_data.get('quantity', 1),
                    custom_price=part_data.get('customPrice'),
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
        raise HTTPException(status_code=500, detail=f"Error processing STEP file: {str(e)}")

@app.put("/api/updateParts/{quote_id}")
async def update_parts(
    quote_id: str, 
    updates: PartUpdate, 
    session_id: str = Header(..., alias="X-Session-ID"),
    db: Session = Depends(get_db)
):
    """
    Update parts in a quote with new material/finish settings and recalculate pricing
    """
    try:
        # Get quote and verify session ownership
        quote = db.query(Quote).filter(Quote.id == quote_id, Quote.session_id == session_id).first()
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found or access denied")
        
        # Get all parts for this quote
        parts = db.query(Part).filter(Part.quote_id == quote_id).all()
        if not parts:
            raise HTTPException(status_code=404, detail="No parts found for this quote")
        
        # Update parts
        updated_count = 0
        for part in parts:
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
            updated_count += 1
        
        db.commit()
        
        # Calculate new pricing (simplified calculation for demo)
        total_price = await calculate_quote_pricing(quote_id, db)
        
        # print the total price
        print(f"Total price: {total_price}")
        
        # Update quote total
        quote.total_price = total_price
        db.commit()
        
        return {
            "success": True,
            "quote_id": quote_id,
            "updated_parts": updated_count,
            "total_price": total_price,
            "message": "Parts updated and pricing recalculated"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating parts: {str(e)}")

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
            # Public access - get quote without session verification
            quote = db.query(Quote).filter(Quote.id == quote_id).first()
        
        if not quote:
            logger.warning(f"Quote not found: quote_id={quote_id}, session_id={session_id}")
            raise HTTPException(status_code=404, detail=f"Quote not found or access denied for quote_id: {quote_id}")
        
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
                    except json.JSONDecodeError as json_err:
                        logger.error(f"JSON decode error for part {part.id}: {json_err}")
                        logger.error(f"Problematic body_data: {part.body_data[:200]}...")
                        # Use empty dict as fallback
                        body_data = {}
                else:
                    logger.warning(f"Empty body_data for part {part.id}")
                
                # Calculate individual part price using helper function
                logger.debug(f"Calculating price for part {part.id}")
                part_price = calculate_part_price(part, body_data)
                logger.debug(f"Calculated price for part {part.id}: {part_price}")
                
                # Validate part data before adding
                if part.quantity is None or part.quantity <= 0:
                    logger.warning(f"Invalid quantity for part {part.id}: {part.quantity}")
                    part.quantity = 1  # Default to 1 if invalid
                
                parts_data.append({
                    "id": part.id,
                    "part_index": part.part_index,
                    "material_type": part.material_type,
                    "material_grade": part.material_grade,
                    "material_thickness": part.material_thickness,
                    "finish": part.finish,
                    "quantity": part.quantity,
                    "custom_price": part.custom_price,
                    "unit_price": round(part_price, 2),
                    "total_price": round(part_price * part.quantity, 2),
                    "body": body_data
                })
                
            except Exception as part_err:
                logger.error(f"Error processing part {part.id if part else 'unknown'}: {str(part_err)}")
                logger.error(f"Part data: {part.__dict__ if part else 'No part data'}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                # Continue processing other parts instead of failing completely
                continue
        
        logger.info(f"Successfully processed {len(parts_data)} parts")
        
        return {
            "success": True,
            "quote": {
                "id": quote.id,
                "created_at": quote.created_at,
                "file_name": quote.file_name,
                "status": quote.status,
                "total_price": quote.total_price,
                "parts": parts_data
            }
        }
        
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
        
        # Include more context in the error response
        detail_msg = f"Error getting quote details: {str(e)}"
        if hasattr(e, '__class__'):
            detail_msg += f" (Error type: {e.__class__.__name__})"
        
        raise HTTPException(status_code=500, detail=detail_msg)

@app.post("/api/checkout/{quote_id}")
async def create_checkout(
    quote_id: str,
    checkout_request: CheckoutRequest,
    session_id: str = Header(..., alias="X-Session-ID"),
    db: Session = Depends(get_db)
):
    """
    Create a Shopify checkout or order for a quote
    """
    try:
        # Verify quote ownership
        quote = db.query(Quote).filter(Quote.id == quote_id, Quote.session_id == session_id).first()
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found or access denied")
        
        # Initialize Shopify integration
        shopify_integration = ShopifyIntegration()
        
        # Prepare quote data
        quote_data = {
            'id': quote.id,
            'file_name': quote.file_name,
            'total_price': quote.total_price,
            'created_at': quote.created_at.isoformat()
        }
        
        # Prepare customer info
        customer_info = {
            'email': checkout_request.customer_info.email,
            'first_name': checkout_request.customer_info.first_name,
            'last_name': checkout_request.customer_info.last_name,
            'phone': checkout_request.customer_info.phone,
            'shipping_address': {
                'first_name': checkout_request.shipping_address.first_name,
                'last_name': checkout_request.shipping_address.last_name,
                'address1': checkout_request.shipping_address.address1,
                'address2': checkout_request.shipping_address.address2,
                'city': checkout_request.shipping_address.city,
                'province': checkout_request.shipping_address.province,
                'country': checkout_request.shipping_address.country,
                'zip': checkout_request.shipping_address.zip,
                'phone': checkout_request.shipping_address.phone
            }
        }
        
        # Create checkout or order based on type
        result = shopify_integration.create_shopify_transaction(quote_data, customer_info, checkout_request.checkout_type)
        
        if result:
            return {
                "success": True,
                "checkout_type": checkout_request.checkout_type,
                "data": result
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create checkout/order")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating checkout: {str(e)}")

@app.get("/api/order-status/{order_id}")
async def get_order_status(order_id: str, session_id: str = Header(..., alias="X-Session-ID")):
    """
    Get order status from Shopify
    """
    try:
        shopify_integration = ShopifyIntegration()
        order_status = shopify_integration.get_order_status(order_id)
        
        if order_status:
            return {
                "success": True,
                "order": order_status
            }
        else:
            raise HTTPException(status_code=404, detail="Order not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting order status: {str(e)}")

@app.post("/api/createProduct/{quote_id}")
async def create_product(
    quote_id: str,
    product_data: dict,
    session_id: str = Header(..., alias="X-Session-ID"),
    db: Session = Depends(get_db)
):
    """
    Create a product in Shopify for the quote
    """
    try:
        # Verify quote ownership
        quote = db.query(Quote).filter(Quote.id == quote_id, Quote.session_id == session_id).first()
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found or access denied")
        
        # Initialize Shopify integration
        shopify_integration = ShopifyIntegration()
        
        # Prepare quote data
        quote_data = {
            'id': quote.id,
            'file_name': quote.file_name,
            'total_price': quote.total_price,
            'created_at': quote.created_at.isoformat()
        }
        
        # Create or get product
        product_info = shopify_integration.create_or_get_product(quote_data)
        
        if product_info:
            return {
                "success": True,
                "data": product_info
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create product")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")

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
                    "created_at": quote.created_at,
                    "file_name": quote.file_name,
                    "status": quote.status,
                    "total_price": quote.total_price
                }
                for quote in quotes
            ]
        }
    except Exception as e:
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
        raise HTTPException(status_code=500, detail=f"Error loading materials: {str(e)}")

async def calculate_quote_pricing(quote_id: str, db: Session) -> float:
    """
    Calculate pricing for a quote using advanced price calculator and update part prices
    """
    try:
        parts = db.query(Part).filter(Part.quote_id == quote_id).all()
        total_price = 0.0
        
        for part in parts:
            body_data = json.loads(part.body_data) if part.body_data else {}
            part_price = calculate_part_price(part, body_data)
            
            # Update part prices in database
            part.unit_price = part_price
            part.total_price = part_price * part.quantity
            
            total_price += part.total_price
        
        # Commit the part price updates
        db.commit()
        
        return round(total_price, 2)
        
    except Exception as e:
        print(f"Error calculating pricing: {e}")
        return 0.0

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
