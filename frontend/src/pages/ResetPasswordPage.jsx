import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import authService from '../services/authService';
import { ShieldCheck, Lock, AlertCircle, CheckCircle2 } from 'lucide-react';

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
    <div className="flex min-h-screen items-center justify-center bg-[#F8FAFC] px-4 py-12 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: 'easeOut' }}
        className="w-full max-w-md"
      >
        {/* Brand Header */}
        <div className="flex flex-col items-center mb-8">
          <div className="flex items-center gap-2 text-brand-600 font-bold text-3xl">
            <ShieldCheck className="h-8 w-8 stroke-[2.5]" />
            <span>RecruitSafe</span>
          </div>
          <p className="mt-2 text-sm text-slate-500">AI-Powered Job Scam Detection</p>
        </div>

        {/* Reset Card */}
        <div className="rounded-2xl bg-white p-8 shadow-xl shadow-slate-100 border border-slate-100">
          <h2 className="text-2xl font-bold text-slate-800 text-center mb-1">Reset Password</h2>
          <p className="text-sm text-slate-500 text-center mb-6 font-medium">Create a new password for your account</p>

          {success ? (
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="text-center py-6"
            >
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-emerald-50 text-emerald-600 mb-4 border border-emerald-100">
                <CheckCircle2 className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-800 mb-2">Password Updated!</h3>
              <p className="text-sm text-slate-500 max-w-xs mx-auto mb-6 leading-relaxed">
                Your new password has been successfully configured. You can now use it to log into the platform.
              </p>
              <Link
                to="/login"
                className="w-full inline-flex justify-center rounded-lg bg-brand-500 py-2.5 text-sm font-bold text-white shadow-lg shadow-brand-500/20 outline-none transition-all hover:bg-brand-600 focus:ring-2 focus:ring-brand-500/40 cursor-pointer"
              >
                Log In Now
              </Link>
            </motion.div>
          ) : (
            <>
              {error && (
                <motion.div
                  initial={{ scale: 0.95, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="mb-4 flex items-start gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-600 border border-red-100"
                >
                  <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                  <span>{error}</span>
                </motion.div>
              )}

              <form className="space-y-4" onSubmit={handleSubmit}>
                <div>
                  <label htmlFor="newPassword" className="block text-sm font-semibold text-slate-700 mb-1">
                    New Password
                  </label>
                  <div className="relative">
                    <input
                      id="newPassword"
                      type="password"
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter new password"
                      className="w-full rounded-lg border border-slate-200 py-2.5 pl-10 pr-4 text-sm text-slate-800 outline-none transition-all placeholder:text-slate-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/10"
                    />
                    <Lock className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" />
                  </div>
                  <p className="mt-1 text-[10px] text-slate-400 leading-normal">
                    Must be at least 8 characters with 1 uppercase, 1 lowercase, 1 digit, and 1 special symbol.
                  </p>
                </div>

                <div>
                  <label htmlFor="confirmPassword" className="block text-sm font-semibold text-slate-700 mb-1">
                    Confirm New Password
                  </label>
                  <div className="relative">
                    <input
                      id="confirmPassword"
                      type="password"
                      required
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Confirm new password"
                      className="w-full rounded-lg border border-slate-200 py-2.5 pl-10 pr-4 text-sm text-slate-800 outline-none transition-all placeholder:text-slate-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/10"
                    />
                    <Lock className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting || !token}
                  className="w-full rounded-lg bg-brand-500 py-2.5 text-sm font-bold text-white shadow-lg shadow-brand-500/20 outline-none transition-all hover:bg-brand-600 focus:ring-2 focus:ring-brand-500/40 disabled:opacity-60 cursor-pointer mt-2"
                >
                  {isSubmitting ? 'Resetting Password...' : 'Reset Password'}
                </button>
              </form>

              <div className="mt-6 text-center">
                <Link
                  to="/login"
                  className="text-xs font-bold text-slate-500 hover:text-brand-600 transition-colors"
                >
                  Return to Login
                </Link>
              </div>
            </>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default ResetPasswordPage;
