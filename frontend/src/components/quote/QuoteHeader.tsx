import React from 'react';
import { useNavigate } from 'react-router-dom';
import { QuoteData } from '../../types';

interface QuoteHeaderProps {
  quote: QuoteData;
}

const QuoteHeader: React.FC<QuoteHeaderProps> = ({ quote }) => {
  const navigate = useNavigate();

  return (
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
              <div className="flex items-baseline gap-4 mt-2">
                <h2 className="text-xl font-semibold text-gray-800">
                  {quote.file_name}
                </h2>
                <p className="text-gray-500 text-sm">
                  Created {new Date(quote.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default QuoteHeader;
