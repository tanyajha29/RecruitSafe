import React from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { motion, AnimatePresence } from 'framer-motion';
import { Bell, Plus, Sun, Moon } from 'lucide-react';
import { PrimaryButton } from './Primitives';

const Header = () => {
  const { user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();

  // Determine page title based on current pathname
  const getPageTitle = () => {
    const path = location.pathname;
    if (path === '/dashboard') return 'Dashboard';
    if (path === '/analysis/new') return 'New Analysis';
    if (path.startsWith('/analysis/')) return 'Analysis Details';
    if (path === '/history') return 'Analysis History';
    if (path === '/profile') return 'User Profile';
    if (path === '/notifications') return 'Notifications';
    return 'RecruitSafe';
  };

  return (
    <header className="h-20 bg-card border-b border-border flex items-center justify-between px-8 relative z-10 shrink-0 transition-colors duration-300">
      {/* Title */}
      <div className="text-left">
        <h1 className="text-xl font-bold text-text-primary">{getPageTitle()}</h1>
        <p className="text-xs text-text-secondary font-medium mt-0.5">
          Welcome back, <span className="font-semibold text-text-primary">{user?.full_name || 'User'}</span>
        </p>
      </div>

      {/* Header Actions */}
      <div className="flex items-center gap-4">
        {/* Quick New Analysis Button */}
        {location.pathname !== '/analysis/new' && (
          <PrimaryButton
            onClick={() => navigate('/analysis/new')}
            className="text-xs px-3.5 py-2"
          >
            <Plus className="h-3.5 w-3.5" />
            <span>New Check</span>
          </PrimaryButton>
        )}

        {/* Theme Toggle Switcher */}
        <motion.button
          onClick={toggleTheme}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="h-9 w-9 rounded-lg border border-border bg-card hover:bg-bg flex items-center justify-center text-text-secondary cursor-pointer overflow-hidden relative transition-colors duration-300"
        >
          <AnimatePresence mode="wait" initial={false}>
            {theme === 'light' ? (
              <motion.div
                key="moon"
                initial={{ y: 20, opacity: 0, rotate: 40 }}
                animate={{ y: 0, opacity: 1, rotate: 0 }}
                exit={{ y: -20, opacity: 0, rotate: -40 }}
                transition={{ duration: 0.25 }}
              >
                <Moon className="h-4.5 w-4.5" />
              </motion.div>
            ) : (
              <motion.div
                key="sun"
                initial={{ y: 20, opacity: 0, rotate: -40 }}
                animate={{ y: 0, opacity: 1, rotate: 0 }}
                exit={{ y: -20, opacity: 0, rotate: 40 }}
                transition={{ duration: 0.25 }}
              >
                <Sun className="h-4.5 w-4.5" />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.button>

        {/* Notifications Icon Shortcut */}
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Link
            to="/notifications"
            className="h-9 w-9 rounded-lg border border-border bg-card hover:bg-bg flex items-center justify-center text-text-secondary relative transition-colors duration-300 cursor-pointer"
          >
            <Bell className="h-4.5 w-4.5" />
            <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-danger ring-2 ring-card animate-pulse"></span>
          </Link>
        </motion.div>

        {/* User initials Avatar */}
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Link 
            to="/profile" 
            className="h-9 w-9 rounded-full bg-brand-light border border-brand/20 flex items-center justify-center font-bold text-brand text-xs transition-colors duration-300 cursor-pointer"
          >
            {user?.full_name ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) : 'U'}
          </Link>
        </motion.div>
      </div>
    </header>
  );
};

export default Header;
