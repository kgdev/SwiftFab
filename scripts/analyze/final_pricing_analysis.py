#!/usr/bin/env python3
"""
Final No Base Price Version Part Pricing Analysis Script
- Material-grade combinations with base cost + material rate + cut count rate
- Finish parameters with base cost + surface rate
- All rates are positive
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class FinalPricingAnalyzer:
    def __init__(self, data_file):
        self.data_file = data_file
        self.df = None
        self.material_grade_combinations = {}
        self.finish_parameters = {}
        
    def load_data(self):
        """Load and preprocess data"""
        print("Loading data...")
        self.df = pd.read_csv(self.data_file)
        
        # Data preprocessing
        self.df['material_thickness'] = pd.to_numeric(self.df['material_thickness'], errors='coerce')
        self.df['price_per_part'] = pd.to_numeric(self.df['price_per_part'], errors='coerce')
        self.df['material_grade_combo'] = self.df['material_type'] + '_' + self.df['material_grade']
        
        print(f"Data loaded: {len(self.df)} records, {self.df['material_grade_combo'].nunique()} material-grade combinations")
        
    def create_features(self):
        """Create feature variables"""
        self.df['material_area_thickness'] = self.df['mat_use_sqin'] * self.df['material_thickness']
        self.material_feature_columns = ['material_area_thickness', 'num_cuts']
        print(f"Features created: {self.material_feature_columns}")
        
    def constrained_linear_regression(self, X, y):
        """Constrained linear regression with positive rate coefficients"""
        n_features = X.shape[1]
        
        def objective(params):
            y_pred = np.dot(X, params)
            return np.sum((y - y_pred) ** 2)
        
        def constraint(params):
            return params - 0.001
        
        # Smart initial values
        feature_means = np.mean(X, axis=0)
        y_mean = np.mean(y)
        
        x0 = np.zeros(n_features)
        x0[0] = y_mean * 0.1  # Base cost
        for i in range(1, n_features):
            x0[i] = (y_mean / feature_means[i]) * 0.1 if feature_means[i] > 0 else 0.01
        
        # Optimization
        result = minimize(objective, x0, method='SLSQP', constraints={'type': 'ineq', 'fun': constraint})
        
        if result.success:
            return result.x
        else:
            # add warning
            print("Warning: Constrained linear regression failed, using simple linear regression")
            # Fallback with positive constraints
            model = LinearRegression(fit_intercept=False)
            model.fit(X, y)
            coefs = model.coef_
            if n_features > 1:
                coefs[1:] = np.maximum(coefs[1:], 0.001)
            else:
                coefs = np.maximum(coefs, 0.001)
            return coefs
    
    def analyze_material_grade_combinations(self):
        """Analyze material-grade combination parameters"""
        print("\n=== Material-Grade Analysis ===")
        
        filtered_df = self.df[self.df['finish'] == 'No Deburring'].copy()
        print(f"Using {len(filtered_df)} 'No Deburring' records")
        
        results = {}
        for combo in filtered_df['material_grade_combo'].unique():
            print(f"\nAnalyzing: {combo}")
            combo_data = filtered_df[filtered_df['material_grade_combo'] == combo].copy()
            
            # Prepare data with base cost column
            X = np.column_stack([np.ones(len(combo_data)), combo_data[self.material_feature_columns].values])
            y = combo_data['price_per_part'].values
            
            # Fit model
            coefs = self.constrained_linear_regression(X, y)
            y_pred = np.dot(X, coefs)
            
            # Calculate metrics
            r2 = r2_score(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))
            mae = mean_absolute_error(y, y_pred)
            mape = np.mean(np.abs((y - y_pred) / y)) * 100
            
            params = {
                'material_base': coefs[0],
                'material_rate': coefs[1],
                'cut_count_rate': coefs[2]
            }
            
            results[combo] = {
                'params': params,
                'metrics': {'r2': r2, 'rmse': rmse, 'mae': mae, 'mape': mape},
                'data_count': len(combo_data)
            }
            
            print(f"  R²: {r2:.4f}, RMSE: {rmse:.2f}")
            print(f"  Base: {params['material_base']:.2f}, Material: {params['material_rate']:.4f}, Cut: {params['cut_count_rate']:.4f}")
        
        self.material_grade_combinations = results
        self._save_material_parameters(results)
        return results
        
    def analyze_finish_parameters(self):
        """Analyze finish parameters using offset from No Deburring baseline"""
        print("\n=== Finish Analysis ===")
        
        finishes = [f for f in self.df['finish'].unique() if f != 'No Deburring']
        no_deburring_data = self.df[self.df['finish'] == 'No Deburring'].copy()
        results = {}
        
        for finish in finishes:
            print(f"\nAnalyzing: {finish}")
            finish_data = self.df[self.df['finish'] == finish].copy()
            
            # Create offset data
            offset_data = []
            for _, finish_row in finish_data.iterrows():
                matching_baseline = no_deburring_data[
                    (no_deburring_data['part_number'] == finish_row['part_number']) &
                    (no_deburring_data['material_type'] == finish_row['material_type']) &
                    (no_deburring_data['material_grade'] == finish_row['material_grade']) &
                    (no_deburring_data['material_thickness'] == finish_row['material_thickness'])
                ]
                
                if len(matching_baseline) > 0:
                    baseline_price = matching_baseline.iloc[0]['price_per_part']
                    offset_price = finish_row['price_per_part'] - baseline_price
                    
                    # Use different surface area metrics for different finishes
                    surface_area = finish_row['surf_area_sqin'] if finish != 'Deburred' else finish_row['mat_use_sqin']
                    
                    offset_data.append({
                        'surface_area': surface_area,
                        'offset_price': offset_price
                    })
            
            if len(offset_data) < 5:
                print(f"  Skipping: too few matched records ({len(offset_data)})")
                continue
                
            # Prepare data with base cost column
            offset_df = pd.DataFrame(offset_data)
            X = np.column_stack([np.ones(len(offset_df)), offset_df[['surface_area']].values.flatten()])
            y = offset_df['offset_price'].values
            
            # Fit model
            coefs = self.constrained_linear_regression(X, y)
            y_pred = np.dot(X, coefs)
            
            # Calculate metrics
            r2 = r2_score(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))
            mae = mean_absolute_error(y, y_pred)
            mape = np.mean(np.abs((y - y_pred) / y)) * 100 if len(y[y != 0]) > 0 else 0
            
            params = {
                'finish_base': coefs[0],
                'surface_rate': coefs[1]
            }
            
            results[finish] = {
                'params': params,
                'metrics': {'r2': r2, 'rmse': rmse, 'mae': mae, 'mape': mape},
                'data_count': len(offset_data)
            }
            
            print(f"  R²: {r2:.4f}, RMSE: {rmse:.2f}")
            print(f"  Base: {params['finish_base']:.2f}, Surface: {params['surface_rate']:.4f}")
        
        self.finish_parameters = results
        self._save_finish_parameters(results)
        return results
        
    def create_visualizations(self):
        """Create comprehensive analysis visualizations"""
        print("\nCreating visualizations...")
        
        # Create a comprehensive analysis plot
        fig = plt.figure(figsize=(20, 12))
        
        # 1. Material analysis - Base costs
        ax1 = plt.subplot(2, 4, 1)
        combinations = list(self.material_grade_combinations.keys())
        base_costs = [self.material_grade_combinations[c]['params']['material_base'] for c in combinations]
        bars1 = ax1.bar(range(len(combinations)), base_costs, color='skyblue', alpha=0.7)
        ax1.set_title('Material Base Costs', fontsize=12, fontweight='bold')
        ax1.set_xticks(range(len(combinations)))
        ax1.set_xticklabels(combinations, rotation=45, ha='right', fontsize=8)
        ax1.set_ylabel('Base Cost ($)')
        for i, bar in enumerate(bars1):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height, f'{base_costs[i]:.1f}',
                    ha='center', va='bottom', fontsize=8)
        
        # 2. Material analysis - Material rates
        ax2 = plt.subplot(2, 4, 2)
        material_rates = [self.material_grade_combinations[c]['params']['material_rate'] for c in combinations]
        bars2 = ax2.bar(range(len(combinations)), material_rates, color='lightgreen', alpha=0.7)
        ax2.set_title('Material Rates', fontsize=12, fontweight='bold')
        ax2.set_xticks(range(len(combinations)))
        ax2.set_xticklabels(combinations, rotation=45, ha='right', fontsize=8)
        ax2.set_ylabel('Rate ($/sq in)')
        for i, bar in enumerate(bars2):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height, f'{material_rates[i]:.3f}',
                    ha='center', va='bottom', fontsize=8)
        
        # 3. Material analysis - Cut count rates
        ax3 = plt.subplot(2, 4, 3)
        cut_rates = [self.material_grade_combinations[c]['params']['cut_count_rate'] for c in combinations]
        bars3 = ax3.bar(range(len(combinations)), cut_rates, color='lightcoral', alpha=0.7)
        ax3.set_title('Cut Count Rates', fontsize=12, fontweight='bold')
        ax3.set_xticks(range(len(combinations)))
        ax3.set_xticklabels(combinations, rotation=45, ha='right', fontsize=8)
        ax3.set_ylabel('Rate ($/cut)')
        for i, bar in enumerate(bars3):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height, f'{cut_rates[i]:.3f}',
                    ha='center', va='bottom', fontsize=8)
        
        # 4. Material analysis - R² scores
        ax4 = plt.subplot(2, 4, 4)
        r2_scores = [self.material_grade_combinations[c]['metrics']['r2'] for c in combinations]
        bars4 = ax4.bar(range(len(combinations)), r2_scores, color='gold', alpha=0.7)
        ax4.set_title('Model Fit (R²)', fontsize=12, fontweight='bold')
        ax4.set_xticks(range(len(combinations)))
        ax4.set_xticklabels(combinations, rotation=45, ha='right', fontsize=8)
        ax4.set_ylabel('R² Score')
        ax4.set_ylim(0, 1)
        for i, bar in enumerate(bars4):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height, f'{r2_scores[i]:.3f}',
                    ha='center', va='bottom', fontsize=8)
        
        # 5. Finish analysis - Base costs
        ax5 = plt.subplot(2, 4, 5)
        finishes = list(self.finish_parameters.keys())
        finish_bases = [self.finish_parameters[f]['params']['finish_base'] for f in finishes]
        bars5 = ax5.bar(range(len(finishes)), finish_bases, color='plum', alpha=0.7)
        ax5.set_title('Finish Base Costs', fontsize=12, fontweight='bold')
        ax5.set_xticks(range(len(finishes)))
        ax5.set_xticklabels(finishes, rotation=45, ha='right', fontsize=10)
        ax5.set_ylabel('Base Cost ($)')
        for i, bar in enumerate(bars5):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height, f'{finish_bases[i]:.2f}',
                    ha='center', va='bottom', fontsize=10)
        
        # 6. Finish analysis - Surface rates
        ax6 = plt.subplot(2, 4, 6)
        surface_rates = [self.finish_parameters[f]['params']['surface_rate'] for f in finishes]
        bars6 = ax6.bar(range(len(finishes)), surface_rates, color='lightblue', alpha=0.7)
        ax6.set_title('Surface Rates', fontsize=12, fontweight='bold')
        ax6.set_xticks(range(len(finishes)))
        ax6.set_xticklabels(finishes, rotation=45, ha='right', fontsize=10)
        ax6.set_ylabel('Rate ($/sq in)')
        for i, bar in enumerate(bars6):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2., height, f'{surface_rates[i]:.4f}',
                    ha='center', va='bottom', fontsize=10)
        
        # 7. Finish analysis - R² scores
        ax7 = plt.subplot(2, 4, 7)
        finish_r2 = [self.finish_parameters[f]['metrics']['r2'] for f in finishes]
        bars7 = ax7.bar(range(len(finishes)), finish_r2, color='orange', alpha=0.7)
        ax7.set_title('Finish Model Fit (R²)', fontsize=12, fontweight='bold')
        ax7.set_xticks(range(len(finishes)))
        ax7.set_xticklabels(finishes, rotation=45, ha='right', fontsize=10)
        ax7.set_ylabel('R² Score')
        ax7.set_ylim(0, 1)
        for i, bar in enumerate(bars7):
            height = bar.get_height()
            ax7.text(bar.get_x() + bar.get_width()/2., height, f'{finish_r2[i]:.3f}',
                    ha='center', va='bottom', fontsize=10)
        
        # 8. Parameter correlation heatmap
        ax8 = plt.subplot(2, 4, 8)
        params_matrix = []
        for combo in combinations:
            params = self.material_grade_combinations[combo]['params']
            params_matrix.append([params['material_base'], params['material_rate'], params['cut_count_rate']])
        
        params_matrix = np.array(params_matrix)
        im = ax8.imshow(params_matrix.T, cmap='viridis', aspect='auto')
        ax8.set_title('Parameter Heatmap', fontsize=12, fontweight='bold')
        ax8.set_xticks(range(len(combinations)))
        ax8.set_xticklabels(combinations, rotation=45, ha='right', fontsize=8)
        ax8.set_yticks(range(3))
        ax8.set_yticklabels(['Base Cost', 'Material Rate', 'Cut Rate'])
        ax8.set_ylabel('Parameters')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax8, shrink=0.8)
        cbar.set_label('Parameter Value')
        
        plt.suptitle('Comprehensive Pricing Analysis Dashboard', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig('data/comprehensive_pricing_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Comprehensive analysis plot saved: data/comprehensive_pricing_analysis.png")
        
    def _save_material_parameters(self, results):
        """Save material parameters to CSV"""
        data = []
        for combo, result in results.items():
            parts = combo.split('_')
            params = result['params']
            metrics = result['metrics']
            
            data.append({
                'material_type': parts[0],
                'material_grade': parts[1],
                'material_base': params['material_base'],
                'material_rate': params['material_rate'],
                'cut_count_rate': params['cut_count_rate'],
                'r2': metrics['r2'],
                'rmse': metrics['rmse'],
                'mae': metrics['mae'],
                'mape': metrics['mape'],
                'data_count': result['data_count']
            })
        
        df = pd.DataFrame(data)
        df.to_csv('data/final_material_parameters.csv', index=False)
        print("Material parameters saved: final_material_parameters.csv")
        
    def _save_finish_parameters(self, results):
        """Save finish parameters to CSV"""
        data = []
        for finish, result in results.items():
            params = result['params']
            metrics = result['metrics']
            
            data.append({
                'finish': finish,
                'finish_base': params['finish_base'],
                'surface_rate': params['surface_rate'],
                'r2': metrics['r2'],
                'rmse': metrics['rmse'],
                'mae': metrics['mae'],
                'mape': metrics['mape'],
                'data_count': result['data_count']
            })
        
        df = pd.DataFrame(data)
        df.to_csv('data/final_finish_parameters.csv', index=False)
        print("Finish parameters saved: final_finish_parameters.csv")
        
    def generate_report(self):
        """Generate concise analysis report"""
        print("\n=== Generating Report ===")
        
        report = []
        report.append("# Pricing Analysis Report")
        report.append("")
        report.append("## Pricing Formula")
        report.append("Total Price = Material Base + (Material Rate × Material Area×Thickness) + (Cut Count Rate × Number of Cuts) + Finish Base + (Surface Rate × Surface Area)")
        report.append("")
        
        report.append("## Material Analysis Summary")
        for combo, result in self.material_grade_combinations.items():
            params = result['params']
            metrics = result['metrics']
            report.append(f"**{combo}**: Base=${params['material_base']:.2f}, Material=${params['material_rate']:.4f}/sq in, Cut=${params['cut_count_rate']:.4f}/cut (R²={metrics['r2']:.3f})")
        
        report.append("")
        report.append("## Finish Analysis Summary")
        for finish, result in self.finish_parameters.items():
            params = result['params']
            metrics = result['metrics']
            report.append(f"**{finish}**: Base=${params['finish_base']:.2f}, Surface=${params['surface_rate']:.4f}/sq in (R²={metrics['r2']:.3f})")
        
        with open('data/final_pricing_analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print("Report saved: data/final_pricing_analysis_report.txt")
        
    def run_analysis(self):
        """Run complete analysis"""
        print("Starting pricing analysis...")
        
        self.load_data()
        self.create_features()
        
        material_results = self.analyze_material_grade_combinations()
        finish_results = self.analyze_finish_parameters()
        
        self.create_visualizations()
        self.generate_report()
        
        print("\nAnalysis completed!")
        print("Generated files:")
        print("- data/comprehensive_pricing_analysis.png: Complete analysis dashboard")
        print("- data/final_material_parameters.csv: Material parameters")
        print("- data/final_finish_parameters.csv: Finish parameters")
        print("- data/final_pricing_analysis_report.txt: Summary report")

if __name__ == "__main__":
    analyzer = FinalPricingAnalyzer('data/pricing_data.csv')
    analyzer.run_analysis()