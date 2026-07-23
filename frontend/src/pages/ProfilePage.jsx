import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import Layout from '../components/common/Layout';
import { Card, PrimaryButton, InputField, Alert, Badge } from '../components/common/Primitives';
import { 
  User, 
  Mail, 
  Lock, 
  ShieldCheck, 
  Activity, 
  AlertTriangle,
  FileText,
  CheckCircle,
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

  // Account stats state
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
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start max-w-5xl mx-auto select-none">
        
        {/* Left Side - Edit forms (8 / 12) */}
        <div className="xl:col-span-8 space-y-6">
          {/* Tab selectors */}
          <div className="flex border-b border-border">
            <button
              onClick={() => setActiveTab('info')}
              className={`pb-4 px-6 text-sm font-bold border-b-2 transition-all relative cursor-pointer ${
                activeTab === 'info'
                  ? 'text-brand border-brand font-extrabold'
                  : 'border-transparent text-text-secondary hover:text-text-primary'
              }`}
            >
              Profile Information
            </button>
            <button
              onClick={() => setActiveTab('password')}
              className={`pb-4 px-6 text-sm font-bold border-b-2 transition-all relative cursor-pointer ${
                activeTab === 'password'
                  ? 'text-brand border-brand font-extrabold'
                  : 'border-transparent text-text-secondary hover:text-text-primary'
              }`}
            >
              Change Password
            </button>
          </div>

          {/* Tab Panels */}
          <div className="relative">
            {activeTab === 'info' ? (
              <Card className="text-left">
                <h3 className="text-lg font-bold text-text-primary mb-6">Profile Settings</h3>
                
                <AnimatePresence>
                  {infoError && (
                    <div className="mb-4">
                      <Alert variant="danger" onClose={() => setInfoError('')}>
                        {infoError}
                      </Alert>
                    </div>
                  )}
                  {infoSuccess && (
                    <div className="mb-4">
                      <Alert variant="success" onClose={() => setInfoSuccess('')}>
                        {infoSuccess}
                      </Alert>
                    </div>
                  )}
                </AnimatePresence>

                <form onSubmit={handleUpdateInfo} className="space-y-6 max-w-lg">
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
                    <User className="absolute right-4 bottom-3.5 h-4.5 w-4.5 text-text-secondary/40" />
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
                    <Mail className="absolute right-4 bottom-3.5 h-4.5 w-4.5 text-text-secondary/40" />
                  </div>

                  <PrimaryButton
                    type="submit"
                    disabled={isUpdatingInfo}
                  >
                    {isUpdatingInfo ? 'Updating...' : 'Update Profile'}
                  </PrimaryButton>
                </form>
              </Card>
            ) : (
              <Card className="text-left">
                <h3 className="text-lg font-bold text-text-primary mb-6">Security Settings</h3>
                
                <AnimatePresence>
                  {passError && (
                    <div className="mb-4">
                      <Alert variant="danger" onClose={() => setPassError('')}>
                        {passError}
                      </Alert>
                    </div>
                  )}
                  {passSuccess && (
                    <div className="mb-4">
                      <Alert variant="success" onClose={() => setPassSuccess('')}>
                        {passSuccess}
                      </Alert>
                    </div>
                  )}
                </AnimatePresence>

                <form onSubmit={handleUpdatePassword} className="space-y-6 max-w-lg">
                  <div className="relative">
                    <InputField
                      label="Current Password"
                      id="currentPass"
                      type="password"
                      required
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      placeholder="••••••••"
                    />
                    <Lock className="absolute right-4 bottom-3.5 h-4.5 w-4.5 text-text-secondary/40" />
                  </div>

                  <div className="relative">
                    <InputField
                      label="New Password"
                      id="newPass"
                      type="password"
                      required
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="••••••••"
                    />
                    <Lock className="absolute right-4 bottom-3.5 h-4.5 w-4.5 text-text-secondary/40" />
                  </div>

                  <div className="relative">
                    <InputField
                      label="Confirm New Password"
                      id="confirmPass"
                      type="password"
                      required
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="••••••••"
                    />
                    <Lock className="absolute right-4 bottom-3.5 h-4.5 w-4.5 text-text-secondary/40" />
                  </div>

                  <PrimaryButton
                    type="submit"
                    disabled={isUpdatingPass}
                  >
                    {isUpdatingPass ? 'Updating...' : 'Change Password'}
                  </PrimaryButton>
                </form>
              </Card>
            )}
          </div>
        </div>

        {/* Right Side - Account Statistics (4 / 12) */}
        <div className="xl:col-span-4 space-y-6">
          <Card className="text-left space-y-6">
            <div className="flex items-center gap-1.5 text-brand mb-2">
              <Sparkles className="h-4.5 w-4.5" />
              <h3 className="text-base font-bold text-text-primary">Account Statistics</h3>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between py-2 border-b border-border last:border-0 text-xs font-semibold">
                <div className="flex items-center gap-2 text-text-secondary">
                  <Activity className="h-4.5 w-4.5 text-text-secondary/45" />
                  <span>Total Analyses</span>
                </div>
                <span className="font-bold text-text-primary">{stats?.total_analyses || 0}</span>
              </div>

              <div className="flex items-center justify-between py-2 border-b border-border last:border-0 text-xs font-semibold">
                <div className="flex items-center gap-2 text-text-secondary">
                  <FileText className="h-4.5 w-4.5 text-text-secondary/45" />
                  <span>Reports Generated</span>
                </div>
                <span className="font-bold text-text-primary">{stats?.total_analyses || 0}</span>
              </div>

              <div className="flex items-center justify-between py-2 border-b border-border last:border-0 text-xs font-semibold">
                <div className="flex items-center gap-2 text-text-secondary">
                  <AlertTriangle className="h-4.5 w-4.5 text-text-secondary/45" />
                  <span>High-Risk Detected</span>
                </div>
                <span className="font-bold text-danger">{stats?.high_risk_count || 0}</span>
              </div>

              <div className="flex items-center justify-between py-2 border-b border-border last:border-0 text-xs font-semibold">
                <div className="flex items-center gap-2 text-text-secondary">
                  <ShieldCheck className="h-4.5 w-4.5 text-text-secondary/45" />
                  <span>Account Status</span>
                </div>
                <Badge variant="success">Active</Badge>
              </div>

              <div className="flex items-center justify-between py-2 border-b border-border last:border-0 text-xs font-semibold">
                <div className="flex items-center gap-2 text-text-secondary">
                  <CheckCircle className="h-4.5 w-4.5 text-text-secondary/45" />
                  <span>Member Since</span>
                </div>
                <span className="font-mono text-xs font-bold text-text-primary">
                  {user?.created_at ? new Date(user.created_at).toLocaleDateString(undefined, {
                    month: 'long',
                    day: 'numeric',
                    year: 'numeric'
                  }) : '—'}
                </span>
              </div>
            </div>
          </Card>
        </div>

      </div>
    </Layout>
  );
};

export default ProfilePage;
