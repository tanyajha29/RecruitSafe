import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import authService from '../services/authService';
import AuthLayout from '../components/auth/AuthLayout';
import { PrimaryButton, InputField, Alert } from '../components/common/Primitives';
import { Mail, CheckCircle2 } from 'lucide-react';

const ForgotPasswordPage = () => {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      await authService.requestPasswordReset(email);
      setSuccess(true);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.error?.message || 
        'Could not initiate password reset. Please verify your email and try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthLayout
      title="Forgot Password"
      subtitle="Enter your email to receive a secure recovery URL link."
    >
      {success ? (
        <div className="text-center py-6 space-y-4">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-success/10 text-success border border-success/20">
            <CheckCircle2 className="h-6 w-6" />
          </div>
          <h3 className="text-lg font-bold text-text-primary">Reset Link Sent</h3>
          <p className="text-sm text-text-secondary leading-relaxed max-w-xs mx-auto">
            If an account exists for <span className="font-semibold text-text-primary">{email}</span>, we have dispatched instructions to reset your password.
            <span className="text-xs text-brand font-medium italic mt-2 block font-mono">
              (Check server terminal log for your local recovery link)
            </span>
          </p>
          <div className="pt-4">
            <Link
              to="/login"
              className="text-xs font-mono font-bold text-brand hover:underline"
            >
              Return to Login
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

            <PrimaryButton
              type="submit"
              disabled={isSubmitting}
              className="w-full py-3"
            >
              {isSubmitting ? 'Sending Link...' : 'Send Reset Link'}
            </PrimaryButton>
          </form>

          <div className="text-center pt-4">
            <Link
              to="/login"
              className="text-xs font-bold text-text-secondary hover:text-brand transition-colors"
            >
              Remembered your password? Login
            </Link>
          </div>
        </>
      )}
    </AuthLayout>
  );
};

export default ForgotPasswordPage;
