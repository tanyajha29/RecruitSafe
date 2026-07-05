import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
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
  AlertCircle
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
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start"
      >
        {/* Left Side - Edit forms */}
        <div className="xl:col-span-8 space-y-6">
          {/* Tab selectors */}
          <div className="flex border-b border-slate-200">
            <button
              onClick={() => setActiveTab('info')}
              className={`pb-4 px-6 text-sm font-bold border-b-2 transition-all cursor-pointer ${
                activeTab === 'info'
                  ? 'border-brand-500 text-brand-600'
                  : 'border-transparent text-slate-400 hover:text-slate-600'
              }`}
            >
              Profile Information
            </button>
            <button
              onClick={() => setActiveTab('password')}
              className={`pb-4 px-6 text-sm font-bold border-b-2 transition-all cursor-pointer ${
                activeTab === 'password'
                  ? 'border-brand-500 text-brand-600'
                  : 'border-transparent text-slate-400 hover:text-slate-600'
              }`}
            >
              Change Password
            </button>
          </div>

          {/* Tab 1: Profile Information Panel */}
          {activeTab === 'info' && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="rounded-2xl bg-white p-8 shadow-sm border border-slate-200/80"
            >
              <h3 className="text-lg font-bold text-slate-800 mb-6">Profile Settings</h3>
              
              {infoError && (
                <div className="mb-4 flex items-start gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-600 border border-red-100">
                  <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                  <span>{infoError}</span>
                </div>
              )}
              {infoSuccess && (
                <div className="mb-4 flex items-start gap-2 rounded-lg bg-emerald-50 p-3 text-sm text-emerald-600 border border-emerald-100">
                  <CheckCircle className="h-4 w-4 shrink-0 mt-0.5" />
                  <span>{infoSuccess}</span>
                </div>
              )}

              <form onSubmit={handleUpdateInfo} className="space-y-6 max-w-lg">
                <div>
                  <label htmlFor="fullName" className="block text-sm font-semibold text-slate-700 mb-1">
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
                      className="w-full rounded-lg border border-slate-200 py-2.5 pl-10 pr-4 text-sm text-slate-800 outline-none transition-all placeholder:text-slate-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/10"
                    />
                    <User className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" />
                  </div>
                </div>

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
                      placeholder="Enter your email"
                      className="w-full rounded-lg border border-slate-200 py-2.5 pl-10 pr-4 text-sm text-slate-800 outline-none transition-all placeholder:text-slate-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/10"
                    />
                    <Mail className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isUpdatingInfo}
                  className="rounded-lg bg-brand-500 px-6 py-2.5 text-sm font-bold text-white shadow-md shadow-brand-500/10 hover:bg-brand-600 transition-colors disabled:opacity-60 cursor-pointer"
                >
                  {isUpdatingInfo ? 'Updating...' : 'Update Profile'}
                </button>
              </form>
            </motion.div>
          )}

          {/* Tab 2: Change Password Panel */}
          {activeTab === 'password' && (
            <motion.div
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              className="rounded-2xl bg-white p-8 shadow-sm border border-slate-200/80"
            >
              <h3 className="text-lg font-bold text-slate-800 mb-6">Security Settings</h3>
              
              {passError && (
                <div className="mb-4 flex items-start gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-600 border border-red-100">
                  <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                  <span>{passError}</span>
                </div>
              )}
              {passSuccess && (
                <div className="mb-4 flex items-start gap-2 rounded-lg bg-emerald-50 p-3 text-sm text-emerald-600 border border-emerald-100">
                  <CheckCircle className="h-4 w-4 shrink-0 mt-0.5" />
                  <span>{passSuccess}</span>
                </div>
              )}

              <form onSubmit={handleUpdatePassword} className="space-y-6 max-w-lg">
                <div>
                  <label htmlFor="currentPass" className="block text-sm font-semibold text-slate-700 mb-1">
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
                      className="w-full rounded-lg border border-slate-200 py-2.5 pl-10 pr-4 text-sm text-slate-800 outline-none transition-all placeholder:text-slate-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/10"
                    />
                    <Lock className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" />
                  </div>
                </div>

                <div>
                  <label htmlFor="newPass" className="block text-sm font-semibold text-slate-700 mb-1">
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
                      className="w-full rounded-lg border border-slate-200 py-2.5 pl-10 pr-4 text-sm text-slate-800 outline-none transition-all placeholder:text-slate-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/10"
                    />
                    <Lock className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" />
                  </div>
                </div>

                <div>
                  <label htmlFor="confirmPass" className="block text-sm font-semibold text-slate-700 mb-1">
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
                      className="w-full rounded-lg border border-slate-200 py-2.5 pl-10 pr-4 text-sm text-slate-800 outline-none transition-all placeholder:text-slate-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/10"
                    />
                    <Lock className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isUpdatingPass}
                  className="rounded-lg bg-brand-500 px-6 py-2.5 text-sm font-bold text-white shadow-md shadow-brand-500/10 hover:bg-brand-600 transition-colors disabled:opacity-60 cursor-pointer"
                >
                  {isUpdatingPass ? 'Updating...' : 'Change Password'}
                </button>
              </form>
            </motion.div>
          )}
        </div>

        {/* Right Side - Account Statistics card */}
        <div className="xl:col-span-4 space-y-6">
          <div className="rounded-2xl bg-white p-6 shadow-sm border border-slate-200/80">
            <h3 className="text-base font-bold text-slate-800 mb-6">Account Statistics</h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between py-1.5 border-b border-slate-50 last:border-0 text-sm">
                <div className="flex items-center gap-2 text-slate-500 font-semibold">
                  <Activity className="h-4.5 w-4.5 text-slate-400" />
                  <span>Total Analyses</span>
                </div>
                <span className="font-bold text-slate-800">{stats?.total_analyses || 0}</span>
              </div>

              <div className="flex items-center justify-between py-1.5 border-b border-slate-50 last:border-0 text-sm">
                <div className="flex items-center gap-2 text-slate-500 font-semibold">
                  <FileText className="h-4.5 w-4.5 text-slate-400" />
                  <span>Reports Generated</span>
                </div>
                <span className="font-bold text-slate-800">{stats?.total_analyses || 0}</span>
              </div>

              <div className="flex items-center justify-between py-1.5 border-b border-slate-50 last:border-0 text-sm">
                <div className="flex items-center gap-2 text-slate-500 font-semibold">
                  <AlertTriangle className="h-4.5 w-4.5 text-slate-400" />
                  <span>High-Risk Detected</span>
                </div>
                <span className="font-bold text-slate-800">{stats?.high_risk_count || 0}</span>
              </div>

              <div className="flex items-center justify-between py-1.5 border-b border-slate-50 last:border-0 text-sm">
                <div className="flex items-center gap-2 text-slate-500 font-semibold">
                  <ShieldCheck className="h-4.5 w-4.5 text-slate-400" />
                  <span>Account Status</span>
                </div>
                <span className="inline-flex items-center rounded-full bg-emerald-50 border border-emerald-100 px-2.5 py-0.5 text-xs font-bold text-emerald-600">
                  Active
                </span>
              </div>

              <div className="flex items-center justify-between py-1.5 border-b border-slate-50 last:border-0 text-sm">
                <div className="flex items-center gap-2 text-slate-500 font-semibold">
                  <CheckCircle className="h-4.5 w-4.5 text-slate-400" />
                  <span>Member Since</span>
                </div>
                <span className="font-bold text-slate-600 text-xs">
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
