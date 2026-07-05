import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import Layout from '../components/common/Layout';
import { 
  User, 
  Mail, 
  Lock, 
  ShieldCheck, 
  Activity, 
  AlertTriangle,
  FileText,
  CheckCircle,
  AlertCircle,
  Sparkles
} from 'lucide-react';

const ProfilePage = () => {
  const { user, setUser } = useAuth();
  
  // Tab control
  const [activeTab, setActiveTab] = useState('info'); // 'info' or 'password'
  
  // Profile info state
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [infoError, setInfoError] = useState('');
  const [infoSuccess, setInfoSuccess] = useState('');
  const [isUpdatingInfo, setIsUpdatingInfo] = useState(false);

  // Password state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passError, setPassError] = useState('');
  const [passSuccess, setPassSuccess] = useState('');
  const [isUpdatingPass, setIsUpdatingPass] = useState(false);

  // Account stats state (fetched from dashboard endpoint)
  const [stats, setStats] = useState(null);

  useEffect(() => {
    if (user) {
      setFullName(user.full_name);
      setEmail(user.email);
    }
  }, [user]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/api/dashboard');
        setStats(response.data);
      } catch (err) {
        console.error('Failed to fetch user stats on profile page:', err);
      }
    };
    fetchStats();
  }, []);

  const handleUpdateInfo = async (e) => {
    e.preventDefault();
    setInfoError('');
    setInfoSuccess('');
    setIsUpdatingInfo(true);

    try {
      const response = await api.put('/api/profile', {
        full_name: fullName,
        email,
      });
      setUser(response.data);
      localStorage.setItem('user', JSON.stringify(response.data));
      setInfoSuccess('Profile details updated successfully.');
    } catch (err) {
      console.error(err);
      setInfoError(
        err.response?.data?.error?.message || 
        'Failed to update profile details. Please try again.'
      );
    } finally {
      setIsUpdatingInfo(false);
    }
  };

  const handleUpdatePassword = async (e) => {
    e.preventDefault();
    setPassError('');
    setPassSuccess('');

    if (newPassword !== confirmPassword) {
      setPassError('New passwords do not match.');
      return;
    }

    setIsUpdatingPass(true);

    try {
      await api.post('/api/profile/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });
      setPassSuccess('Password updated successfully.');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      console.error(err);
      setPassError(
        err.response?.data?.error?.message || 
        'Failed to change password. Please check your current password.'
      );
    } finally {
      setIsUpdatingPass(false);
    }
  };

  return (
    <Layout>
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45 }}
        className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start max-w-5xl mx-auto"
      >
        {/* Left Side - Edit forms */}
        <div className="xl:col-span-8 space-y-6">
          {/* Tab selectors */}
          <div className="flex border-b border-slate-200 dark:border-slate-800">
            <button
              onClick={() => setActiveTab('info')}
              className={`pb-4 px-6 text-sm font-bold border-b-2 transition-all relative cursor-pointer ${
                activeTab === 'info'
                  ? 'text-indigo-650 dark:text-indigo-400 border-indigo-600 dark:border-indigo-400'
                  : 'border-transparent text-slate-400 hover:text-slate-655'
              }`}
            >
              Profile Information
            </button>
            <button
              onClick={() => setActiveTab('password')}
              className={`pb-4 px-6 text-sm font-bold border-b-2 transition-all relative cursor-pointer ${
                activeTab === 'password'
                  ? 'text-indigo-650 dark:text-indigo-400 border-indigo-600 dark:border-indigo-400'
                  : 'border-transparent text-slate-400 hover:text-slate-655'
              }`}
            >
              Change Password
            </button>
          </div>

          {/* Tab 1: Profile Information Panel */}
          <AnimatePresence mode="wait">
            {activeTab === 'info' ? (
              <motion.div
                key="info"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                transition={{ duration: 0.25 }}
                className="rounded-2xl bg-white dark:bg-slate-900 p-8 shadow-sm border border-slate-200/80 dark:border-slate-800/80 transition-colors duration-300"
              >
                <h3 className="text-lg font-bold text-slate-850 dark:text-slate-100 mb-6">Profile Settings</h3>
                
                <AnimatePresence>
                  {infoError && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="mb-4 flex items-start gap-2 rounded-2xl bg-red-50 dark:bg-red-950/20 p-3.5 text-xs font-semibold text-red-650 dark:text-red-400 border border-red-105 dark:border-red-900/40"
                    >
                      <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                      <span>{infoError}</span>
                    </motion.div>
                  )}
                  {infoSuccess && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="mb-4 flex items-start gap-2 rounded-2xl bg-emerald-50 dark:bg-emerald-950/20 p-3.5 text-xs font-semibold text-emerald-650 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-900/40"
                    >
                      <CheckCircle className="h-4 w-4 shrink-0 mt-0.5" />
                      <span>{infoSuccess}</span>
                    </motion.div>
                  )}
                </AnimatePresence>

                <form onSubmit={handleUpdateInfo} className="space-y-6 max-w-lg">
                  <div>
                    <label htmlFor="fullName" className="block text-xs font-bold text-slate-450 dark:text-slate-500 uppercase tracking-wider mb-1.5">
                      Full Name
                    </label>
                    <div className="relative">
                      <input
                        id="fullName"
                        type="text"
                        required
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        placeholder="Enter your name"
                        className="w-full rounded-2xl border border-slate-205 dark:border-slate-800 py-3.5 pl-11 pr-5 text-sm text-slate-800 dark:text-slate-200 bg-white dark:bg-slate-900/60 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-600 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
                      />
                      <User className="absolute left-4 top-3.5 h-4.5 w-4.5 text-slate-400 dark:text-slate-600" />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="email" className="block text-xs font-bold text-slate-450 dark:text-slate-500 uppercase tracking-wider mb-1.5">
                      Email Address
                    </label>
                    <div className="relative">
                      <input
                        id="email"
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Enter your email"
                        className="w-full rounded-2xl border border-slate-205 dark:border-slate-800 py-3.5 pl-11 pr-5 text-sm text-slate-805 dark:text-slate-200 bg-white dark:bg-slate-900/60 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-600 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
                      />
                      <Mail className="absolute left-4 top-3.5 h-4.5 w-4.5 text-slate-400 dark:text-slate-600" />
                    </div>
                  </div>

                  <motion.button
                    type="submit"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    disabled={isUpdatingInfo}
                    className="rounded-2xl bg-indigo-650 hover:bg-indigo-700 text-white font-bold text-sm px-6 py-3.5 shadow-lg shadow-indigo-600/10 dark:shadow-none transition-colors disabled:opacity-60 cursor-pointer"
                  >
                    {isUpdatingInfo ? 'Updating...' : 'Update Profile'}
                  </motion.button>
                </form>
              </motion.div>
            ) : (
              <motion.div
                key="password"
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.25 }}
                className="rounded-2xl bg-white dark:bg-slate-900 p-8 shadow-sm border border-slate-200/80 dark:border-slate-800/80 transition-colors duration-300"
              >
                <h3 className="text-lg font-bold text-slate-850 dark:text-slate-100 mb-6">Security Settings</h3>
                
                <AnimatePresence>
                  {passError && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="mb-4 flex items-start gap-2 rounded-2xl bg-red-50 dark:bg-red-955/20 p-3.5 text-xs font-semibold text-red-650 dark:text-red-400 border border-red-105 dark:border-red-900/40"
                    >
                      <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                      <span>{passError}</span>
                    </motion.div>
                  )}
                  {passSuccess && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="mb-4 flex items-start gap-2 rounded-2xl bg-emerald-50 dark:bg-emerald-950/20 p-3.5 text-xs font-semibold text-emerald-650 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-900/40"
                    >
                      <CheckCircle className="h-4 w-4 shrink-0 mt-0.5" />
                      <span>{passSuccess}</span>
                    </motion.div>
                  )}
                </AnimatePresence>

                <form onSubmit={handleUpdatePassword} className="space-y-6 max-w-lg">
                  <div>
                    <label htmlFor="currentPass" className="block text-xs font-bold text-slate-450 dark:text-slate-500 uppercase tracking-wider mb-1.5">
                      Current Password
                    </label>
                    <div className="relative">
                      <input
                        id="currentPass"
                        type="password"
                        required
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        placeholder="Enter current password"
                        className="w-full rounded-2xl border border-slate-205 dark:border-slate-800 py-3.5 pl-11 pr-5 text-sm text-slate-800 dark:text-slate-200 bg-white dark:bg-slate-900/60 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-600 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
                      />
                      <Lock className="absolute left-4 top-3.5 h-4.5 w-4.5 text-slate-400 dark:text-slate-600" />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="newPass" className="block text-xs font-bold text-slate-450 dark:text-slate-500 uppercase tracking-wider mb-1.5">
                      New Password
                    </label>
                    <div className="relative">
                      <input
                        id="newPass"
                        type="password"
                        required
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        placeholder="Enter new password"
                        className="w-full rounded-2xl border border-slate-205 dark:border-slate-800 py-3.5 pl-11 pr-5 text-sm text-slate-800 dark:text-slate-200 bg-white dark:bg-slate-900/60 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-600 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
                      />
                      <Lock className="absolute left-4 top-3.5 h-4.5 w-4.5 text-slate-400 dark:text-slate-600" />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="confirmPass" className="block text-xs font-bold text-slate-450 dark:text-slate-500 uppercase tracking-wider mb-1.5">
                      Confirm New Password
                    </label>
                    <div className="relative">
                      <input
                        id="confirmPass"
                        type="password"
                        required
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="Confirm new password"
                        className="w-full rounded-2xl border border-slate-205 dark:border-slate-800 py-3.5 pl-11 pr-5 text-sm text-slate-800 dark:text-slate-200 bg-white dark:bg-slate-900/60 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-600 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
                      />
                      <Lock className="absolute left-4 top-3.5 h-4.5 w-4.5 text-slate-400 dark:text-slate-600" />
                    </div>
                  </div>

                  <motion.button
                    type="submit"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    disabled={isUpdatingPass}
                    className="rounded-2xl bg-indigo-650 hover:bg-indigo-700 text-white font-bold text-sm px-6 py-3.5 shadow-lg shadow-indigo-600/10 dark:shadow-none transition-colors disabled:opacity-60 cursor-pointer"
                  >
                    {isUpdatingPass ? 'Updating...' : 'Change Password'}
                  </motion.button>
                </form>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Right Side - Account Statistics card */}
        <div className="xl:col-span-4 space-y-6">
          <div className="rounded-2xl bg-white dark:bg-slate-900 p-6 shadow-sm border border-slate-200/80 dark:border-slate-800/80 transition-colors duration-300">
            <div className="flex items-center gap-1.5 text-indigo-605 dark:text-indigo-400 mb-6">
              <Sparkles className="h-4.5 w-4.5" />
              <h3 className="text-base font-bold text-slate-850 dark:text-slate-100">Account Statistics</h3>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between py-2 border-b border-slate-100 dark:border-slate-800/80 last:border-0 text-xs font-semibold">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
                  <Activity className="h-4.5 w-4.5 text-slate-400" />
                  <span>Total Analyses</span>
                </div>
                <span className="font-bold text-slate-800 dark:text-slate-200">{stats?.total_analyses || 0}</span>
              </div>

              <div className="flex items-center justify-between py-2 border-b border-slate-100 dark:border-slate-800/80 last:border-0 text-xs font-semibold">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
                  <FileText className="h-4.5 w-4.5 text-slate-400" />
                  <span>Reports Generated</span>
                </div>
                <span className="font-bold text-slate-800 dark:text-slate-200">{stats?.total_analyses || 0}</span>
              </div>

              <div className="flex items-center justify-between py-2 border-b border-slate-100 dark:border-slate-800/80 last:border-0 text-xs font-semibold">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
                  <AlertTriangle className="h-4.5 w-4.5 text-slate-400" />
                  <span>High-Risk Detected</span>
                </div>
                <span className="font-bold text-slate-800 dark:text-slate-200">{stats?.high_risk_count || 0}</span>
              </div>

              <div className="flex items-center justify-between py-2 border-b border-slate-100 dark:border-slate-800/80 last:border-0 text-xs font-semibold">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
                  <ShieldCheck className="h-4.5 w-4.5 text-slate-400" />
                  <span>Account Status</span>
                </div>
                <span className="inline-flex items-center rounded-full bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/40 px-2.5 py-0.5 text-[10px] font-black uppercase text-emerald-600 dark:text-emerald-400">
                  Active
                </span>
              </div>

              <div className="flex items-center justify-between py-2 border-b border-slate-100 dark:border-slate-800/80 last:border-0 text-xs font-semibold">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
                  <CheckCircle className="h-4.5 w-4.5 text-slate-400" />
                  <span>Member Since</span>
                </div>
                <span className="font-bold text-slate-650 dark:text-slate-350 text-xs">
                  {user?.created_at ? new Date(user.created_at).toLocaleDateString(undefined, {
                    month: 'long',
                    day: 'numeric',
                    year: 'numeric'
                  }) : '—'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </Layout>
  );
};

export default ProfilePage;
