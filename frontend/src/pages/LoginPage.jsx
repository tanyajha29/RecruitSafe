import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import AuthLayout from '../components/auth/AuthLayout';
import { PrimaryButton, InputField, Alert } from '../components/common/Primitives';
import { Mail, Lock } from 'lucide-react';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { loginUser, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  // Show a warning if redirected due to expired token
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get('expired')) {
      setError('Your session has expired. Please log in again.');
    }
  }, [location]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      await loginUser(email, password, rememberMe);
      const destination = location.state?.from?.pathname || '/dashboard';
      navigate(destination, { replace: true });
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail || 
        err.response?.data?.error?.message || 
        'Login failed. Please check your credentials and try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthLayout
      title="Welcome Back"
      subtitle="Sign in to your RecruitSafe dashboard to manage scans."
    >
      {error && (
        <Alert variant="danger" onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <form className="space-y-5" onSubmit={handleSubmit}>
        <div className="relative">
          <InputField
            label="Email Address"
            id="email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="name@company.com"
          />
          <Mail className="absolute right-4 bottom-3.5 h-4 w-4 text-text-secondary/40" />
        </div>

        <div className="space-y-1">
          <div className="flex items-center justify-between">
            <label className="font-mono text-[11px] font-bold text-text-secondary uppercase tracking-wider">
              Password
            </label>
            <Link
              to="/forgot-password"
              className="text-xs font-semibold text-brand hover:underline"
            >
              Forgot Password?
            </Link>
          </div>
          <div className="relative">
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="bg-bg border border-border text-text-primary placeholder:text-text-secondary/40 rounded-lg px-4 py-3 focus:outline-none focus:ring-1 focus:ring-brand focus:border-brand transition-all w-full text-[14px]"
            />
            <Lock className="absolute right-4 bottom-3.5 h-4 w-4 text-text-secondary/40" />
          </div>
        </div>

        <div className="flex items-center justify-between py-1">
          <label className="flex items-center gap-2 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              className="h-4 w-4 rounded border-border text-brand focus:ring-brand bg-bg"
            />
            <span className="text-xs text-text-secondary font-medium">Remember me for 30 days</span>
          </label>
        </div>

        <PrimaryButton
          type="submit"
          disabled={isSubmitting}
          className="w-full py-3"
        >
          {isSubmitting ? 'Signing in...' : 'Sign In'}
        </PrimaryButton>
      </form>

      {/* Social login option */}
      <div className="relative my-6 flex items-center justify-center">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-border"></div>
        </div>
        <span className="relative bg-bg px-3 text-[10px] text-text-secondary font-mono uppercase tracking-wider">or</span>
      </div>

      <button
        type="button"
        onClick={() => alert('Social authentication is currently disabled for this release.')}
        className="flex w-full items-center justify-center gap-2 rounded-lg border border-border bg-card hover:bg-bg py-3 text-sm font-bold text-text-primary transition-colors cursor-pointer shadow-sm"
      >
        <svg className="h-5 w-5" viewBox="0 0 24 24">
          <path
            fill="#EA4335"
            d="M12 5.04c1.67 0 3.2.58 4.39 1.71l3.27-3.27C17.68 1.54 15.03 1 12 1 7.24 1 3.22 3.76 1.34 7.78l3.92 3.04C6.18 7.68 8.85 5.04 12 5.04z"
          />
          <path
            fill="#4285F4"
            d="M23.49 12.27c0-.81-.07-1.59-.2-2.36H12v4.51h6.46c-.29 1.48-1.14 2.73-2.42 3.57l3.77 2.92c2.2-2.03 3.68-5.01 3.68-8.64z"
          />
          <path
            fill="#FBBC05"
            d="M5.26 14.82c-.25-.74-.39-1.53-.39-2.35s.14-1.61.39-2.35L1.34 7.08C.48 8.78 0 10.66 0 12.62s.48 3.84 1.34 5.54l3.92-3.34z"
          />
          <path
            fill="#34A853"
            d="M12 23c3.24 0 5.97-1.07 7.96-2.91l-3.77-2.92c-1.08.73-2.47 1.17-4.19 1.17-3.15 0-5.82-2.64-6.74-5.78L1.34 15.9C3.22 19.92 7.24 23 12 23z"
          />
        </svg>
        <span className="font-mono text-xs">Continue with Google</span>
      </button>

      <p className="mt-8 text-center text-xs text-text-secondary">
        New to RecruitSafe?{' '}
        <Link to="/register" className="font-bold text-brand hover:underline">
          Create an account
        </Link>
      </p>
    </AuthLayout>
  );
};

export default LoginPage;
