import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSession } from '../hooks/useSession';
import Header from '../components/ui/Header';
import Card from '../components/ui/Card';
import FileUpload from '../components/ui/FileUpload';
import Button from '../components/ui/Button';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import API_ENDPOINTS from '../config/api';

interface QuoteData {
  id: string;
  file_name: string;
  created_at: string;
  total_price: number;
}

const Home: React.FC = () => {
  const navigate = useNavigate();
  const { sessionId } = useSession();
  const [isUploading, setIsUploading] = useState(false);
  const [showQuotes, setShowQuotes] = useState(false);
  const [quotes, setQuotes] = useState<QuoteData[]>([]);
  const [loadingQuotes, setLoadingQuotes] = useState(false);

  const handleFileUpload = async (file: File) => {
    if (!file) return;
    
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('session_id', sessionId);
      
      const response = await fetch(API_ENDPOINTS.CREATE_QUOTE, {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
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
      const response = await fetch(API_ENDPOINTS.GET_QUOTES, {
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

  const handleViewQuotes = () => {
    setShowQuotes(!showQuotes);
    if (!showQuotes) {
      loadAllQuotes();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100">
      <Header onViewQuotes={handleViewQuotes} showQuotes={showQuotes} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        <Card
          title="Upload STEP File"
          icon={
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          }
        >
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-4">
                Select STEP File (.step or .stp)
              </label>
              <FileUpload
                onFileSelect={handleFileUpload}
                isUploading={isUploading}
                accept=".step,.stp"
                maxSize={25}
              />
            </div>
          </div>
        </Card>

        {showQuotes && (
          <Card
            title="My Quotes"
            icon={
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            }
          >
            {loadingQuotes ? (
              <LoadingSpinner size="lg" text="Loading quotes..." />
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
                        <td className="py-4 px-4 text-sm font-bold text-green-600">
                          ${(quote.total_price || 0).toFixed(2)}
                        </td>
                        <td className="py-4 px-4">
                          <Button
                            onClick={() => navigate(`/quote/${quote.id}`)}
                            size="sm"
                          >
                            View Quote
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        )}
      </main>
    </div>
  );
};

export default Home;

