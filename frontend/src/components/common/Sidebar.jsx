import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  LayoutDashboard, 
  PlusCircle, 
  History, 
  User, 
  Bell, 
  LogOut, 
  ShieldCheck 
} from 'lucide-react';

const Sidebar = () => {
  const { user, logoutUser } = useAuth();
  const navigate = useNavigate();

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
    <aside className="w-64 bg-darkbg-950 border-r border-slate-800/40 text-slate-400 flex flex-col h-screen shrink-0 relative z-20">
      {/* Brand Header */}
      <div className="h-20 flex items-center gap-2 px-6 border-b border-slate-800/40">
        <ShieldCheck className="h-7 w-7 text-brand-500 stroke-[2.5]" />
        <span className="text-white font-bold text-xl tracking-tight">RecruitSafe</span>
      </div>

      {/* Nav List */}
      <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-semibold transition-all duration-200 cursor-pointer ${
                  isActive
                    ? 'bg-brand-500 text-white shadow-lg shadow-brand-500/20'
                    : 'text-slate-400 hover:bg-slate-800/30 hover:text-slate-200'
                }`
              }
            >
              <Icon className="h-4.5 w-4.5 shrink-0" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer Profile card */}
      <div className="p-4 border-t border-slate-800/40">
        <div className="flex items-center gap-3 bg-slate-900/40 border border-slate-800/30 rounded-xl p-3 mb-2">
          {/* Mock Avatar */}
          <div className="h-9 w-9 rounded-full bg-brand-500/20 border border-brand-500/30 flex items-center justify-center font-bold text-brand-400 text-sm">
            {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-bold text-white truncate">{user?.full_name || 'Loading...'}</p>
            <p className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Standard Plan</p>
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-semibold text-slate-500 hover:bg-red-500/10 hover:text-red-400 transition-colors cursor-pointer"
        >
          <LogOut className="h-4.5 w-4.5 shrink-0" />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
