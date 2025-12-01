import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      // Handle different error formats from FastAPI
      const errorData = err.response?.data;
      let errorMessage = 'Connexion échouée';

      if (errorData) {
        if (typeof errorData.detail === 'string') {
          // Standard error message
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          // 422 validation error - extract first message
          errorMessage = errorData.detail[0]?.msg || 'Erreur de validation';
        } else if (typeof errorData.detail === 'object') {
          // Object error - extract msg field
          errorMessage = errorData.detail.msg || 'Erreur de connexion';
        }
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <h2 className="text-3xl font-bold text-center">Village Partner Login</h2>

        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full text-white py-2 px-4 rounded-md disabled:opacity-50"
            style={{ backgroundColor: loading ? '#006666' : 'var(--color-primary, #008080)' }}
            onMouseOver={(e) => !loading && (e.target.style.backgroundColor = '#006666')}
            onMouseOut={(e) => !loading && (e.target.style.backgroundColor = 'var(--color-primary, #008080)')}
          >
            {loading ? 'Connexion...' : 'Se connecter'}
          </button>
        </form>
      </div>
    </div>
  );
}
