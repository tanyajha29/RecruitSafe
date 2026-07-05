import React from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Bell, Plus, ShieldCheck } from 'lucide-react';

const Header = () => {
  const { user } = useAuth();
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
    <header className="h-20 bg-white border-b border-slate-200/80 flex items-center justify-between px-8 relative z-10 shrink-0">
      {/* Title */}
      <div>
        <h1 className="text-xl font-bold text-slate-800">{getPageTitle()}</h1>
        <p className="text-xs text-slate-400 font-medium mt-0.5">
          Welcome back, <span className="font-semibold text-slate-600">{user?.full_name || 'User'}</span>
        </p>
      </div>

      {/* Header Actions */}
      <div className="flex items-center gap-4">
        {/* Quick New Analysis Button */}
        {location.pathname !== '/analysis/new' && (
          <Link
            to="/analysis/new"
            className="flex items-center gap-1.5 rounded-lg bg-brand-500 hover:bg-brand-600 text-white font-bold text-xs px-3.5 py-2 shadow-md shadow-brand-500/10 transition-colors cursor-pointer"
          >
            <Plus className="h-3.5 w-3.5" />
            <span>New Check</span>
          </Link>
        )}

        {/* Notifications Icon Shortcut */}
        <Link
          to="/notifications"
          className="h-9 w-9 rounded-lg border border-slate-200 hover:border-slate-300 hover:bg-slate-50 flex items-center justify-center text-slate-500 relative transition-all cursor-pointer"
        >
          <Bell className="h-4.5 w-4.5" />
          {/* Unread dot indicator (pulsing) */}
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-red-500 ring-2 ring-white animate-pulse"></span>
        </Link>
      </div>
    </header>
  );
};

export default Header;
