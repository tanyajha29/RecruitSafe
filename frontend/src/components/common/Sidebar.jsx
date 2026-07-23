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
      className="bg-card border-r border-border text-text-secondary flex flex-col h-screen shrink-0 relative z-20"
    >
      {/* Collapse Toggle Button */}
      <button 
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute top-6 -right-3 h-6 w-6 rounded-full border border-border bg-card text-text-secondary hover:text-text-primary flex items-center justify-center shadow-sm cursor-pointer hover:scale-105 transition-transform z-30"
      >
        {isCollapsed ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
      </button>

      {/* Brand Header */}
      <div className="h-20 flex items-center gap-2.5 px-6 border-b border-border overflow-hidden shrink-0">
        <ShieldCheck className="h-7 w-7 text-brand stroke-[2.5]" />
        <AnimatePresence>
          {!isCollapsed && (
            <motion.span 
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              className="text-text-primary font-bold text-lg tracking-tight whitespace-nowrap"
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
              className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-semibold transition-all duration-200 cursor-pointer relative group ${isActive ? 'text-white' : 'hover:bg-bg text-text-secondary hover:text-brand'}`}
            >
              {/* Active Background Slide Indicator */}
              {isActive && (
                <motion.div
                  layoutId="activeNavIndicator"
                  className="absolute inset-0 bg-brand rounded-lg -z-10 shadow-sm"
                  transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                />
              )}
              
              <Icon className={`h-4.5 w-4.5 shrink-0 transition-colors duration-200 ${isActive ? 'text-white' : 'text-text-secondary/80 group-hover:text-brand'}`} />
              
              <AnimatePresence>
                {!isCollapsed && (
                  <motion.span 
                    initial={{ opacity: 0, width: 0 }}
                    animate={{ opacity: 1, width: 'auto' }}
                    exit={{ opacity: 0, width: 0 }}
                    className={`whitespace-nowrap transition-colors duration-200 ${isActive ? 'text-white font-bold' : 'group-hover:text-text-primary'}`}
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
      <div className="p-4 border-t border-border shrink-0">
        <div className="flex items-center gap-3 bg-bg border border-border rounded-lg p-3 mb-2 overflow-hidden">
          {/* Avatar */}
          <div className="h-9 w-9 rounded-full bg-brand-light border border-brand/20 flex items-center justify-center font-bold text-brand text-sm shrink-0">
            {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
          </div>
          <AnimatePresence>
            {!isCollapsed && (
              <motion.div 
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                className="min-w-0 flex-1 text-left"
              >
                <p className="text-xs font-bold text-text-primary truncate">{user?.full_name || 'Loading...'}</p>
                <p className="text-[9px] text-text-secondary font-semibold uppercase tracking-wider">Standard Plan</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-semibold text-text-secondary hover:bg-danger/5 hover:text-danger transition-colors cursor-pointer"
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
