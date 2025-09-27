import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSession } from '../hooks/useSession';
import { QuoteData, Material, Finish } from '../types';
import QuoteHeader from '../components/quote/QuoteHeader';
import PartsTable from '../components/quote/PartsTable';
import QuoteSummary from '../components/quote/QuoteSummary';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Button from '../components/ui/Button';
import API_ENDPOINTS from '../config/api';


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
  const [isCheckingOut, setIsCheckingOut] = useState(false);
  const [isRedirecting, setIsRedirecting] = useState(false);

  const loadMaterials = useCallback(async () => {
    try {
      const response = await fetch(API_ENDPOINTS.GET_MATERIALS);
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
      const response = await fetch(API_ENDPOINTS.GET_QUOTE_DETAILS(quoteId), {
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
    if (id && sessionId) {
      loadQuote(id);
    }
  }, [id, sessionId, loadQuote]);


  const handlePartUpdate = async (partId: string, field: string, value: string) => {
    if (!sessionId) return;
    
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
      
      const response = await fetch(API_ENDPOINTS.UPDATE_PART(partId), {
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

  const handleDownload = async () => {
    if (!quote || !sessionId) return;
    
    try {
      const response = await fetch(API_ENDPOINTS.DOWNLOAD_FILE(quote.id), {
        headers: {
          'X-Session-ID': sessionId
        }
      });
      
      if (response.ok) {
        // Get the filename from the response headers or use a default
        const contentDisposition = response.headers.get('content-disposition');
        let filename = quote.file_name || 'design.step';
        
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="(.+)"/);
          if (filenameMatch) {
            filename = filenameMatch[1];
          }
        }
        
        // Create a blob from the response
        const blob = await response.blob();
        
        // Create a download link and trigger download
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } else {
        console.error('Download failed:', response.status, response.statusText);
        alert('Download failed. Please try again.');
      }
    } catch (error) {
      console.error('Download error:', error);
      alert('Download failed. Please try again.');
    }
  };

  const handleCheckout = async () => {
    if (!quote || isCheckingOut || !sessionId) return;
    
    setIsCheckingOut(true);
    
    try {
      // Create Shopify cart using Storefront API
      const response = await fetch(API_ENDPOINTS.CHECKOUT(quote.id), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId,
        },
        body: JSON.stringify({}),
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.data && data.data.checkout_url) {
          // Show redirecting state
          setIsCheckingOut(false);
          setIsRedirecting(true);
          
          // Small delay to show the redirecting state, then redirect
          setTimeout(() => {
            window.location.href = data.data.checkout_url;
          }, 1000);
        } else {
          console.error('Cart creation response missing checkout URL:', data);
          alert('Cart creation failed: No checkout URL received');
          setIsCheckingOut(false);
          setIsRedirecting(false);
        }
      } else {
        const errorData = await response.json();
        console.error('Cart creation failed:', errorData);
        
        // Format error message properly
        let errorMessage = 'Unknown error';
        if (errorData.detail) {
          if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else if (Array.isArray(errorData.detail)) {
            errorMessage = errorData.detail.map((err: any) => 
              typeof err === 'string' ? err : JSON.stringify(err)
            ).join(', ');
          } else {
            errorMessage = JSON.stringify(errorData.detail);
          }
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
        
        alert(`Cart creation failed: ${errorMessage}`);
        setIsCheckingOut(false);
        setIsRedirecting(false);
      }
    } catch (error) {
      console.error('Cart creation error:', error);
      alert('Cart creation failed: Network error');
      setIsCheckingOut(false);
      setIsRedirecting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center bg-white rounded-2xl shadow-xl p-8 max-w-md mx-4">
          <LoadingSpinner size="lg" text="Loading quote..." />
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
          <Button onClick={() => navigate('/')} size="lg">
            Back to Home
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100">
      <QuoteHeader quote={quote} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Parts List - Takes up 2/3 of the width */}
          <div className="lg:col-span-2">
            <PartsTable
              parts={quote.parts}
              materials={materials}
              finishes={finishes}
              quantityInputs={quantityInputs}
              animatingPrices={animatingPrices}
              onPartUpdate={handlePartUpdate}
              onQuantityChange={(partId, value) => {
                setQuantityInputs(prev => ({ ...prev, [partId]: value }));
                if (value !== '' && !isNaN(parseInt(value)) && parseInt(value) >= 0) {
                  handlePartUpdate(partId, 'quantity', value);
                }
              }}
              onQuantityBlur={(partId, value) => {
                const quantity = value === '' ? 0 : Math.max(0, parseInt(value) || 0);
                handlePartUpdate(partId, 'quantity', quantity.toString());
                setQuantityInputs(prev => {
                  const newState = { ...prev };
                  delete newState[partId];
                  return newState;
                });
              }}
              getUniqueMaterialTypes={getUniqueMaterialTypes}
              getMaterialGrades={getMaterialGrades}
              getMaterialThicknesses={getMaterialThicknesses}
              getUniqueFinishes={getUniqueFinishes}
              created_at={quote.created_at}
            />
          </div>
          
          {/* Quote Summary - Takes up 1/3 of the width */}
          <div className="lg:col-span-1">
            <QuoteSummary
              quote={quote}
              isCheckingOut={isCheckingOut}
              isRedirecting={isRedirecting}
              onCheckout={handleCheckout}
              onDownload={handleDownload}
            />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Quote;

