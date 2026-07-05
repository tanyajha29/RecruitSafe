import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import authService from '../services/authService';
import { ShieldCheck, Mail, ArrowLeft, CheckCircle2, AlertCircle } from 'lucide-react';

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

        {/* Card */}
        <div className="rounded-2xl bg-white p-8 shadow-xl shadow-slate-100 border border-slate-100 relative overflow-hidden">
          <h2 className="text-2xl font-bold text-slate-800 text-center mb-1">Forgot Password</h2>
          <p className="text-sm text-slate-500 text-center mb-6">
            Enter your email and we'll send you a reset link
          </p>

          {success ? (
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="text-center py-6"
            >
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-emerald-50 text-emerald-600 mb-4 border border-emerald-100">
                <CheckCircle2 className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-800 mb-2">Reset Link Sent!</h3>
              <p className="text-sm text-slate-500 max-w-xs mx-auto mb-6 leading-relaxed">
                If an account exists for <span className="font-semibold text-slate-700">{email}</span>, we have dispatched instructions to reset your password. 
                <br />
                <span className="text-xs text-brand-500 font-medium italic mt-2 block">
                  (Developer mode: check server console for reset URL link)
                </span>
              </p>
              <Link
                to="/login"
                className="inline-flex items-center gap-2 text-sm font-bold text-brand-600 hover:text-brand-500 transition-colors cursor-pointer"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Return to Login</span>
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
                  <label htmlFor="email" className="block text-sm font-semibold text-slate-700 mb-1">
                    Email Address
                  </label>
                  <div className="relative">
                    <input
                      id="email"
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter your registered email"
                      className="w-full rounded-lg border border-slate-200 py-2.5 pl-10 pr-4 text-sm text-slate-800 outline-none transition-all placeholder:text-slate-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/10"
                    />
                    <Mail className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full rounded-lg bg-brand-500 py-2.5 text-sm font-bold text-white shadow-lg shadow-brand-500/20 outline-none transition-all hover:bg-brand-600 focus:ring-2 focus:ring-brand-500/40 disabled:opacity-60 cursor-pointer"
                >
                  {isSubmitting ? 'Sending Link...' : 'Send Reset Link'}
                </button>
              </form>

              <div className="mt-6 text-center">
                <Link
                  to="/login"
                  className="text-xs font-bold text-slate-500 hover:text-brand-600 transition-colors"
                >
                  Remember your password? Login
                </Link>
              </div>
            </>
          )}

          {/* Visual Envelope graphics matching the locked UI Page 1 Far Right */}
          <div className="mt-8 flex justify-center">
            <svg
              className="h-32 w-full text-brand-300"
              viewBox="0 0 200 120"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              {/* Paper airplane */}
              <motion.path
                initial={{ x: -10, y: 10, opacity: 0 }}
                animate={{ x: 10, y: -10, opacity: 1 }}
                transition={{ duration: 2, repeat: Infinity, repeatType: "reverse", ease: "easeInOut" }}
                d="M170 15L135 30L150 35L170 15ZM170 15L150 35L155 50L170 15Z"
                fill="#818CF8"
              />
              <motion.path
                initial={{ x: -10, y: 10, opacity: 0 }}
                animate={{ x: 10, y: -10, opacity: 0.7 }}
                transition={{ duration: 2, repeat: Infinity, repeatType: "reverse", ease: "easeInOut" }}
                d="M170 15L135 30L150 35M150 35L155 50"
                stroke="#4F46E5"
                strokeWidth="0.75"
              />

              {/* Envelope Letter coming out */}
              <rect x="50" y="30" width="100" height="60" rx="4" fill="#EEF2F6" stroke="#C7D2FE" strokeWidth="1" />
              <line x1="60" y1="45" x2="140" y2="45" stroke="#D1D5DB" strokeWidth="2" />
              <line x1="60" y1="58" x2="140" y2="58" stroke="#E5E7EB" strokeWidth="2" />
              <line x1="60" y1="71" x2="110" y2="71" stroke="#E5E7EB" strokeWidth="2" />

              {/* Envelope Body */}
              <path d="M40 50L100 85L160 50V100H40V50Z" fill="#C7D2FE" />
              <path d="M40 50L100 85L160 50" stroke="#818CF8" strokeWidth="2" strokeLinejoin="round" />
              <path d="M40 100L90 75" stroke="#818CF8" strokeWidth="1.5" />
              <path d="M160 100L110 75" stroke="#818CF8" strokeWidth="1.5" />
            </svg>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default ForgotPasswordPage;
