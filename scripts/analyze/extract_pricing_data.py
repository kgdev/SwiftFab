#!/usr/bin/env python3
"""
Extract pricing data from SwiftFab quote JSON files and create CSV analysis
Fixed version that correctly extracts pricing data
"""

import json
import csv
import os
import glob
from collections import defaultdict, Counter
import statistics

def extract_pricing_data():
    """Extract pricing data from all JSON files in the data directory"""
    
    data_dir = "/mnt/c/Users/kgdev/SwiftFab/data"
    all_data = []
    
    # Find all JSON files
    json_files = glob.glob(os.path.join(data_dir, "**", "*.json"), recursive=True)
    
    print(f"Found {len(json_files)} JSON files to process...")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract combination info
            combination_info = data.get('combination_info', {})
            material_type = combination_info.get('materialType', '')
            material_grade = combination_info.get('materialGrade', '')
            material_thickness = combination_info.get('materialThickness', '')
            finish = combination_info.get('finish', '')
            
            # Extract quote details
            quote_details = data.get('quote_details', [])
            
            for quote_detail in quote_details:
                result = quote_detail.get('result', {})
                quote_data = result.get('data', {}).get('json', {})
                
                # Extract assemblies and parts
                assemblies = quote_data.get('assemblies', [])
                
                # Create a mapping of part_id to part data
                part_data_map = {}
                
                for assembly in assemblies:
                    parts = assembly.get('parts', [])
                    
                    for part in parts:
                        part_id = part.get('id', '')
                        
                        # Extract part basic info
                        part_name = part.get('name', '')
                        part_number = part.get('number', '')
                        quantity = part.get('quantity', 1)
                        
                        # Extract part material properties
                        part_material_type = part.get('materialType', material_type)
                        part_material_grade = part.get('materialGrade', material_grade)
                        part_material_thickness = part.get('materialThickness', material_thickness)
                        part_finish = part.get('finish', finish)
                        
                        # Extract part dimensions and properties
                        body = part.get('body', {})
                        cut_len_in = body.get('cutLenIn', 0)
                        num_cuts = body.get('numCuts', 0)
                        mat_use_sqin = body.get('matUseSqin', 0)
                        sheet_area_sqin = body.get('sheetAreaSqin', 0)
                        surf_area_sqin = body.get('surfAreaSqin', 0)
                        volume_in3 = body.get('volumeIn3', 0)
                        length_in = body.get('lengthIn', 0)
                        thickness = body.get('thickness', 0)
                        
                        # Store part data
                        part_data_map[part_id] = {
                            'part_name': part_name,
                            'part_number': part_number,
                            'quantity': quantity,
                            'material_type': part_material_type,
                            'material_grade': part_material_grade,
                            'material_thickness': part_material_thickness,
                            'finish': part_finish,
                            'cut_len_in': cut_len_in,
                            'num_cuts': num_cuts,
                            'mat_use_sqin': mat_use_sqin,
                            'sheet_area_sqin': sheet_area_sqin,
                            'surf_area_sqin': surf_area_sqin,
                            'volume_in3': volume_in3,
                            'length_in': length_in,
                            'thickness': thickness,
                            'source_file': os.path.basename(json_file)
                        }
                
                # Now extract pricing data
                pricing_data = quote_data.get('pricing', {})
                pricing_parts = pricing_data.get('parts', [])
                
                for pricing_part in pricing_parts:
                    part_id = pricing_part.get('id', '')
                    total = pricing_part.get('total', {})
                    price_per_part = total.get('pricePerPart', 0)
                    
                    # Get the corresponding part data
                    if part_id in part_data_map:
                        part_data = part_data_map[part_id].copy()
                        part_data['part_id'] = part_id
                        part_data['price_per_part'] = price_per_part / 100.0
                        all_data.append(part_data)
                        
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
            continue
    
    return all_data

def create_csv_file(data, filename="pricing_data.csv"):
    """Create CSV file with extracted data"""
    
    if not data:
        print("No data to write to CSV")
        return
    
    # Get all fieldnames from the first record
    fieldnames = list(data[0].keys())
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Created CSV file: {filename}")
    print(f"Total records: {len(data)}")
    
    return data



def main():
    """Main function to extract and analyze pricing data"""
    
    print("Starting SwiftFab pricing data extraction (fixed version)...")
    
    # Extract data
    data = extract_pricing_data()
    
    if not data:
        print("No data extracted. Exiting.")
        return
    
    # Create CSV
    create_csv_file(data, "/mnt/c/Users/kgdev/SwiftFab/pricing_data.csv")
    
    print(f"\n=== SUMMARY ===")
    print(f"Data extraction completed successfully!")
    print(f"Total parts analyzed: {len(data)}")
    print(f"Files created:")
    print(f"  - pricing_data.csv")

if __name__ == "__main__":
    main()
