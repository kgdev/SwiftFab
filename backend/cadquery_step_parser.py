#!/usr/bin/env python3
"""
CADQuery-based STEP File Parser

Alternative implementation using CADQuery (built on pythonocc-core)
More stable in headless environments, avoids FreeCAD segfault issues.
"""

import json
import uuid
import math
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
import os
import sys

# Set up logger
logger = logging.getLogger(__name__)

try:
    import cadquery as cq
    from cadquery import importers
    logger.info("[CADQuery] Successfully imported CADQuery")
except ImportError as e:
    logger.error(f"[CADQuery] Import failed: {e}")
    logger.error("Install with: pip install cadquery")
    raise


class CADQueryStepParser:
    """STEP parser using CADQuery (OpenCascade-based)"""
    
    def __init__(self):
        logger.info("[CADQuery Parser] Initialized")
    
    def parse_step_content(self, step_file_path: str) -> Dict[str, Any]:
        """Parse STEP file using CADQuery"""
        
        try:
            logger.info(f"[CADQuery Parser] Step 1: Importing STEP file from {step_file_path}")
            logger.info(f"[CADQuery Parser] Step 1.1: File exists: {os.path.exists(step_file_path)}")
            logger.info(f"[CADQuery Parser] Step 1.2: File size: {os.path.getsize(step_file_path) if os.path.exists(step_file_path) else 'N/A'} bytes")
            
            # Import STEP file using CADQuery
            logger.info("[CADQuery Parser] Step 2: Loading STEP file with CADQuery...")
            result = importers.importStep(step_file_path)
            logger.info("[CADQuery Parser] Step 3: ✅ STEP file imported successfully")
            
            # Get all solids from the imported assembly
            if isinstance(result, cq.Assembly):
                logger.info("[CADQuery Parser] Step 4: Processing assembly")
                solids = self._extract_solids_from_assembly(result)
            elif isinstance(result, cq.Workplane):
                logger.info("[CADQuery Parser] Step 4: Processing workplane")
                solids = result.solids().vals() if result.solids().size() > 0 else []
            else:
                logger.info("[CADQuery Parser] Step 4: Processing direct solid")
                solids = [result] if hasattr(result, 'BoundingBox') else []
            
            logger.info(f"[CADQuery Parser] Step 5: Found {len(solids)} solid(s)")
            
            parts_data = []
            for i, solid in enumerate(solids):
                try:
                    logger.info(f"[CADQuery Parser] Step 6.{i+1}: Processing solid {i+1}/{len(solids)}")
                    part_data = self._process_solid(solid, i)
                    parts_data.append(part_data)
                    logger.info(f"[CADQuery Parser] Step 6.{i+1}: ✅ Solid {i+1} processed")
                except Exception as solid_error:
                    logger.error(f"[CADQuery Parser] ERROR processing solid {i+1}: {str(solid_error)}")
                    raise
            
            logger.info("[CADQuery Parser] Step 7: Creating quote structure")
            result = self._create_quote_structure(parts_data, step_file_path)
            logger.info("[CADQuery Parser] Step 8: ✅ Parsing completed successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"[CADQuery Parser] ❌ FATAL ERROR: {str(e)}")
            import traceback
            logger.error(f"[CADQuery Parser] Stack trace:\n{traceback.format_exc()}")
            raise
    
    def _extract_solids_from_assembly(self, assembly: cq.Assembly) -> List:
        """Extract all solids from a CADQuery assembly"""
        solids = []
        
        # Get all shapes from assembly
        for name, shape in assembly.traverse():
            if hasattr(shape, 'val') and shape.val() is not None:
                solids.append(shape.val())
        
        return solids
    
    def _process_solid(self, solid, index: int) -> Dict[str, Any]:
        """Process a single solid and extract geometry data"""
        
        # Get bounding box
        bbox = solid.BoundingBox()
        
        # Convert from mm to inches
        length = (bbox.xmax - bbox.xmin) / 25.4
        width = (bbox.zmax - bbox.zmin) / 25.4
        height = (bbox.ymax - bbox.ymin) / 25.4
        
        # Calculate volume and surface area
        volume = solid.Volume() / (25.4**3)  # mm³ to in³
        
        # Surface area - sum of all faces
        surface_area = 0
        for face in solid.Faces():
            try:
                surface_area += face.Area() / (25.4**2)  # mm² to in²
            except:
                pass
        
        logger.info(f"[CADQuery Parser]   Dimensions: L={length:.3f}\", W={width:.3f}\", H={height:.3f}\"")
        logger.info(f"[CADQuery Parser]   Volume: {volume:.3f} in³, Surface Area: {surface_area:.3f} in²")
        
        # Detect holes
        holes = self._detect_holes(solid)
        logger.info(f"[CADQuery Parser]   Found {len(holes)} hole(s)")
        
        # Create body data
        body_data = self._create_body_data(
            volume, surface_area, length, width, height, holes, index
        )
        
        # Create part data
        part_data = self._create_part_data(body_data, index)
        
        return part_data
    
    def _detect_holes(self, solid) -> List[Dict]:
        """Detect holes in the solid"""
        holes = []
        
        try:
            # Analyze faces to find cylindrical holes
            for face_idx, face in enumerate(solid.Faces()):
                # Check if face is cylindrical (potential hole)
                if hasattr(face, 'geomType') and face.geomType() == 'CYLINDER':
                    # Get face properties
                    center = face.Center()
                    area = face.Area() / (25.4**2)  # mm² to in²
                    
                    # Estimate diameter from area (assuming circular)
                    diameter = 2 * math.sqrt(area / math.pi)
                    
                    hole_data = {
                        "idx": f"hole_{len(holes)}",
                        "axis": [0, 1, 0],
                        "faceIds": [face_idx],
                        "diameter": diameter,
                        "location": [
                            center.x / 25.4,
                            center.y / 25.4,
                            center.z / 25.4
                        ],
                        "hasBackside": True,
                        "shape": "circular",
                        "perimeter": math.pi * diameter
                    }
                    holes.append(hole_data)
                    logger.debug(f"[CADQuery Parser]     Hole detected: diameter={diameter:.3f}\"")
        
        except Exception as e:
            logger.warning(f"[CADQuery Parser]   Hole detection warning: {str(e)}")
        
        return holes
    
    def _create_body_data(self, volume: float, surface_area: float,
                         length: float, width: float, height: float,
                         holes: List[Dict], body_index: int) -> Dict[str, Any]:
        """Create body data structure"""
        
        # Calculate cut length (perimeter + holes)
        outer_perimeter = 2 * (length + width)
        hole_perimeters = sum(hole.get('perimeter', 0) for hole in holes)
        cut_length = outer_perimeter + hole_perimeters
        
        num_cuts = len(holes) + 1
        sheet_area = length * width
        mat_use_area = length * width
        
        logger.debug(f"[CADQuery Parser]     Cut length: {cut_length:.3f}\" (outer: {outer_perimeter:.3f}\", holes: {hole_perimeters:.3f}\")")
        
        return {
            "id": f"body_{self._generate_id()}",
            "createdAt": datetime.now(timezone.utc).isoformat().replace('+00:00', '.000Z'),
            "fileId": f"file_{self._generate_id()}",
            "bodyIndex": body_index,
            "thickness": str(height),
            "cutLenIn": cut_length,
            "numCuts": num_cuts,
            "matUseSqin": mat_use_area,
            "numBends": None,
            "surfAreaSqin": surface_area,
            "sheetAreaSqin": sheet_area,
            "volumeIn3": volume,
            "lengthIn": length,
            "widthIn": width,
            "heightIn": height,
            "tubeWidthIn": None,
            "tubeHeightIn": None,
            "tubeLengthIn": None,
            "tubeCornerRadiusIn": None,
            "flatLengthIn": length,
            "flatWidthIn": width,
            "bendData": None,
            "holeData": holes,
            "orientation": ["x", "z", "y"],
            "codes": [],
            "type": "sheet",
            "subType": "flat"
        }
    
    def _create_part_data(self, body_data: Dict[str, Any], part_index: int) -> Dict[str, Any]:
        """Create part data structure"""
        assembly_id = f"assm_{self._generate_id()}"
        
        return {
            "id": f"part_{self._generate_id()}",
            "assemblyId": assembly_id,
            "deleted": False,
            "customPrice": None,
            "customNotes": None,
            "createdAt": datetime.now(timezone.utc).isoformat().replace('+00:00', '.000Z'),
            "number": f"{self._generate_date_prefix()}-{self._generate_part_number()}",
            "name": f"Part {part_index + 1}",
            "bodyId": body_data["id"],
            "quantity": 1,
            "materialType": None,
            "materialGrade": None,
            "materialThickness": None,
            "finish": None,
            "holeOps": None,
            "bypassErrors": None,
            "body": body_data
        }
    
    def _create_quote_structure(self, parts_data: List[Dict], step_file_path: str) -> List[Dict[str, Any]]:
        """Create the complete quote structure"""
        quote_id = f"qte_{self._generate_id()}"
        assembly_id = f"assm_{self._generate_id()}"
        file_id = f"file_{self._generate_id()}"
        
        # Update assembly IDs in parts
        for part in parts_data:
            part["assemblyId"] = assembly_id
        
        quote_data = {
            "result": {
                "data": {
                    "json": {
                        "id": quote_id,
                        "createdAt": datetime.now(timezone.utc).isoformat().replace('+00:00', '.000Z'),
                        "number": f"{self._generate_date_prefix()}-{self._generate_quote_number()}",
                        "userId": None,
                        "orgId": None,
                        "guestId": str(uuid.uuid4()),
                        "deleted": False,
                        "shareId": None,
                        "sharedFrom": None,
                        "prodSpeed": None,
                        "customFee": None,
                        "customNotes": None,
                        "customDueDate": None,
                        "zipCode": None,
                        "needsLiftGate": None,
                        "assemblies": [{
                            "id": assembly_id,
                            "createdAt": datetime.now(timezone.utc).isoformat().replace('+00:00', '.000Z'),
                            "quoteId": quote_id,
                            "number": f"{self._generate_date_prefix()}-{self._generate_assembly_number()}",
                            "deleted": False,
                            "name": os.path.basename(step_file_path),
                            "fileId": file_id,
                            "parts": parts_data,
                            "file": {
                                "id": file_id,
                                "createdAt": datetime.now(timezone.utc).isoformat().replace('+00:00', '.000Z'),
                                "parsedVersion": 2,
                                "fileName": os.path.basename(step_file_path),
                                "fileType": "",
                                "status": "success"
                            }
                        }],
                        "pricing": {
                            "allConfigured": False,
                            "parts": [None] * len(parts_data),
                            "total": {
                                "price": 0
                            }
                        }
                    },
                    "meta": {
                        "values": self._generate_meta_values(parts_data)
                    }
                }
            }
        }
        
        return [quote_data]
    
    def parse_step_file(self, step_file_path: str, output_file_path: str = None) -> List[Dict[str, Any]]:
        """Main parsing function using CADQuery"""
        
        if not os.path.exists(step_file_path):
            raise FileNotFoundError(f"STEP file not found: {step_file_path}")
        
        logger.info("Using CADQuery parser...")
        result = self.parse_step_content(step_file_path)
        
        # Save to file if specified
        if output_file_path:
            with open(output_file_path, 'w') as f:
                json.dump(result, f, indent=4)
            logger.info(f"Quote data saved to: {output_file_path}")
        
        return result
    
    def _generate_id(self) -> str:
        """Generate a random ID"""
        import random
        import string
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=22))
    
    def _generate_date_prefix(self) -> str:
        """Generate date prefix in DD-MM format"""
        now = datetime.now()
        return f"{now.day:02d}-{now.month:02d}"
    
    def _generate_quote_number(self) -> str:
        """Generate quote number"""
        import random
        return f"{random.randint(1000, 9999)}"
    
    def _generate_part_number(self) -> str:
        """Generate part number"""
        import random
        return f"{random.randint(100, 999)}-{random.randint(100, 999)}"
    
    def _generate_assembly_number(self) -> str:
        """Generate assembly number"""
        import random
        return f"{random.randint(100, 999)}-{random.randint(100, 999)}"
    
    def _generate_meta_values(self, parts_data: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate meta values for date fields"""
        meta = {
            "createdAt": ["Date"],
            "assemblies.0.createdAt": ["Date"],
            "assemblies.0.file.createdAt": ["Date"]
        }
        
        for i in range(len(parts_data)):
            meta[f"assemblies.0.parts.{i}.createdAt"] = ["Date"]
            meta[f"assemblies.0.parts.{i}.body.createdAt"] = ["Date"]
        
        return meta


def main():
    """Main function for standalone usage"""
    if len(sys.argv) < 2:
        logger.info("Usage: python cadquery_step_parser.py <step_file_path> [output_json_path]")
        logger.info("Example: python cadquery_step_parser.py custom_parts.step quote_output.json")
        return 1
    
    step_file_path = sys.argv[1]
    output_file_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        parser = CADQueryStepParser()
        result = parser.parse_step_file(step_file_path, output_file_path)
        
        if not output_file_path:
            logger.info(json.dumps(result, indent=2))
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

