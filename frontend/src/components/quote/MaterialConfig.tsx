import React from 'react';
import { Part, Material, Finish } from '../../types';

interface MaterialConfigProps {
  part: Part;
  materials: Material[];
  finishes: Finish[];
  onPartUpdate: (partId: string, field: string, value: string) => void;
  getUniqueMaterialTypes: () => string[];
  getMaterialGrades: (type: string) => string[];
  getMaterialThicknesses: (type: string, grade: string) => string[];
  getUniqueFinishes: () => string[];
}

const MaterialConfig: React.FC<MaterialConfigProps> = ({
  part,
  materials,
  finishes,
  onPartUpdate,
  getUniqueMaterialTypes,
  getMaterialGrades,
  getMaterialThicknesses,
  getUniqueFinishes
}) => {
  return (
    <div className="space-y-3">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Material</label>
        <select
          value={part.material_type || ''}
          onChange={(e) => onPartUpdate(part.id, 'material_type', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 bg-white"
        >
          <option value="">Select a Material...</option>
          {getUniqueMaterialTypes().map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Grade</label>
        <select
          value={part.material_grade || ''}
          onChange={(e) => onPartUpdate(part.id, 'material_grade', e.target.value)}
          disabled={!part.material_type}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 bg-white disabled:bg-gray-100 disabled:cursor-not-allowed"
        >
          <option value="">Select Grade</option>
          {getMaterialGrades(part.material_type).map(grade => (
            <option key={grade} value={grade}>{grade}</option>
          ))}
        </select>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Thickness</label>
        <select
          value={part.material_thickness || ''}
          onChange={(e) => onPartUpdate(part.id, 'material_thickness', e.target.value)}
          disabled={!part.material_type || !part.material_grade}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 bg-white disabled:bg-gray-100 disabled:cursor-not-allowed"
        >
          <option value="">--</option>
          {getMaterialThicknesses(part.material_type, part.material_grade).map(thickness => (
            <option key={thickness} value={thickness}>{thickness}"</option>
          ))}
        </select>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Finish</label>
        <select
          value={part.finish || ''}
          onChange={(e) => onPartUpdate(part.id, 'finish', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 bg-white"
        >
          <option value="">Select Finish</option>
          {getUniqueFinishes().map(finish => (
            <option key={finish} value={finish}>{finish}</option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default MaterialConfig;
