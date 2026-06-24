import { useEffect, useState } from 'react';
import axios from 'axios';
import NavBar from '../components/NavBar';
import ResultsPanel from '../components/ResultsPanel';
import ScenarioForm from '../components/ScenarioForm';
import { useAuth } from '../context/AuthContext';
import { getProviders, getRecommendations } from '../services/recommendationService';

function getErrorMessage(error) {
  if (axios.isAxiosError(error)) {
    return error.response?.data?.message || 'Request failed. Please verify provider settings and try again.';
  }

  return error.message || 'Request failed. Please verify provider settings and try again.';
}

export default function HomePage() {
  const { user, logout } = useAuth();
  const [providers, setProviders] = useState([]);
  const [providersError, setProvidersError] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [activeDomain, setActiveDomain] = useState('procurement');
  const [loading, setLoading] = useState(false);
  const [loadingProviders, setLoadingProviders] = useState(true);
  const [resultError, setResultError] = useState('');

  useEffect(() => {
    let isMounted = true;

    const loadProviders = async () => {
      try {
        setLoadingProviders(true);
        const response = await getProviders();

        if (isMounted) {
          setProviders(response);
          setProvidersError('');
        }
      } catch (error) {
        if (isMounted) {
          setProvidersError('Provider catalog unavailable. Using built-in defaults.');
        }
      } finally {
        if (isMounted) {
          setLoadingProviders(false);
        }
      }
    };

    loadProviders();

    return () => {
      isMounted = false;
    };
  }, []);

  const handleLogout = () => {
    setProviders([]);
    setRecommendations([]);
    setActiveDomain('procurement');
    setProvidersError('');
    setResultError('');
    logout();
  };

  const handleSubmit = async (payload) => {
    try {
      setLoading(true);
      setResultError('');
      setActiveDomain(payload.domain);
      const nextRecommendations = await getRecommendations(payload);
      setRecommendations(nextRecommendations);
    } catch (error) {
      setRecommendations([]);
      setResultError(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <NavBar user={user} onLogout={handleLogout} />

      <main className="app-content">
        {providersError ? <div className="banner banner-warning">{providersError}</div> : null}

        <div className="content-grid">
          <ScenarioForm providers={providers} onSubmit={handleSubmit} loading={loading || loadingProviders} />
          <ResultsPanel
            loading={loading}
            recommendations={recommendations}
            error={resultError}
            domain={activeDomain}
          />
        </div>
      </main>
    </div>
  );
}
