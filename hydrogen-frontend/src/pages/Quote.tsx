import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSession } from '../hooks/useSession';

// RollingNumber component for number rolling animation
interface RollingNumberProps {
  value: number;
  isAnimating: boolean;
  prefix?: string;
  decimals?: number;
}

const RollingNumber: React.FC<RollingNumberProps> = ({ value, isAnimating, prefix = '', decimals = 2 }) => {
  const [displayValue, setDisplayValue] = useState(value);
  const [isRolling, setIsRolling] = useState(false);

  useEffect(() => {
    if (isAnimating && value !== displayValue) {
      setIsRolling(true);
      
      // Animate to new value with faster duration
      const startValue = displayValue;
      const endValue = value;
      const duration = 500; // 0.5 seconds - faster animation
      const startTime = Date.now();

      const animate = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function for smooth animation
        const easeOut = 1 - Math.pow(1 - progress, 3);
        
        const currentValue = startValue + (endValue - startValue) * easeOut;
        setDisplayValue(currentValue);

        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          setDisplayValue(endValue);
          setIsRolling(false);
        }
      };

      requestAnimationFrame(animate);
    }
  }, [value, isAnimating, displayValue]);

  // Split the formatted value into individual characters for independent animation
  const formatValueWithDigits = (val: number) => {
    const formatted = val.toFixed(decimals);
    return formatted.split('');
  };

  const digits = formatValueWithDigits(displayValue);

  return (
    <span className={`inline-block transition-colors duration-200 ${isRolling ? 'text-green-600' : ''}`}>
      {prefix}
      {digits.map((digit, index) => (
        <span
          key={index}
          className={`inline-block transition-all duration-200 ${
            isRolling ? 'animate-pulse' : ''
          }`}
          style={{
            animationDelay: isRolling ? `${index * 50}ms` : '0ms',
          }}
        >
          {digit}
        </span>
      ))}
    </span>
  );
};

interface Part {
  id: string;
  name: string;
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

interface QuoteData {
  id: string;
  file_name: string;
  status: string;
  total_price: number;
  parts: Part[];
  created_at: string;
}

interface Material {
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

interface Finish {
  name: string;
  type: string;
  displayOrder: number;
  colorHex: string;
  colorString: string;
  vendorColorCode: string;
  notes: string;
}


const Quote: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { sessionId } = useSession();
  const [quote, setQuote] = useState<QuoteData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [materials, setMaterials] = useState<Material[]>([]);
  const [finishes, setFinishes] = useState<Finish[]>([]);
  const [animatingPrices, setAnimatingPrices] = useState<Set<string>>(new Set());
  const [quantityInputs, setQuantityInputs] = useState<{[key: string]: string}>({});

  const loadMaterials = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/materials');
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setMaterials(data.materials);
          setFinishes(data.finishes);
        }
      }
    } catch (error) {
      console.error('Error loading materials:', error);
    }
  }, []);

  // Helper functions to get unique values for dropdowns
  const getUniqueMaterialTypes = () => {
    const types = Array.from(new Set(materials.map(m => m.type)));
    return types.sort();
  };

  const getMaterialGrades = (selectedType: string) => {
    const grades = materials
      .filter(m => m.type === selectedType)
      .map(m => m.grade);
    return Array.from(new Set(grades)).sort();
  };


  const getMaterialThicknesses = (selectedType: string, selectedGrade: string) => {
    const thicknesses = materials
      .filter(m => m.type === selectedType && m.grade === selectedGrade)
      .map(m => m.thickness);
    return Array.from(new Set(thicknesses)).sort((a, b) => parseFloat(a) - parseFloat(b));
  };

  const getUniqueFinishes = () => {
    const finishNames = finishes.map(f => f.name);
    
    // Custom sorting: "No Deburring" first, then "Deburred", then alphabetical
    return finishNames.sort((a, b) => {
      if (a === "No Deburring") return -1;
      if (b === "No Deburring") return 1;
      if (a === "Deburred") return -1;
      if (b === "Deburred") return 1;
      return a.localeCompare(b);
    });
  };

  // Helper function to find thickness nearest to 0.125
  const findNearestThickness = (thicknesses: string[], target: number = 0.125) => {
    if (thicknesses.length === 0) return '';
    
    return thicknesses.reduce((closest, current) => {
      const currentDiff = Math.abs(parseFloat(current) - target);
      const closestDiff = Math.abs(parseFloat(closest) - target);
      return currentDiff < closestDiff ? current : closest;
    });
  };

  const loadQuote = useCallback(async (quoteId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/api/quoteDetails/${quoteId}`, {
        headers: {
          'X-Session-ID': sessionId
        }
      });
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setQuote(data.quote);
          
        } else {
          setError('Quote not found');
        }
      } else {
        setError('Failed to load quote');
      }
    } catch (error) {
      console.error('Load quote error:', error);
      setError('Error loading quote');
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    loadMaterials();
  }, [loadMaterials]);

  useEffect(() => {
    if (id) {
      loadQuote(id);
    }
  }, [id, loadQuote]);


  const handlePartUpdate = async (partId: string, field: string, value: string) => {
    try {
      const updates: any = {};
      updates[field] = value;
      
      // Auto-selection logic when material_type is selected
      if (field === 'material_type' && value) {
        // Auto-select first available grade
        const availableGrades = getMaterialGrades(value);
        if (availableGrades.length > 0) {
          const autoGrade = availableGrades[0];
          updates.material_grade = autoGrade;
          
          // Auto-select thickness nearest to 0.125
          const availableThicknesses = getMaterialThicknesses(value, autoGrade);
          if (availableThicknesses.length > 0) {
            const autoThickness = findNearestThickness(availableThicknesses);
            updates.material_thickness = autoThickness;
          }
        }
        
        // Auto-select "No Deburring" finish
        updates.finish = "No Deburring";
      }
      
      const response = await fetch(`http://localhost:8000/api/updatePart/${partId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId,
        },
        body: JSON.stringify(updates),
      });
      
      if (response.ok) {
        const result = await response.json();
        
        // Update local state with complete quote data from API
        if (result.success && result.quote) {
          setQuote(result.quote);
          
          // Trigger price animations
          setAnimatingPrices(prev => new Set(Array.from(prev).concat([partId, 'total'])));
          
          // Remove animation after 0.5 seconds (faster)
          setTimeout(() => {
            setAnimatingPrices(prev => {
              const newSet = new Set(prev);
              newSet.delete(partId);
              newSet.delete('total');
              return newSet;
            });
          }, 500);
        }
      } else {
        console.error('Failed to update part');
      }
    } catch (error) {
      console.error('Part update error:', error);
    }
  };

  const handleCheckout = async () => {
    if (!quote) return;
    
    try {
      // Create Shopify checkout
      const response = await fetch(`http://localhost:8000/api/checkout/${quote.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId,
        },
        body: JSON.stringify({
          customer_info: {
            email: 'customer@example.com',
            phone: '+1234567890'
          },
          shipping_address: {
            first_name: 'John',
            last_name: 'Doe',
            address1: '123 Main St',
            city: 'Anytown',
            province: 'CA',
            country: 'US',
            zip: '12345'
          },
          checkout_method: 'shopify'
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.checkout_url) {
          window.open(data.checkout_url, '_blank');
        }
      }
    } catch (error) {
      console.error('Checkout error:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center bg-white rounded-2xl shadow-xl p-8 max-w-md mx-4">
          <div className="loading mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading quote...</p>
        </div>
      </div>
    );
  }

  if (error || !quote) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center bg-white rounded-2xl shadow-xl p-8 max-w-md mx-4">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Quote Not Found</h1>
          <p className="text-gray-600 mb-6">{error || 'The quote you\'re looking for doesn\'t exist.'}</p>
          <button
            onClick={() => navigate('/')}
            className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 transform hover:scale-105 shadow-lg"
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md shadow-lg border-b border-white/20 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <button
                onClick={() => navigate('/')}
                className="mr-6 text-gray-500 hover:text-gray-700 transition-colors duration-200 flex items-center group"
              >
                <svg className="w-5 h-5 mr-2 group-hover:-translate-x-1 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Back
              </button>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  Quote #{quote.id}
                </h1>
                <p className="text-gray-500 text-sm mt-1">Created {new Date(quote.created_at).toLocaleDateString()}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button className="bg-white/60 hover:bg-white/80 text-gray-700 font-medium py-2 px-4 rounded-xl transition-all duration-200 border border-gray-200/50 shadow-sm hover:shadow-md">
                Share
              </button>
              <button className="bg-white/60 hover:bg-white/80 text-gray-700 font-medium py-2 px-4 rounded-xl transition-all duration-200 border border-gray-200/50 shadow-sm hover:shadow-md">
                Edit Quote
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* Parts List */}
        <div className="space-y-6">
          {quote.parts.map((part: Part, index: number) => (
            <div key={part.id} className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
              <div className="grid grid-cols-12 gap-6">
                {/* Left Section - Part Details & Configurable Dropdowns */}
                <div className="col-span-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">{part.name || `Part ${index + 1}`}</h3>
                      <p className="text-sm text-gray-500">{new Date(quote.created_at).toLocaleDateString()}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-600">Number</div>
                      <div className="text-sm font-medium text-gray-900">{part.id}</div>
                    </div>
                  </div>
                  
                  <div className="text-sm text-gray-600 mb-4">
                    <span className="font-medium">Dimensions:</span> {part.body.lengthIn?.toFixed(2) || 'N/A'}" × {part.body.widthIn?.toFixed(2) || 'N/A'}" × {part.body.heightIn?.toFixed(2) || 'N/A'}"
                  </div>
                  
                  {/* Configurable Dropdowns */}
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Material</label>
                      <select
                        value={part.material_type || ''}
                        onChange={(e) => handlePartUpdate(part.id, 'material_type', e.target.value)}
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
                        onChange={(e) => handlePartUpdate(part.id, 'material_grade', e.target.value)}
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
                        onChange={(e) => handlePartUpdate(part.id, 'material_thickness', e.target.value)}
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
                        onChange={(e) => handlePartUpdate(part.id, 'finish', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 bg-white"
                      >
                        <option value="">Select Finish</option>
                        {getUniqueFinishes().map(finish => (
                          <option key={finish} value={finish}>{finish}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
                
                
                {/* Right Section - Quantity & Pricing */}
                <div className="col-span-6">
                  <div className="text-right">
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-1">Qty</label>
                      <div className="flex items-center justify-end space-x-2">
                        <input
                          type="number"
                          value={quantityInputs[part.id] !== undefined ? quantityInputs[part.id] : (part.quantity || 1).toString()}
                          onChange={(e) => {
                            const value = e.target.value;
                            // Update local state to allow empty input during typing
                            setQuantityInputs(prev => ({
                              ...prev,
                              [part.id]: value
                            }));
                            
                            // Only update part if value is valid
                            if (value !== '' && !isNaN(parseInt(value)) && parseInt(value) >= 1) {
                              handlePartUpdate(part.id, 'quantity', value);
                            }
                          }}
                          onBlur={(e) => {
                            const value = e.target.value;
                            // On blur, ensure we have a valid quantity
                            const quantity = value === '' ? 1 : Math.max(1, parseInt(value) || 1);
                            handlePartUpdate(part.id, 'quantity', quantity.toString());
                            
                            // Clear local state to show the final value
                            setQuantityInputs(prev => {
                              const newState = {...prev};
                              delete newState[part.id];
                              return newState;
                            });
                          }}
                          className="w-16 px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                          min="1"
                          placeholder="1"
                        />
                        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                        </svg>
                      </div>
                    </div>
                    
                    <div className="mb-2">
                      <div className="text-xs text-gray-500">0% Off</div>
                      <div className={`text-sm text-gray-500 transition-all duration-500 ${animatingPrices.has(part.id) ? 'animate-pulse text-green-600' : ''}`}>
                        ${(part.total_price || 0).toFixed(2)} total
                      </div>
                    </div>
                    
                    <div className={`text-2xl font-bold text-blue-600 transition-all duration-500 ${animatingPrices.has(part.id) ? 'text-green-600' : ''}`}>
                      <RollingNumber 
                        value={part.total_price || 0} 
                        isAnimating={animatingPrices.has(part.id)}
                        prefix="$"
                        decimals={2}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Total Price Section */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl flex items-center justify-center mr-4">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
              <div>
                <h3 className="text-2xl font-bold text-gray-900">Quote Total</h3>
                <p className="text-gray-600">Final pricing for all parts</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent transition-all duration-500">
                <RollingNumber 
                  value={quote.total_price} 
                  isAnimating={animatingPrices.has('total')}
                  prefix="$"
                  decimals={2}
                />
              </div>
              <div className="text-sm text-gray-500 mt-1">USD</div>
            </div>
          </div>
        </div>
          
        {/* Checkout Section */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8">
          <div className="flex flex-col sm:flex-row gap-4">
            <button 
              onClick={handleCheckout}
              className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-semibold py-4 px-8 rounded-xl transition-all duration-200 transform hover:scale-105 shadow-lg flex items-center justify-center space-x-3"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l2.5 5m6-5v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m8 0V9a2 2 0 00-2-2H9a2 2 0 00-2 2v4.01" />
              </svg>
              <span>Checkout</span>
            </button>
            <button 
              className="flex-1 bg-white/60 hover:bg-white/80 text-gray-700 font-medium py-4 px-8 rounded-xl transition-all duration-200 border border-gray-200/50 shadow-sm hover:shadow-md flex items-center justify-center space-x-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              <span>Forward to Purchaser</span>
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Quote;

