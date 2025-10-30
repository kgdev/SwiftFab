#!/usr/bin/env python3
"""
Simplified STEP File Parser using FreeCAD

This is an alternative implementation using FreeCAD as the CAD library,
which might be easier to install on some systems.
"""


import json
import uuid
import math
import signal
from datetime import datetime, timezone
from typing import List, Dict, Any
import os
import sys

# Timeout handler for FreeCAD operations
class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("FreeCAD operation timed out")

# Set up signal handler for timeout (Unix only, won't work on Windows)
if hasattr(signal, 'SIGALRM'):
    signal.signal(signal.SIGALRM, timeout_handler)
    print("[Parser] Timeout handler registered")

# Add FreeCAD Python path for various environments (Amazon Linux 2023)
freecad_paths = [
    '/usr/lib/freecad-python3/lib',
    '/usr/lib/freecad/lib',
    '/usr/lib64/freecad/lib',  # Amazon Linux 2023 64-bit
    '/usr/local/lib/freecad/lib',
    '/var/task/usr/lib/freecad-python3/lib',  # Vercel Lambda path
    '/var/task/usr/lib/freecad/lib',           # Vercel Lambda path
    '/var/task/usr/lib64/freecad/lib'          # Vercel Lambda 64-bit path
]

for path in freecad_paths:
    if os.path.exists(path):
        sys.path.append(path)
        print(f"Added FreeCAD path: {path}")
        break

# Set up FreeCAD environment variables for headless operation
os.environ['FREECAD_USER_HOME'] = '/tmp/freecad'
os.environ['QT_QPA_PLATFORM'] = 'offscreen'  # Headless mode for serverless
os.environ['DISPLAY'] = ':99'  # Fake display
os.environ['QT_QPA_FONTDIR'] = '/usr/share/fonts'  # Prevent font errors
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib'  # Matplotlib config
os.makedirs('/tmp/freecad', exist_ok=True)
os.makedirs('/tmp/matplotlib', exist_ok=True)

# Disable GUI-related warnings
import warnings
warnings.filterwarnings('ignore')

print("[FreeCAD Setup] Environment configured for headless operation")

try:
    print("[FreeCAD Import] Starting FreeCAD module imports...")
    
    # Try to import FreeCAD in headless mode
    import sys
    sys.argv = ['FreeCAD', '-c']  # Force console mode
    
    import FreeCAD
    print("[FreeCAD Import] FreeCAD module imported")
    
    import Import
    print("[FreeCAD Import] Import module loaded")
    
    import Part
    print("[FreeCAD Import] Part module loaded")
    
    print("[FreeCAD Import] ✅ All FreeCAD modules imported successfully")
    
except ImportError as e:
    print(f"[FreeCAD Import] ❌ FreeCAD import failed: {e}")
    print("Available paths:", sys.path)
    raise
except Exception as e:
    print(f"[FreeCAD Import] ❌ Unexpected error during import: {e}")
    import traceback
    print(f"Stack trace:\n{traceback.format_exc()}")
    raise


class SimplifiedStepParser:
    """Simplified STEP parser using FreeCAD"""
    
    def __init__(self):
        # Create a new document
        print("[Parser] __init__: Creating new FreeCAD document...")
        try:
            self.doc = FreeCAD.newDocument("TempDoc")
            print(f"[Parser] __init__: ✅ FreeCAD document created successfully: {self.doc.Name}")
        except Exception as e:
            print(f"[Parser] __init__: ❌ CRASH in FreeCAD.newDocument(): {str(e)}")
            import traceback
            print(f"[Parser] Stack trace:\n{traceback.format_exc()}")
            raise
    
    def parse_step_content(self, step_file_path: str) -> Dict[str, Any]:
        """Parse STEP file using FreeCAD"""
        
        try:
            print(f"[Parser] Step 1: Importing STEP file from {step_file_path}")
            print(f"[Parser] Step 1.1: File exists: {os.path.exists(step_file_path)}")
            print(f"[Parser] Step 1.2: File size: {os.path.getsize(step_file_path) if os.path.exists(step_file_path) else 'N/A'} bytes")
            print(f"[Parser] Step 1.3: Document name: {self.doc.Name}")
            
            # Import the STEP file - THIS IS LIKELY WHERE IT CRASHES
            print(f"[Parser] Step 1.4: Calling Import.insert() - CRASH LIKELY HERE")
            
            # Set a timeout for the import operation (60 seconds)
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(60)
            
            try:
                Import.insert(step_file_path, self.doc.Name)
                
                # Cancel the alarm if successful
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)
                    
                print(f"[Parser] Step 2: ✅ STEP file imported successfully (Import.insert completed)")
            except TimeoutException as timeout_error:
                print(f"[Parser] ❌ TIMEOUT in Import.insert(): FreeCAD took too long (>60s)")
                raise Exception("FreeCAD Import.insert() timed out after 60 seconds") from timeout_error
            except Exception as import_error:
                # Cancel the alarm on error
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)
                    
                print(f"[Parser] ❌ CRASH in Import.insert(): {str(import_error)}")
                import traceback
                print(f"[Parser] Import.insert stack trace:\n{traceback.format_exc()}")
                
                # Try to get more information about the error
                error_type = type(import_error).__name__
                print(f"[Parser] Error type: {error_type}")
                
                raise Exception(f"FreeCAD Import.insert() failed ({error_type}): {str(import_error)}") from import_error
            
            # Get all objects
            objects = self.doc.Objects
            print(f"[Parser] Step 3: Found {len(objects)} objects in STEP file")
            
            parts_data = []
            
            for i, obj in enumerate(objects):
                try:
                    print(f"[Parser] Step 4.{i+1}: Processing object {i+1}/{len(objects)}")
                    if hasattr(obj, 'Shape'):
                        shape = obj.Shape
                        print(f"[Parser] Step 4.{i+1}.1: Object has Shape")
                        
                        # Get geometric properties
                        print(f"[Parser] Step 4.{i+1}.2: Calculating volume and surface area")
                        volume = shape.Volume / (25.4**3)  # Convert mm³ to in³
                        surface_area = shape.Area / (25.4**2)  # Convert mm² to in²
                        print(f"[Parser] Step 4.{i+1}.3: Volume={volume:.3f} in³, SurfaceArea={surface_area:.3f} in²")
                        
                        # Get bounding box
                        print(f"[Parser] Step 4.{i+1}.4: Calculating bounding box")
                        bbox = shape.BoundBox
                        length = (bbox.XMax - bbox.XMin) / 25.4  # Length is X-axis dimension
                        width = (bbox.ZMax - bbox.ZMin) / 25.4   # Width is Z-axis dimension  
                        height = (bbox.YMax - bbox.YMin) / 25.4  # Height is Y-axis dimension (thickness)
                        print(f"[Parser] Step 4.{i+1}.5: BBox - L={length:.3f}\", W={width:.3f}\", H={height:.3f}\"")
                        
                        # Detect holes and get wire perimeter data
                        print(f"[Parser] Step 4.{i+1}.6: Detecting holes and wire perimeters")
                        holes, wire_perimeters = self._detect_holes_freecad(shape)
                        print(f"[Parser] Step 4.{i+1}.7: Found {len(holes)} holes")
                        
                        # Create body data with enhanced geometric analysis
                        print(f"[Parser] Step 4.{i+1}.8: Creating body data")
                        body_data = self._create_body_data_enhanced(
                            volume, surface_area, length, width, height, holes, shape,
                            i, wire_perimeters
                        )
                        print(f"[Parser] Step 4.{i+1}.9: Body data created")
                        
                        # Create part data
                        print(f"[Parser] Step 4.{i+1}.10: Creating part data")
                        part_data = self._create_part_data(body_data, i, obj)
                        parts_data.append(part_data)
                        print(f"[Parser] Step 4.{i+1}.11: Part {i+1} completed")
                    else:
                        print(f"[Parser] Step 4.{i+1}: Object has no Shape attribute, skipping")
                except Exception as obj_error:
                    print(f"[Parser] ERROR processing object {i+1}: {str(obj_error)}")
                    raise
            
            print(f"[Parser] Step 5: Creating quote structure")
            result = self._create_quote_structure(parts_data, step_file_path)
            print(f"[Parser] Step 6: ✅ Parsing completed successfully")
            return result
            
        except Exception as e:
            print(f"[Parser] ❌ FATAL ERROR in parse_step_content: {str(e)}")
            import traceback
            print(f"[Parser] Stack trace:\n{traceback.format_exc()}")
            raise
        finally:
            # Clean up
            if self.doc:
                print(f"[Parser] Cleanup: Closing FreeCAD document")
                FreeCAD.closeDocument(self.doc.Name)
                print(f"[Parser] Cleanup: Document closed")
    
    
    def _detect_holes_freecad(self, shape):
        """Detect holes using FreeCAD Face topology analysis and return wire perimeter data"""
        holes = []
        all_wire_perimeters = []
        
        try:
            # Analyze each face to find inner wires (holes)
            for face_idx, face in enumerate(shape.Faces):
                # Print face information
                face_name = getattr(face, 'Name', f'Face_{face_idx}')
                print(f"Analyzing face: {face_name} (index {face_idx})")
                
                # Analyze all wires in the face to detect holes
                if hasattr(face, 'Wires') and len(face.Wires) > 0:
                    print(f"  Face has {len(face.Wires)} wire(s)")
                    
                    # Analyze each wire to determine if it's a hole
                    analyzed_wires, face_wire_perimeters = self._analyze_wires_for_holes(face, face_idx)
                    holes.extend(analyzed_wires)
                    all_wire_perimeters.extend(face_wire_perimeters)
                            
            # Merge opposite holes (front/back pairs into single through holes)
            holes = self._merge_opposite_holes(holes)
                    
        except Exception as e:
            print(f"Error in hole detection: {e}")
            return [], []
        
        return holes, all_wire_perimeters
    
    def _analyze_wires_for_holes(self, face, face_idx: int):
        """分析face中的所有wires，检测哪些是holes（支持各种形状）"""
        holes = []
        wire_perimeters = []
        
        try:
            wires = face.Wires
            if len(wires) <= 1:
                print(f"    No inner wires found (only {len(wires)} wire)")
                # Still record the single wire's perimeter for cut length calculation
                if len(wires) == 1:
                    wire_perimeters.append({
                        'type': 'outer',
                        'face_idx': face_idx,
                        'wire_idx': 0,
                        'perimeter': wires[0].Length / 25.4
                    })
                return holes, wire_perimeters
            
            # 计算每个wire的属性来判断哪些是holes
            wire_info = []
            for wire_idx, wire in enumerate(wires):
                try:
                    # 计算wire的基本属性
                    wire_length = wire.Length / 25.4  # 周长 (inches)
                    bbox = wire.BoundBox
                    
                    # 计算wire的中心和尺寸
                    center_x = (bbox.XMax + bbox.XMin) / 2 / 25.4
                    center_y = (bbox.YMax + bbox.YMin) / 2 / 25.4  
                    center_z = (bbox.ZMax + bbox.ZMin) / 2 / 25.4
                    width = (bbox.XMax - bbox.XMin) / 25.4
                    height = (bbox.YMax - bbox.YMin) / 25.4
                    depth = (bbox.ZMax - bbox.ZMin) / 25.4
                    
                    # Try to calculate area enclosed by wire (if possible)
                    try:
                        # Create face from wire to calculate area
                        import Part
                        wire_face = Part.Face(wire)
                        area = wire_face.Area / (25.4**2)  # Area (square inches)
                    except:
                        # If unable to create face, use bounding box area as approximation
                        area = width * height
                        print(f"Warning: Could not create face from wire {wire_idx}, using bounding box area approximation: {area:.3f} sq in")
                    
                    wire_info.append({
                        'index': wire_idx,
                        'wire': wire,
                        'length': wire_length,
                        'area': area,
                        'center': [center_x, center_y, center_z],
                        'dimensions': [width, height, depth],
                        'bbox': bbox
                    })
                    
                    print(f"    Wire {wire_idx}: Length={wire_length:.3f}\", Area={area:.4f}sq\", Center=({center_x:.3f}, {center_y:.3f}, {center_z:.3f})")
                    
                except Exception as wire_error:
                    print(f"    Error analyzing wire {wire_idx}: {wire_error}")
                    continue
            
            # 智能识别外边界wire - 不能仅依赖面积大小
            outer_wire_idx = self._identify_outer_wire(wire_info)
            
            # 记录所有wire的perimeter信息用于cut length计算
            for wire in wire_info:
                wire_type = 'outer' if wire['index'] == outer_wire_idx else 'hole'
                wire_perimeters.append({
                    'type': wire_type,
                    'face_idx': face_idx,
                    'wire_idx': wire['index'],
                    'perimeter': wire['length']
                })
            
            # 找到外边界wire和hole wires
            outer_wire = next((w for w in wire_info if w['index'] == outer_wire_idx), None)
            hole_wires = [w for w in wire_info if w['index'] != outer_wire_idx]
            
            if outer_wire:
                print(f"    Outer boundary: Wire {outer_wire['index']} (Area: {outer_wire['area']:.4f}, Perimeter: {outer_wire['length']:.3f}\")")
                
                # 处理所有hole wires
                for hole_wire in hole_wires:
                    hole_idx = hole_wire['index']
                    
                    # 计算等效直径（基于面积）
                    equiv_diameter = 2 * math.sqrt(hole_wire['area'] / math.pi)
                    
                    # 检测hole的形状类型
                    hole_shape = self._detect_hole_shape(hole_wire)
                    
                    print(f"    Detected hole: Wire {hole_idx}, Shape={hole_shape}, EquivDiam={equiv_diameter:.4f}\", Perimeter={hole_wire['length']:.3f}\"")
                    
                    hole_data = {
                        "idx": f"f{face_idx}_w{hole_idx}",
                        "axis": [0, 1, 0],
                        "faceIds": [face_idx],
                        "diameter": equiv_diameter,
                        "location": hole_wire['center'],
                        "hasBackside": True,
                        "wireIndex": hole_idx,
                        "shape": hole_shape,
                        "perimeter": hole_wire['length'],
                        "actualDimensions": {
                            "width": hole_wire['dimensions'][0],
                            "height": hole_wire['dimensions'][1], 
                            "area": hole_wire['area']
                        }
                    }
                    holes.append(hole_data)
                    
        except Exception as e:
            print(f"    Error in wire analysis: {e}")
            
        return holes, wire_perimeters
    
    def _identify_outer_wire(self, wire_info: List[Dict]) -> int:
        """智能识别外边界wire"""
        if len(wire_info) == 1:
            return wire_info[0]['index']
        
        print(f"    Analyzing {len(wire_info)} wires to identify outer boundary:")
        for wire in wire_info:
            print(f"      Wire {wire['index']}: Area={wire['area']:.4f}, Length={wire['length']:.3f}")
        
        # 策略1: 检查包含关系 - 外边界应该包含所有其他wires
        candidates = []
        
        for i, wire1 in enumerate(wire_info):
            bbox1 = wire1['bbox']
            contains_all_others = True
            contained_count = 0
            
            for j, wire2 in enumerate(wire_info):
                if i == j:
                    continue
                    
                bbox2 = wire2['bbox']
                
                # 检查wire1的bounding box是否包含wire2的bounding box (放宽一点容差)
                tolerance = 0.001  # 1mm tolerance
                if (bbox1.XMin <= (bbox2.XMin + tolerance) and bbox1.XMax >= (bbox2.XMax - tolerance) and
                    bbox1.YMin <= (bbox2.YMin + tolerance) and bbox1.YMax >= (bbox2.YMax - tolerance) and
                    bbox1.ZMin <= (bbox2.ZMin + tolerance) and bbox1.ZMax >= (bbox2.ZMax - tolerance)):
                    contained_count += 1
                else:
                    contains_all_others = False
            
            wire1['containment_score'] = contained_count
            
            if contains_all_others:
                candidates.append(wire1)
                print(f"      Wire {wire1['index']} contains ALL other wires (perfect candidate)")
            elif contained_count > 0:
                print(f"      Wire {wire1['index']} contains {contained_count} other wires")
        
        # 策略1结果: 如果有完美候选者，选择其中面积最大的
        if candidates:
            outer_wire = max(candidates, key=lambda w: w['area'])
            print(f"    ✓ Selected outer wire {outer_wire['index']} (containment + largest area)")
            return outer_wire['index']
        
        # 策略2: 选择包含最多其他wires的，如果平局则选择面积最大的
        best_containment = max(w['containment_score'] for w in wire_info)
        if best_containment > 0:
            containment_candidates = [w for w in wire_info if w['containment_score'] == best_containment]
            outer_wire = max(containment_candidates, key=lambda w: w['area'])
            print(f"    ✓ Selected outer wire {outer_wire['index']} (best containment: {best_containment} wires)")
            return outer_wire['index']
        
        # 策略3: 如果包含关系都不明确，选择面积最大的
        print("    No clear containment relationship found")
        outer_wire = max(wire_info, key=lambda w: w['area'])
        print(f"    ✓ Selected outer wire {outer_wire['index']} (largest area fallback)")
        return outer_wire['index']
    
    def _detect_hole_shape(self, wire_info: Dict) -> str:
        """检测hole的形状类型"""
        wire = wire_info['wire']
        width = wire_info['dimensions'][0]
        height = wire_info['dimensions'][1]
        area = wire_info['area']
        perimeter = wire_info['length']
        
        try:
            # 检查是否为圆形（基于面积和周长的关系）
            theoretical_circle_area = (perimeter / (2 * math.pi))**2 * math.pi
            area_ratio = abs(area - theoretical_circle_area) / theoretical_circle_area
            
            # 检查是否为正圆（宽高比接近1）
            aspect_ratio = max(width, height) / min(width, height) if min(width, height) > 0 else float('inf')
            
            if area_ratio < 0.1 and aspect_ratio < 1.2:  # 面积匹配且接近正圆
                return "circular"
            elif aspect_ratio > 2.0:  # 长宽比很大，可能是slot
                return "slot"  
            elif len(wire.Edges) <= 4 and area_ratio > 0.2:  # 边数少且不是圆形
                return "rectangular"
            else:
                return "irregular"
                
        except:
            return "unknown"
    
    def _merge_opposite_holes(self, holes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge holes that are opposite each other (front/back pairs) into single through holes"""
        if len(holes) <= 1:
            return holes
            
        merged_holes = []
        used_indices = set()
        
        for i, hole1 in enumerate(holes):
            if i in used_indices:
                continue
                
            # Look for matching holes at the same X,Z position (Y is thickness)
            matches = []
            for j, hole2 in enumerate(holes[i+1:], i+1):
                if j in used_indices:
                    continue
                    
                dx = abs(hole1['location'][0] - hole2['location'][0])
                dy = abs(hole1['location'][1] - hole2['location'][1])
                dz = abs(hole1['location'][2] - hole2['location'][2])
                
                position_tolerance = 0.01
                diameter_tolerance = 0.005
                
                diameter1 = hole1.get('diameter', 0)
                diameter2 = hole2.get('diameter', 0)
                
                if (dx < position_tolerance and 
                    dz < position_tolerance and 
                    abs(diameter1 - diameter2) < diameter_tolerance and
                    dy > 0.05):
                    
                    matches.append((j, hole2))
            
            if matches:
                # Create through hole
                match_idx, match_hole = matches[0]
                used_indices.add(i)
                used_indices.add(match_idx)
                
                avg_x = (hole1['location'][0] + match_hole['location'][0]) / 2
                avg_y = (hole1['location'][1] + match_hole['location'][1]) / 2
                avg_z = (hole1['location'][2] + match_hole['location'][2]) / 2
                avg_diameter = (hole1.get('diameter', 0) + match_hole.get('diameter', 0)) / 2
                
                # Calculate perimeter for merged hole
                # Use average perimeter if both holes have perimeter data, otherwise calculate from diameter
                perimeter1 = hole1.get('perimeter', 3.14159 * hole1.get('diameter', 0))
                perimeter2 = match_hole.get('perimeter', 3.14159 * match_hole.get('diameter', 0))
                avg_perimeter = (perimeter1 + perimeter2) / 2
                
                through_hole = {
                    "idx": f"through_{len(merged_holes)}",
                    "axis": [0, 1, 0],
                    "faceIds": hole1.get('faceIds', []) + match_hole.get('faceIds', []),
                    "diameter": avg_diameter,
                    "perimeter": avg_perimeter,
                    "location": [avg_x, avg_y, avg_z],
                    "hasBackside": True,
                    "shape": hole1.get('shape', 'circular'),  # Preserve shape information
                    "mergedFrom": [hole1.get('idx', ''), match_hole.get('idx', '')],
                    "thickness": abs(hole1['location'][1] - match_hole['location'][1])
                }
                
                merged_holes.append(through_hole)
            else:
                # Keep as single-sided hole - ensure it has perimeter information
                hole1['hasBackside'] = False
                if 'perimeter' not in hole1:
                    # Calculate perimeter if not already present
                    hole1['perimeter'] = 3.14159 * hole1.get('diameter', 0)
                merged_holes.append(hole1)
                used_indices.add(i)
        
        return merged_holes
    
    def _calculate_sheet_area_freecad(self, shape) -> float:
        """Calculate the actual sheet area using FreeCAD face analysis"""
        if not shape or not hasattr(shape, 'Faces'):
            return 0.0
            
        try:
            # For sheet metal parts, find the largest face area (represents the main sheet face)
            # This accounts for cutouts, holes, and complex shapes
            largest_face_area = 0.0
            
            for face in shape.Faces:
                face_area = face.Area / (25.4**2)  # Convert mm² to in²
                if face_area > largest_face_area:
                    largest_face_area = face_area
                    
            return largest_face_area
            
        except Exception as e:
            print(f"Error calculating sheet area: {e}")
            return 0.0

    def _create_body_data_enhanced(self, volume: float, surface_area: float,
                                  length: float, width: float, height: float,
                                  holes: List[Dict], shape,
                                  body_index: int, wire_perimeters: List[Dict]) -> Dict[str, Any]:
        """Create enhanced body data structure using actual wire perimeters"""
        
        # Calculate cut length based on merged holes and single outer boundary
        if wire_perimeters:
            # Find the largest outer perimeter (main boundary) - only count once
            outer_wires = [w for w in wire_perimeters if w['type'] == 'outer']
            if outer_wires:
                # Use the largest outer perimeter as the main boundary
                outer_perimeter = max(w['perimeter'] for w in outer_wires)
            else:
                # Fallback to rectangular approximation
                outer_perimeter = 2 * (length + width)
                
            # Use all merged holes to avoid double counting
            hole_perimeters = sum(hole.get('perimeter', 3.14159 * hole.get('diameter', 0)) for hole in holes)
            cut_length = outer_perimeter + hole_perimeters
            
            print(f"Cut length calculation:")
            print(f"  Outer perimeter (largest boundary): {outer_perimeter:.3f}\"")
            print(f"  All hole perimeters ({len(holes)} holes): {hole_perimeters:.3f}\"")
            print(f"  Total cut length: {cut_length:.3f}\"")
        else:
            # Fallback to rectangular approximation if no wire data
            outer_perimeter = 2 * (length + width)
            hole_perimeters = sum(hole.get('perimeter', 3.14159 * hole.get('diameter', 0)) for hole in holes)
            cut_length = outer_perimeter + hole_perimeters
            print(f"Using fallback cut length calculation: {cut_length:.3f}\" ({len(holes)} holes)")
        
        # Number of cuts = outer cut + one cut per hole
        num_cuts = len(holes) + 1
        
        # Calculate actual sheet area using FreeCAD face analysis
        sheet_area = self._calculate_sheet_area_freecad(shape)
        
        # If face analysis fails, fallback to bounding box
        if sheet_area <= 0:
            sheet_area = length * width
            print(f"Warning: Using fallback bounding box area for sheet area: {sheet_area:.3f} sq in")
        
        # Calculate material usage based on bounding box dimensions
        mat_use_area = length * width
        
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
    
    def _create_part_data(self, body_data: Dict[str, Any], part_index: int, obj=None) -> Dict[str, Any]:
        """Create part data structure"""
        assembly_id = f"assm_{self._generate_id()}"
        
        # Get the shape name from the FreeCAD object
        shape_name = f"Part {part_index + 1}"  # Default fallback
        if obj:
            # Try to get the object name/label from FreeCAD
            if hasattr(obj, 'Label') and obj.Label:
                shape_name = obj.Label
            elif hasattr(obj, 'Name') and obj.Name:
                shape_name = obj.Name
        
        return {
            "id": f"part_{self._generate_id()}",
            "assemblyId": assembly_id,
            "deleted": False,
            "customPrice": None,
            "customNotes": None,
            "createdAt": datetime.now(timezone.utc).isoformat().replace('+00:00', '.000Z'),
            "number": f"{self._generate_date_prefix()}-{self._generate_part_number()}",
            "name": shape_name,
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
        """Main parsing function using FreeCAD"""
        
        if not os.path.exists(step_file_path):
            raise FileNotFoundError(f"STEP file not found: {step_file_path}")
        
        print("Using FreeCAD parser...")
        result = self.parse_step_content(step_file_path)
        
        # Save to file if specified
        if output_file_path:
            with open(output_file_path, 'w') as f:
                json.dump(result, f, indent=4)
            print(f"Quote data saved to: {output_file_path}")
        
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
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python simple_step_parser.py <step_file_path> [output_json_path]")
        print("Example: python simple_step_parser.py custom_parts.step quote_output.json")
        return 1
    
    step_file_path = sys.argv[1]
    output_file_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        parser = SimplifiedStepParser()
        result = parser.parse_step_file(step_file_path, output_file_path)
        
        if not output_file_path:
            print(json.dumps(result, indent=2))
        
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
