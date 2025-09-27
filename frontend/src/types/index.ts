export interface Part {
  id: string;
  part_name: string;
  part_index: number;
  material_type: string;
  material_grade: string;
  material_thickness: string;
  finish: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  body: {
    lengthIn: number;
    widthIn: number;
    heightIn: number;
    holeData: Array<any>;
  };
}

export interface QuoteData {
  id: string;
  file_name: string;
  total_price: number;
  parts: Part[];
  created_at: string;
}

export interface Material {
  type: string;
  grade: string;
  thickness: string;
  thicknessToleranceIn: string;
  minFeatureSizeIn: string;
  minPartLengthIn: string;
  minPartWidthIn: string;
  maxPartLengthIn: string;
  maxPartWidthIn: string;
}

export interface Finish {
  name: string;
  type: string;
  displayOrder: number;
  colorHex: string;
  colorString: string;
  vendorColorCode: string;
  notes: string;
}

export interface RollingNumberProps {
  value: number;
  isAnimating: boolean;
  prefix?: string;
  decimals?: number;
}
