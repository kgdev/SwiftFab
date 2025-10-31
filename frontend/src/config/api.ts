// API Configuration
// For React apps, environment variables must use REACT_APP_ prefix
// In production (Railway), the backend URL should be set via REACT_APP_API_BASE_URL
// In development, it defaults to localhost:8000

const getApiBaseUrl = (): string => {
  // Priority 1: Use REACT_APP_API_BASE_URL if set (build-time env var)
  if (process.env.REACT_APP_API_BASE_URL) {
    return process.env.REACT_APP_API_BASE_URL;
  }
  
  // Priority 2: In production (served by 'serve'), use window.location
  // This allows the frontend to adapt to whatever domain it's hosted on
  if (process.env.NODE_ENV === 'production') {
    // If frontend and backend are on the same domain, use relative URLs
    // Otherwise, you need to set REACT_APP_API_BASE_URL at build time
    return '';  // Empty string means same origin (relative URLs)
  }
  
  // Priority 3: Development default
  return 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

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
