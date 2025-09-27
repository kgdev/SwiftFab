#!/usr/bin/env python3
"""
Final No Base Price Version Part Price Calculator
- No base price included, only rate parameters
- material_type + material_grade is a combination
- finish is an independent parameter, No Deburring generates no cost
- All rates are positive
"""

import pandas as pd
import numpy as np
import os

class FinalPriceCalculator:
    def __init__(self, material_params_file=None, finish_params_file=None):
        """Initialize price calculator"""
        # Auto-detect parameter files if not provided
        if material_params_file is None:
            # Look for parameter files in data directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.normpath(os.path.join(script_dir, '..', '..', 'data'))
            material_params_file = os.path.join(data_dir, 'final_material_parameters.csv')
            finish_params_file = os.path.join(data_dir, 'final_finish_parameters.csv')
        
        self.material_params_df = pd.read_csv(material_params_file)
        self.finish_params_df = pd.read_csv(finish_params_file)
        print(f"Loaded pricing parameters for {len(self.material_params_df)} material-grade combinations")
        print(f"Loaded pricing parameters for {len(self.finish_params_df)} finish types")
        
    def calculate_price(self, material_type, material_grade, finish, material_area, thickness, 
                       num_cuts, surface_area):
        """
        Calculate part price
        
        Parameters:
        - material_type: Material type (Aluminum, Steel, Stainless Steel, Galvanized Steel)
        - material_grade: Material grade (5052-H32, 6061-T6, 7075-T6, 304-2B, 1008, A36, G90)
        - finish: Finish type (Deburred, Matte Black Powder Coat, No Deburring)
        - material_area: Material usage area (square inches) - used as surface area for Deburred finish
        - thickness: Material thickness (inches)
        - num_cuts: Number of cuts
        - surface_area: Surface area (square inches) - used for non-Deburred finishes
        
        Returns:
        - Calculated price
        """
        # Find material-grade combination parameters
        material_params = self.material_params_df[
            (self.material_params_df['material_type'] == material_type) & 
            (self.material_params_df['material_grade'] == material_grade)
        ]
        
        if material_params.empty:
            raise ValueError(f"Parameters not found for material type '{material_type}' and grade '{material_grade}' combination")
            
        material_params = material_params.iloc[0]
        
        # Handle finish parameters (No Deburring is baseline with no additional cost)
        if finish == 'No Deburring':
            # No Deburring is the baseline - no additional finish cost
            finish_params = {
                'surface_rate': 0,
                'r2': 1.0,
                'mape': 0.0
            }
        else:
            # Find finish parameters for other finishes
            finish_params = self.finish_params_df[
                self.finish_params_df['finish'] == finish
            ]
            
            if finish_params.empty:
                # Default to "Matte Black Powder Coat" if finish not found
                finish_params = self.finish_params_df[
                    self.finish_params_df['finish'] == 'Matte Black Powder Coat'
                ]
                if finish_params.empty:
                    raise ValueError("Default finish 'Matte Black Powder Coat' not found in parameters")
                
            finish_params = finish_params.iloc[0]
        
        # Calculate price (no base price included)
        material_cost = material_params['material_rate'] * material_area * thickness
        cut_count_cost = material_params['cut_count_rate'] * num_cuts
        
        # Handle surface cost based on finish type
        if finish == 'No Deburring':
            # No surface cost for No Deburring
            surface_cost = 0
            effective_surface_area = 0
        elif finish == 'Deburred':
            # Use material_area (mat_use_sqin) as surface area for Deburred
            effective_surface_area = material_area
            surface_cost = finish_params['surface_rate'] * effective_surface_area
        else:
            # Use provided surface_area (surf_area_sqin) for other finishes
            effective_surface_area = surface_area
            surface_cost = finish_params['surface_rate'] * effective_surface_area
        
        total_price = material_cost + cut_count_cost + surface_cost
        
        return {
            'price': total_price,
            'cost_breakdown': {
                'material_cost': material_cost,
                'cut_count_cost': cut_count_cost,
                'surface_cost': surface_cost
            },
            'material_params': {
                'material_rate': material_params['material_rate'],
                'cut_count_rate': material_params['cut_count_rate']
            },
            'finish_params': {
                'surface_rate': finish_params['surface_rate'],
                'effective_surface_area': effective_surface_area
            },
            'accuracy': {
                'material_r2': material_params['r2'],
                'material_mape': material_params['mape'],
                'finish_r2': finish_params['r2'],
                'finish_mape': finish_params['mape']
            }
        }
    
    def get_available_materials(self):
        """Get all available material-grade combinations"""
        return self.material_params_df[['material_type', 'material_grade', 'r2', 'mape']].copy()
    
    def get_available_finishes(self):
        """Get all available finish types"""
        finishes = self.finish_params_df[['finish', 'r2', 'mape']].copy()
        # Add No Deburring as baseline finish
        no_deburring = pd.DataFrame([['No Deburring', 1.0, 0.0]], columns=['finish', 'r2', 'mape'])
        return pd.concat([no_deburring, finishes], ignore_index=True)
    

def main():
    """Main function - Initialize calculator"""
    calculator = FinalPriceCalculator()
    print("Final Price Calculator initialized successfully.")
    return calculator

if __name__ == "__main__":
    main()
