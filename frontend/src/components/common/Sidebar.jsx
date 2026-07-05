import React, { useState } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  LayoutDashboard, 
  PlusCircle, 
  History, 
  User, 
  Bell, 
  LogOut, 
  ShieldCheck,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

const Sidebar = () => {
  const { user, logoutUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isCollapsed, setIsCollapsed] = useState(false);

  const handleLogout = async () => {
    try {
      await logoutUser();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'New Analysis', path: '/analysis/new', icon: PlusCircle },
    { name: 'History', path: '/history', icon: History },
    { name: 'Profile', path: '/profile', icon: User },
    { name: 'Notifications', path: '/notifications', icon: Bell },
  ];

  return (
    <motion.aside 
      animate={{ width: isCollapsed ? 80 : 256 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="bg-white dark:bg-slate-900 border-r border-slate-200/80 dark:border-slate-800/80 text-slate-500 dark:text-slate-400 flex flex-col h-screen shrink-0 relative z-20 transition-colors duration-300"
    >
      {/* Collapse Toggle Button */}
      <button 
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute top-6 -right-3 h-6 w-6 rounded-full border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-850 flex items-center justify-center shadow-sm cursor-pointer hover:scale-105 transition-transform z-30"
      >
        {isCollapsed ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
      </button>

      {/* Brand Header */}
      <div className="h-20 flex items-center gap-2.5 px-6 border-b border-slate-200/80 dark:border-slate-800/80 overflow-hidden shrink-0">
        <ShieldCheck className="h-7 w-7 text-indigo-600 dark:text-indigo-500 stroke-[2.5]" />
        <AnimatePresence>
          {!isCollapsed && (
            <motion.span 
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              className="text-slate-800 dark:text-white font-bold text-lg tracking-tight whitespace-nowrap"
            >
              RecruitSafe
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      {/* Nav List */}
      <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto overflow-x-hidden">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <NavLink
              key={item.name}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-200 cursor-pointer relative group ${isActive ? 'text-white' : 'hover:bg-slate-100 dark:hover:bg-slate-800/40 text-slate-500 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400'}`}
            >
              {/* Active Background Slide Indicator */}
              {isActive && (
                <motion.div
                  layoutId="activeNavIndicator"
                  className="absolute inset-0 bg-indigo-600 rounded-xl -z-10 shadow-sm"
                  transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                />
              )}
              
              <Icon className={`h-4.5 w-4.5 shrink-0 transition-colors duration-200 ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400'}`} />
              
              <AnimatePresence>
                {!isCollapsed && (
                  <motion.span 
                    initial={{ opacity: 0, width: 0 }}
                    animate={{ opacity: 1, width: 'auto' }}
                    exit={{ opacity: 0, width: 0 }}
                    className={`whitespace-nowrap transition-colors duration-200 ${isActive ? 'text-white font-bold' : 'group-hover:text-indigo-700 dark:group-hover:text-indigo-350'}`}
                  >
                    {item.name}
                  </motion.span>
                )}
              </AnimatePresence>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer Profile card */}
      <div className="p-4 border-t border-slate-200/80 dark:border-slate-800/80 shrink-0">
        <div className="flex items-center gap-3 bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800/30 rounded-xl p-3 mb-2 overflow-hidden">
          {/* Avatar */}
          <div className="h-9 w-9 rounded-full bg-indigo-100 dark:bg-indigo-950/50 border border-indigo-200 dark:border-indigo-900 flex items-center justify-center font-bold text-indigo-600 dark:text-indigo-400 text-sm shrink-0">
            {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
          </div>
          <AnimatePresence>
            {!isCollapsed && (
              <motion.div 
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                className="min-w-0 flex-1"
              >
                <p className="text-xs font-bold text-slate-800 dark:text-slate-200 truncate">{user?.full_name || 'Loading...'}</p>
                <p className="text-[9px] text-slate-400 dark:text-slate-500 font-semibold uppercase tracking-wider">Standard Plan</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold text-slate-400 hover:bg-red-50 dark:hover:bg-red-950/20 hover:text-red-650 dark:hover:text-red-400 transition-colors cursor-pointer"
        >
          <LogOut className="h-4.5 w-4.5 shrink-0" />
          <AnimatePresence>
            {!isCollapsed && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                Logout
              </motion.span>
            )}
          </AnimatePresence>
        </button>
      </div>
    </motion.aside>
  );
};

export default Sidebar;
