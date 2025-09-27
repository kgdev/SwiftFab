import React from 'react';
import { Part, Material, Finish } from '../../types';
import MaterialConfig from './MaterialConfig';
import RollingNumber from '../ui/RollingNumber';

interface PartsTableProps {
  parts: Part[];
  materials: Material[];
  finishes: Finish[];
  quantityInputs: {[key: string]: string};
  animatingPrices: Set<string>;
  onPartUpdate: (partId: string, field: string, value: string) => void;
  onQuantityChange: (partId: string, value: string) => void;
  onQuantityBlur: (partId: string, value: string) => void;
  getUniqueMaterialTypes: () => string[];
  getMaterialGrades: (type: string) => string[];
  getMaterialThicknesses: (type: string, grade: string) => string[];
  getUniqueFinishes: () => string[];
  created_at: string;
}

const PartsTable: React.FC<PartsTableProps> = ({
  parts,
  materials,
  finishes,
  quantityInputs,
  animatingPrices,
  onPartUpdate,
  onQuantityChange,
  onQuantityBlur,
  getUniqueMaterialTypes,
  getMaterialGrades,
  getMaterialThicknesses,
  getUniqueFinishes,
  created_at
}) => {
  return (
    <div className="space-y-6">
      {parts.map((part: Part, index: number) => (
        <div key={part.id} className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
          <div className="grid grid-cols-12 gap-6">
            {/* Left Section - Part Details & Configurable Dropdowns */}
            <div className="col-span-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">{part.part_name || `Part ${part.part_index || index + 1}`}</h3>
                  <p className="text-sm text-gray-500">{new Date(created_at).toLocaleDateString()}</p>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-600">Number</div>
                  <div className="text-sm font-medium text-gray-900">{part.id}</div>
                </div>
              </div>
              
              <div className="text-sm text-gray-600 mb-4">
                <span className="font-medium">Dimensions:</span> {part.body.lengthIn?.toFixed(2) || 'N/A'}" × {part.body.widthIn?.toFixed(2) || 'N/A'}" × {part.body.heightIn?.toFixed(2) || 'N/A'}"
              </div>
              
              <MaterialConfig
                part={part}
                materials={materials}
                finishes={finishes}
                onPartUpdate={onPartUpdate}
                getUniqueMaterialTypes={getUniqueMaterialTypes}
                getMaterialGrades={getMaterialGrades}
                getMaterialThicknesses={getMaterialThicknesses}
                getUniqueFinishes={getUniqueFinishes}
              />
            </div>
            
            {/* Right Section - Quantity & Pricing */}
            <div className="col-span-6">
              <div className="text-right">
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Qty</label>
                  <div className="flex items-center justify-end space-x-2">
                    <input
                      type="number"
                      value={quantityInputs[part.id] !== undefined ? quantityInputs[part.id] : (part.quantity || 0).toString()}
                      onChange={(e) => onQuantityChange(part.id, e.target.value)}
                      onBlur={(e) => onQuantityBlur(part.id, e.target.value)}
                      className="w-20 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 bg-white text-center"
                      min="0"
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Unit Price:</span>
                    <span className="text-sm font-medium text-gray-900">
                      <RollingNumber
                        value={part.unit_price || 0}
                        isAnimating={animatingPrices.has(part.id)}
                        prefix="$"
                        decimals={2}
                      />
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center border-t border-gray-200 pt-2">
                    <span className="text-sm font-semibold text-gray-900">Total:</span>
                    <span className="text-lg font-bold text-green-600">
                      <RollingNumber
                        value={part.total_price || 0}
                        isAnimating={animatingPrices.has(part.id)}
                        prefix="$"
                        decimals={2}
                      />
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default PartsTable;
