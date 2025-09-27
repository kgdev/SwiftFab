import { useState, useEffect } from 'react';

const SESSION_STORAGE_KEY = 'swiftfab_session_id';

export const useSession = () => {
  const [sessionId, setSessionId] = useState<string>('');

  useEffect(() => {
    // Try to get existing session from localStorage
    let currentSessionId = localStorage.getItem(SESSION_STORAGE_KEY);
    
    if (!currentSessionId) {
      // Generate a new unique session ID
      currentSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem(SESSION_STORAGE_KEY, currentSessionId);
    }
    
    setSessionId(currentSessionId);
  }, []);

  const resetSession = () => {
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem(SESSION_STORAGE_KEY, newSessionId);
    setSessionId(newSessionId);
  };

  return {
    sessionId,
    resetSession
  };
};