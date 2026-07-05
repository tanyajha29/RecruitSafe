import React from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { motion, AnimatePresence } from 'framer-motion';
import { Bell, Plus, Sun, Moon } from 'lucide-react';

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
    <header className="h-20 bg-white dark:bg-slate-900 border-b border-slate-200/80 dark:border-slate-800/80 flex items-center justify-between px-8 relative z-10 shrink-0 transition-colors duration-300">
      {/* Title */}
      <div>
        <h1 className="text-xl font-bold text-slate-800 dark:text-slate-100">{getPageTitle()}</h1>
        <p className="text-xs text-slate-400 dark:text-slate-500 font-medium mt-0.5">
          Welcome back, <span className="font-semibold text-slate-600 dark:text-slate-300">{user?.full_name || 'User'}</span>
        </p>
      </div>

      {/* Header Actions */}
      <div className="flex items-center gap-4">
        {/* Quick New Analysis Button */}
        {location.pathname !== '/analysis/new' && (
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Link
              to="/analysis/new"
              className="flex items-center gap-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-600 dark:hover:bg-indigo-500 text-white font-bold text-xs px-3.5 py-2 shadow-md shadow-indigo-600/10 dark:shadow-none transition-colors cursor-pointer"
            >
              <Plus className="h-3.5 w-3.5" />
              <span>New Check</span>
            </Link>
          </motion.div>
        )}



        {/* Theme Toggle Switcher */}
        <motion.button
          onClick={toggleTheme}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="h-9 w-9 rounded-lg border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/50 flex items-center justify-center text-slate-500 dark:text-slate-400 cursor-pointer overflow-hidden relative transition-colors duration-300"
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
            className="h-9 w-9 rounded-lg border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/50 flex items-center justify-center text-slate-500 dark:text-slate-400 relative transition-colors duration-300 cursor-pointer"
          >
            <Bell className="h-4.5 w-4.5" />
            <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-red-500 ring-2 ring-white dark:ring-slate-900 animate-pulse"></span>
          </Link>
        </motion.div>

        {/* User initials Avatar */}
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Link 
            to="/profile" 
            className="h-9 w-9 rounded-full bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900/50 flex items-center justify-center font-bold text-indigo-600 dark:text-indigo-400 text-xs transition-colors duration-300 cursor-pointer"
          >
            {user?.full_name ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) : 'U'}
          </Link>
        </motion.div>
      </div>
    </header>
  );
};

export default Header;
