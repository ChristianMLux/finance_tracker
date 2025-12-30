
import { useState, useEffect } from 'react';
import { api, Tool } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

export function useTools() {
  const { token } = useAuth();
  const [tools, setTools] = useState<Tool[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      setLoading(true);
      api.getTools(token)
        .then((data) => {
            // Sort: Saved first, then newest
            const sorted = data.sort((a, b) => {
                if (a.status === 'saved' && b.status !== 'saved') return -1;
                if (a.status !== 'saved' && b.status === 'saved') return 1;
                return b.id - a.id; 
            });
            setTools(sorted);
        })
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [token]);

  return { tools, loading };
}
