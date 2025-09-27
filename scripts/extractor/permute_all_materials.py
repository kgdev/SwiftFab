#!/usr/bin/env python3
"""
Script to permute through all material combinations from materials.json
and update the quote, saving each result to a file.

Usage:
    python permute_all_materials.py --quote-id qte_123456789
    python permute_all_materials.py -q qte_123456789 --output-prefix "test_run"
"""

import json
import os
import argparse
import sys
import urllib3
from datetime import datetime
from fabworks_api_client import FabworksAPIClient

# Disable SSL certificate verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_materials_data(materials_file='samples/materials.json'):
    """Load materials data from specified materials.json file"""
    try:
        with open(materials_file, 'r') as f:
            data = json.load(f)
        return data[0]['result']['data']['json']
    except FileNotFoundError:
        print(f"❌ Error: Materials file not found: {materials_file}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in materials file: {e}")
        return None
    except Exception as e:
        print(f"❌ Error loading materials file: {e}")
        return None

def extract_material_combinations(materials_data):
    """Extract all unique material combinations"""
    combinations = []
    
    # Extract from materials array
    for material in materials_data['materials']:
        combination = {
            'materialType': material['type'],
            'materialGrade': material['grade'],
            'materialThickness': material['thickness']
        }
        if combination not in combinations:
            combinations.append(combination)
    
    return combinations

def extract_finish_options(materials_data):
    """Extract finish options - only first powder coat to reduce permutations"""
    finishes = []
    powder_coat_added = False
    
    for finish in materials_data['finishes']:
        if finish['type'] == 'powder_coat':
            # Only add the first powder coat finish
            if not powder_coat_added:
                finishes.append(finish['name'])
                powder_coat_added = True
        else:
            # Add all non-powder-coat finishes
            finishes.append(finish['name'])
    
    return finishes

def create_output_directory(quote_id, output_prefix=None):
    """Create output directory for results with quote_id and optional prefix"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Clean quote_id for filename (remove special characters)
    clean_quote_id = quote_id.replace("qte_", "").replace("-", "_")
    
    if output_prefix:
        output_dir = f"{output_prefix}_quote_{clean_quote_id}_materials_{timestamp}"
    else:
        output_dir = f"quote_{clean_quote_id}_materials_{timestamp}"
    
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def safe_filename(material_type, material_grade, thickness, finish):
    """Create a safe filename from material properties"""
    # Replace problematic characters
    safe_type = material_type.replace(" ", "_").replace("/", "-")
    safe_grade = material_grade.replace("-", "_").replace("/", "-")
    safe_thickness = thickness.replace(".", "p")
    safe_finish = finish.replace(" ", "_").replace("/", "-")
    
    return f"{safe_type}_{safe_grade}_{safe_thickness}_{safe_finish}.json"

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Permute through all material combinations and update quotes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --quote-id qte_333at6zprvFFBYez5eCTxVmFGYl
  %(prog)s -q qte_123456789 --output-prefix "test_batch"
  %(prog)s -q qte_987654321 --materials-file "samples/custom_materials.json"
        """
    )
    
    parser.add_argument(
        '--quote-id', '-q',
        required=True,
        help='Quote ID to update (e.g., qte_333at6zprvFFBYez5eCTxVmFGYl)'
    )
    
    parser.add_argument(
        '--output-prefix', '-o',
        help='Optional prefix for output directory name'
    )
    
    parser.add_argument(
        '--materials-file', '-m',
        default='samples/materials.json',
        help='Path to materials.json file (default: samples/materials.json)'
    )
    
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Show what would be done without making API calls'
    )
    
    return parser.parse_args()

def main():
    """
    Main function to permute through all material combinations
    """
    # Parse command line arguments
    args = parse_arguments()
    
    print("🚀 MATERIAL PERMUTATION SCRIPT")
    print("=" * 60)
    print(f"📋 Quote ID: {args.quote_id}")
    print(f"📂 Materials file: {args.materials_file}")
    if args.output_prefix:
        print(f"🏷️ Output prefix: {args.output_prefix}")
    if args.dry_run:
        print("🔍 DRY RUN MODE - No API calls will be made")
    print("=" * 60)
    
    # Load materials data
    print("📂 Loading materials data...")
    materials_data = load_materials_data(args.materials_file)
    if not materials_data:
        print("❌ Failed to load materials data. Exiting.")
        sys.exit(1)
    
    # Extract combinations
    print("🔍 Extracting material combinations...")
    material_combinations = extract_material_combinations(materials_data)
    finish_options = extract_finish_options(materials_data)
    
    print(f"📊 Found {len(material_combinations)} material combinations")
    print(f"🎨 Found {len(finish_options)} finish options")
    print(f"🔢 Total permutations: {len(material_combinations) * len(finish_options)}")
    
    # Create output directory
    output_dir = create_output_directory(args.quote_id, args.output_prefix)
    print(f"📁 Output directory: {output_dir}")
    
    # Initialize API client (only if not dry run)
    quote_id = args.quote_id
    client = None
    
    if not args.dry_run:
        print("🔌 Initializing API client...")
        # Configure proxy settings
        proxy_config = {
            'http': 'http://10.86.98.56:8282',
            'https': 'http://10.86.98.56:8282'
        }
        client = FabworksAPIClient()
        # Set proxy for the session
        client.session.proxies.update(proxy_config)
        # Disable SSL certificate verification
        client.session.verify = False
        print("🌐 Proxy configured: 10.86.98.56:8282")
        print("🔒 SSL certificate verification disabled")
    else:
        print("🔍 DRY RUN: API client not initialized")
    
    total_combinations = len(material_combinations) * len(finish_options)
    current_combination = 0
    
    print("\n" + "=" * 60)
    print("🎯 Starting permutation process...")
    print("=" * 60)
    
    # Loop through all combinations
    for material_combo in material_combinations:
        for finish in finish_options:
            current_combination += 1
            
            print(f"\n📝 Processing combination {current_combination}/{total_combinations}")
            print(f"   Material: {material_combo['materialType']} {material_combo['materialGrade']}")
            print(f"   Thickness: {material_combo['materialThickness']}\"")
            print(f"   Finish: {finish}")
            
            # Prepare update data
            updates = {
                'materialType': material_combo['materialType'],
                'materialGrade': material_combo['materialGrade'], 
                'materialThickness': material_combo['materialThickness'],
                'finish': finish
            }
            
            try:
                if args.dry_run:
                    # Dry run mode - just show what would be done
                    print("   🔍 DRY RUN: Would update quote with these settings")
                    print(f"   🔍 DRY RUN: Would save to file")
                    filename = safe_filename(
                        material_combo['materialType'],
                        material_combo['materialGrade'],
                        material_combo['materialThickness'],
                        finish
                    )
                    print(f"   🔍 DRY RUN: Filename would be: {filename}")
                    continue
                
                # Update all parts in quote with this combination
                print("   🔄 Updating quote...")
                result = client.update_all_parts_in_quote(quote_id, updates)
                
                if result and not result.get('error'):
                    # Get updated quote details
                    print("   📋 Getting updated quote details...")
                    quote_details = client.get_quote_details(quote_id)
                    
                    if quote_details:
                        # Create filename
                        filename = safe_filename(
                            material_combo['materialType'],
                            material_combo['materialGrade'],
                            material_combo['materialThickness'],
                            finish
                        )
                        filepath = os.path.join(output_dir, filename)
                        
                        # Prepare output data
                        output_data = {
                            'combination_info': {
                                'materialType': material_combo['materialType'],
                                'materialGrade': material_combo['materialGrade'],
                                'materialThickness': material_combo['materialThickness'],
                                'finish': finish,
                                'timestamp': datetime.now().isoformat()
                            },
                            # 'update_result': result,
                            'quote_details': quote_details
                        }
                        
                        # Save to file
                        with open(filepath, 'w') as f:
                            json.dump(output_data, f, indent=2)
                        
                        print(f"   ✅ Saved to: {filename}")
                        
                        # Extract pricing if available
                        if isinstance(quote_details, list) and len(quote_details) > 0:
                            quote_data = quote_details[0].get('result', {}).get('data', {}).get('json')
                            if quote_data and 'pricing' in quote_data:
                                total_cents = quote_data['pricing'].get('total', {}).get('price', 0)
                                total_dollars = total_cents / 100
                                print(f"   💰 Quote total: ${total_dollars:.2f}")
                    else:
                        print(f"   ❌ Failed to get quote details")
                
                else:
                    print(f"   ❌ Failed to update quote: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"   ❌ Error processing combination: {e}")
                continue
            
            # Progress indicator
            progress = (current_combination / total_combinations) * 100
            print(f"   📈 Progress: {progress:.1f}% ({current_combination}/{total_combinations})")
    
    print("\n" + "=" * 60)
    if args.dry_run:
        print("🎉 DRY RUN COMPLETE!")
        print(f"🔍 Would have processed: {current_combination} combinations")
        print(f"📁 Output directory would be: {output_dir}")
    else:
        print("🎉 PERMUTATION COMPLETE!")
        print(f"📁 Results saved in: {output_dir}")
        print(f"📊 Processed: {current_combination} combinations")
    print("=" * 60)

if __name__ == "__main__":
    main()
