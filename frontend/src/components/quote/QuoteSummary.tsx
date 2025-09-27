import React, { useState, useEffect } from 'react';
import { QuoteData } from '../../types';
import RollingNumber from '../ui/RollingNumber';
import Button from '../ui/Button';

interface QuoteSummaryProps {
  quote: QuoteData;
  isCheckingOut: boolean;
  isRedirecting: boolean;
  onCheckout: () => void;
  onDownload: () => void;
}

const QuoteSummary: React.FC<QuoteSummaryProps> = ({
  quote,
  isCheckingOut,
  isRedirecting,
  onCheckout,
  onDownload
}) => {
  const [isAnimatingTotal, setIsAnimatingTotal] = useState(false);
  const [previousTotal, setPreviousTotal] = useState(0);

  // Calculate current total price
  const currentTotal = quote.parts.reduce((sum, part) => sum + (part.total_price || 0), 0);

  // Trigger animation when total price changes
  useEffect(() => {
    if (previousTotal !== 0 && previousTotal !== currentTotal) {
      setIsAnimatingTotal(true);
      const timer = setTimeout(() => {
        setIsAnimatingTotal(false);
      }, 500); // Match animation duration
      return () => clearTimeout(timer);
    }
    setPreviousTotal(currentTotal);
  }, [currentTotal, previousTotal]);

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-900">Quote Summary</h3>
      </div>
      
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Total Parts:</span>
          <span className="text-sm font-medium text-gray-900">{quote.parts.length}</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Total Quantity:</span>
          <span className="text-sm font-medium text-gray-900">
            {quote.parts.reduce((sum, part) => sum + (part.quantity || 0), 0)}
          </span>
        </div>
        
        <div className="border-t border-gray-200 pt-4">
          <div className="flex justify-between items-center">
            <span className="text-lg font-semibold text-gray-900">Total Price:</span>
            <span className="text-2xl font-bold text-green-600">
              <RollingNumber
                value={currentTotal}
                isAnimating={isAnimatingTotal}
                prefix="$"
                decimals={2}
              />
            </span>
          </div>
        </div>
      </div>
      
      <div className="mt-6 space-y-3">
        <Button
          onClick={onCheckout}
          disabled={isCheckingOut || isRedirecting}
          className="w-full"
          size="lg"
        >
          {isRedirecting ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Redirecting to Checkout...</span>
            </div>
          ) : isCheckingOut ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Creating Cart...</span>
            </div>
          ) : (
            'Proceed to Checkout'
          )}
        </Button>
        
        <Button
          onClick={onDownload}
          variant="secondary"
          className="w-full"
          size="lg"
        >
          <div className="flex items-center justify-center space-x-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>Download Original File</span>
          </div>
        </Button>
      </div>
    </div>
  );
};

export default QuoteSummary;
