import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSession } from '../hooks/useSession';

interface QuoteData {
  id: string;
  file_name: string;
  created_at: string;
  status: string;
  total_price: number;
}

const Home: React.FC = () => {
  const navigate = useNavigate();
  const { sessionId } = useSession();
  const [isUploading, setIsUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [showQuotes, setShowQuotes] = useState(false);
  const [quotes, setQuotes] = useState<QuoteData[]>([]);
  const [loadingQuotes, setLoadingQuotes] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (file: File) => {
    if (!file) return;
    
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('session_id', sessionId);
      
      // Call backend API
      const response = await fetch('http://localhost:8000/api/createQuote', {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          // Navigate to quote page
          navigate(`/quote/${result.quote_id}`);
        }
      }
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const loadAllQuotes = async () => {
    setLoadingQuotes(true);
    try {
      const response = await fetch(`http://localhost:8000/api/quotes`, {
        headers: {
          'X-Session-ID': sessionId
        }
      });
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setQuotes(data.quotes);
        }
      }
    } catch (error) {
      console.error('Load quotes error:', error);
    } finally {
      setLoadingQuotes(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    const stepFile = files.find(file => 
      file.name.toLowerCase().endsWith('.step') || 
      file.name.toLowerCase().endsWith('.stp')
    );
    
    if (stepFile) {
      handleFileUpload(stepFile);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleViewQuotes = () => {
    setShowQuotes(!showQuotes);
    if (!showQuotes) {
      loadAllQuotes();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md shadow-lg border-b border-white/20 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl flex items-center justify-center mr-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  SwiftFab Quote System
                </h1>
                <p className="text-gray-500 text-sm mt-1">Upload your STEP files for instant quotes</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button 
                onClick={handleViewQuotes}
                className="bg-white/60 hover:bg-white/80 text-gray-700 font-medium py-2 px-4 rounded-xl transition-all duration-200 border border-gray-200/50 shadow-sm hover:shadow-md flex items-center space-x-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <span>{showQuotes ? 'Hide My Quotes' : 'View My Quotes'}</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* File Upload Section */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8">
          <div className="flex items-center mb-6">
            <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl flex items-center justify-center mr-4">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Upload STEP File</h2>
          </div>
          
          <div className="space-y-6">
            {/* File Upload */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-4">
                Select STEP File (.step or .stp)
              </label>
              <label 
                htmlFor="file-upload"
                className={`relative flex justify-center px-8 pt-12 pb-12 border-2 border-dashed rounded-2xl transition-all duration-300 cursor-pointer group ${
                  dragOver 
                    ? 'border-purple-500 bg-purple-50/50' 
                    : 'border-gray-300 hover:border-purple-400 hover:bg-purple-50/30'
                }`}
                onDrop={handleDrop}
                onDragOver={(e) => {
                  e.preventDefault();
                  setDragOver(true);
                }}
                onDragLeave={() => setDragOver(false)}
              >
                <div className="space-y-1 text-center">
                  <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  <div className="flex text-sm text-gray-600">
                    <span className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500">
                      Upload a file
                    </span>
                    <p className="pl-1">or drag and drop</p>
                  </div>
                  <p className="text-xs text-gray-500">
                    STEP, STP up to 25MB
                  </p>
                </div>
                <input 
                  id="file-upload" 
                  name="file-upload" 
                  type="file" 
                  className="sr-only" 
                  accept=".step,.stp"
                  onChange={handleFileSelect}
                  ref={fileInputRef}
                />
              </label>
              
              {isUploading && (
                <div className="mt-4 text-center">
                  <div className="loading"></div>
                  <p className="text-sm text-gray-600">Processing file...</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* My Quotes Section */}
        {showQuotes && (
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8">
            <div className="flex items-center mb-6">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center mr-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900">My Quotes</h2>
            </div>
            
            {loadingQuotes ? (
              <div className="text-center py-12">
                <div className="loading mx-auto mb-4"></div>
                <p className="text-gray-600 text-lg">Loading quotes...</p>
              </div>
            ) : quotes.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <p className="text-gray-600 text-lg">No quotes found. Upload a STEP file to create your first quote.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-4 px-4 font-semibold text-gray-700">Quote ID</th>
                      <th className="text-left py-4 px-4 font-semibold text-gray-700">File Name</th>
                      <th className="text-left py-4 px-4 font-semibold text-gray-700">Created</th>
                      <th className="text-left py-4 px-4 font-semibold text-gray-700">Status</th>
                      <th className="text-left py-4 px-4 font-semibold text-gray-700">Total Price</th>
                      <th className="text-left py-4 px-4 font-semibold text-gray-700">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {quotes.map((quote, index) => (
                      <tr key={quote.id} className={`border-b border-gray-100 hover:bg-gray-50/50 transition-colors duration-200 ${index % 2 === 0 ? 'bg-white/30' : 'bg-white/10'}`}>
                        <td className="py-4 px-4">
                          <div className="font-medium text-gray-900">{quote.id}</div>
                        </td>
                        <td className="py-4 px-4 text-sm text-gray-600">
                          {quote.file_name}
                        </td>
                        <td className="py-4 px-4 text-sm text-gray-600">
                          {new Date(quote.created_at).toLocaleDateString()}
                        </td>
                        <td className="py-4 px-4">
                          <span className="inline-flex px-3 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                            {quote.status}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-sm font-bold text-green-600">
                          ${(quote.total_price || 0).toFixed(2)}
                        </td>
                        <td className="py-4 px-4">
                          <button
                            onClick={() => navigate(`/quote/${quote.id}`)}
                            className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-all duration-200 transform hover:scale-105 shadow-sm"
                          >
                            View Quote
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default Home;

