import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import authService from '../services/authService';
import AuthLayout from '../components/auth/AuthLayout';
import { PrimaryButton, InputField, Alert } from '../components/common/Primitives';
import { Lock, CheckCircle2 } from 'lucide-react';

const ResetPasswordPage = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const navigate = useNavigate();

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!token) {
      setError('Invalid reset link: token is missing.');
    }
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!token) {
      setError('Cannot submit: reset token is missing from the URL.');
      return;
    }

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
      await authService.confirmPasswordReset(token, password);
      setSuccess(true);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.error?.message || 
        'Reset failed. The token may be expired or already used.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthLayout
      title="Reset Password"
      subtitle="Enter a new secure password for your RecruitSafe account."
    >
      {success ? (
        <div className="text-center py-6 space-y-4">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-success/10 text-success border border-success/20">
            <CheckCircle2 className="h-6 w-6" />
          </div>
          <h3 className="text-lg font-bold text-text-primary">Password Updated</h3>
          <p className="text-sm text-text-secondary leading-relaxed max-w-xs mx-auto">
            Your new password has been successfully configured. You can now use it to log into the platform.
          </p>
          <div className="pt-4">
            <Link
              to="/login"
              className="inline-flex justify-center w-full bg-brand hover:bg-[#754f32] text-white font-mono text-[13px] font-bold rounded-lg px-5 py-3 shadow-sm"
            >
              Log In Now
            </Link>
          </div>
        </div>
      ) : (
        <>
          {error && (
            <Alert variant="danger" onClose={() => setError('')}>
              {error}
            </Alert>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="relative">
              <InputField
                label="New Password"
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
              />
              <Lock className="absolute right-4 bottom-3.5 h-4 w-4 text-text-secondary/40" />
            </div>

            <div className="relative">
              <InputField
                label="Confirm New Password"
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
              disabled={isSubmitting || !token}
              className="w-full py-3 mt-2"
            >
              {isSubmitting ? 'Resetting Password...' : 'Reset Password'}
            </PrimaryButton>
          </form>

          <div className="text-center pt-4">
            <Link
              to="/login"
              className="text-xs font-bold text-text-secondary hover:text-brand transition-colors"
            >
              Return to Login
            </Link>
          </div>
        </>
      )}
    </AuthLayout>
  );
};

export default ResetPasswordPage;
