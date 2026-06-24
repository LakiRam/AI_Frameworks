import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

function getErrorMessage(error) {
  if (axios.isAxiosError(error)) {
    return error.response?.data?.message || 'Unable to sign in. Check credentials and try again.';
  }

  return error.message || 'Unable to sign in. Check credentials and try again.';
}

export default function LoginPage() {
  const [formState, setFormState] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleChange = (field, value) => {
    setFormState((current) => ({ ...current, [field]: value }));
    setError('');
  };

  const validate = () => {
    if (!formState.username.trim() || !formState.password.trim()) {
      setError('Username and password are required.');
      return false;
    }

    return true;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!validate()) {
      return;
    }

    try {
      setLoading(true);
      await login({
        username: formState.username.trim(),
        password: formState.password,
      });
      const redirectPath = location.state?.from?.pathname || '/';
      navigate(redirectPath, { replace: true });
    } catch (submitError) {
      setError(getErrorMessage(submitError));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-shell">
      <section className="login-card panel">
        <div className="login-intro">
          <span className="hero-badge">Trusted AI workflows</span>
          <h1>Supply Chain Prompt Advisor</h1>
          <p>
            Sign in to generate production-ready prompt recommendations for procurement, logistics,
            forecasting, inventory, and supplier risk workflows.
          </p>
        </div>

        {error ? <div className="banner banner-error">{error}</div> : null}

        <form className="login-form" onSubmit={handleSubmit}>
          <div className="field-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              autoComplete="username"
              value={formState.username}
              onChange={(event) => handleChange('username', event.target.value)}
              placeholder="Enter your username"
            />
          </div>

          <div className="field-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              value={formState.password}
              onChange={(event) => handleChange('password', event.target.value)}
              placeholder="Enter your password"
            />
          </div>

          <button className="primary-button login-button" type="submit" disabled={loading}>
            {loading ? (
              <>
                <span className="button-spinner" aria-hidden="true" />
                Signing in...
              </>
            ) : (
              'Sign in'
            )}
          </button>
        </form>
      </section>
    </main>
  );
}
