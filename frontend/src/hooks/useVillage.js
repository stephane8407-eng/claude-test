import { useState, useEffect } from 'react';
import { villageAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export function useVillage() {
  const { user } = useAuth();
  const [village, setVillage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (user?.village_slug) {
      loadVillage();
    }
  }, [user]);

  const loadVillage = async () => {
    try {
      const data = await villageAPI.getBySlug(user.village_slug);
      setVillage(data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  const updateVillage = async (updates) => {
    try {
      const updated = await villageAPI.update(user.village_slug, updates);
      setVillage(updated);
      return updated;
    } catch (err) {
      throw err;
    }
  };

  return { village, loading, error, updateVillage, refresh: loadVillage };
}
