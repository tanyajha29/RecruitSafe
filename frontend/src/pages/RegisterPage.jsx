import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AuthLayout from '../components/auth/AuthLayout';
import { PrimaryButton, InputField, Alert } from '../components/common/Primitives';
import { User, Mail, Lock } from 'lucide-react';

const RegisterPage = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { registerUser, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const getPasswordStrength = () => {
    if (!password) return { label: 'Empty', color: 'bg-border', pct: 0 };
    let score = 0;
    if (password.length >= 8) score += 20;
    if (/[A-Z]/.test(password)) score += 20;
    if (/[a-z]/.test(password)) score += 20;
    if (/\d/.test(password)) score += 20;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 20;
    
    if (score <= 40) return { label: 'Weak', color: 'bg-danger', pct: score };
    if (score <= 80) return { label: 'Moderate', color: 'bg-warning', pct: score };
    return { label: 'Strong', color: 'bg-success', pct: score };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Pre-validation matching strict backend rules
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }
    if (!/[A-Z]/.test(password)) {
      setError('Password must contain at least one uppercase letter.');
      return;
    }
    if (!/[a-z]/.test(password)) {
      setError('Password must contain at least one lowercase letter.');
      return;
    }
    if (!/\d/.test(password)) {
      setError('Password must contain at least one number.');
      return;
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      setError('Password must contain at least one special character.');
      return;
    }

    setIsSubmitting(true);

    try {
      await registerUser(fullName, email, password);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail || 
        err.response?.data?.error?.message || 
        err.response?.data?.error?.details?.validation_errors?.[0]?.message ||
        'Registration failed. Please check your inputs.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const pwStrength = getPasswordStrength();

  return (
    <AuthLayout
      title="Create Account"
      subtitle="Start protecting your career searches from recruiter scam loops."
    >
      {error && (
        <Alert variant="danger" onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <form className="space-y-4" onSubmit={handleSubmit}>
        <div className="relative">
          <InputField
            label="Full Name"
            id="fullName"
            type="text"
            required
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="John Doe"
          />
          <User className="absolute right-4 bottom-3.5 h-4 w-4 text-text-secondary/40" />
        </div>

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

        <div className="relative">
          <InputField
            label="Password"
            id="password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
          />
          <Lock className="absolute right-4 bottom-3.5 h-4 w-4 text-text-secondary/40" />
        </div>

        {/* Password Strength Indicator */}
        {password && (
          <div className="space-y-1.5 text-left">
            <div className="flex justify-between text-[10px] font-mono font-bold tracking-wider text-text-secondary">
              <span>PASSWORD STRENGTH</span>
              <span className="uppercase">{pwStrength.label}</span>
            </div>
            <div className="h-1 bg-border rounded-full overflow-hidden">
              <div 
                className={`h-full ${pwStrength.color} transition-all duration-300`} 
                style={{ width: `${pwStrength.pct}%` }} 
              />
            </div>
          </div>
        )}

        <div className="relative">
          <InputField
            label="Confirm Password"
            id="confirmPassword"
            type="password"
            required
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="••••••••"
          />
          <Lock className="absolute right-4 bottom-3.5 h-4 w-4 text-text-secondary/40" />
        </div>

        <PrimaryButton
          type="submit"
          disabled={isSubmitting}
          className="w-full py-3 mt-2"
        >
          {isSubmitting ? 'Creating Account...' : 'Create Account'}
        </PrimaryButton>
      </form>

      <p className="mt-8 text-center text-xs text-text-secondary">
        Already have an account?{' '}
        <Link to="/login" className="font-bold text-brand hover:underline">
          Sign In
        </Link>
      </p>
    </AuthLayout>
  );
};

export default RegisterPage;
