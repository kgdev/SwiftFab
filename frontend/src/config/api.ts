// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Quote endpoints
  CREATE_QUOTE: `${API_BASE_URL}/api/createQuote`,
  GET_QUOTES: `${API_BASE_URL}/api/quotes`,
  GET_QUOTE_DETAILS: (id: string) => `${API_BASE_URL}/api/quoteDetails/${id}`,
  
  // Part endpoints
  UPDATE_PART: (id: string) => `${API_BASE_URL}/api/updatePart/${id}`,
  
  // Material endpoints
  GET_MATERIALS: `${API_BASE_URL}/api/materials`,
  
  // File endpoints
  DOWNLOAD_FILE: (id: string) => `${API_BASE_URL}/api/downloadFile/${id}`,
  
  // Checkout endpoints
  CHECKOUT: (id: string) => `${API_BASE_URL}/api/checkout/${id}`,
} as const;

export default API_ENDPOINTS;
