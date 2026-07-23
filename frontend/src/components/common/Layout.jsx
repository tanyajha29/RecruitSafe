import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import { useAuth } from '../../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';

const Layout = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  if (isAuthenticated) {
    return (
      <div className="flex h-screen w-screen overflow-hidden bg-bg text-text-primary font-sans transition-colors duration-300">
        {/* Navigation Sidebar */}
        <Sidebar />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col h-full overflow-hidden">
          {/* Header */}
          <Header />

          {/* Scrollable page body */}
          <main className="flex-1 overflow-y-auto p-8 relative bg-bg">
            {children}
          </main>
        </div>
      </div>
    );
  }

  // Guest Top Bar & Layout (matching brand aesthetics)
  return (
    <div className="min-h-screen bg-bg text-text-primary font-sans transition-colors duration-300 flex flex-col justify-between">
      
      {/* Header */}
      <header className="fixed top-0 w-full z-50 bg-card border-b border-border select-none">
        <div className="flex justify-between items-center px-6 md:px-12 py-4 max-w-[1280px] mx-auto w-full">
          <div 
            onClick={() => navigate('/')}
            className="flex items-center gap-3 cursor-pointer active:scale-95 transition-transform animate-in fade-in"
          >
            <span className="material-symbols-outlined text-brand text-xl font-semibold">verified_user</span>
            <span className="font-sans text-xl font-semibold text-text-primary tracking-tight">RecruitSafe</span>
          </div>

          <div className="flex items-center gap-6">
            <nav className="hidden md:flex items-center gap-8 font-mono text-[13px] font-bold">
              <Link className="text-text-secondary hover:text-brand transition-colors" to="/">Home</Link>
              <Link className="text-brand" to="/analysis/new">Scan</Link>
              <Link className="text-text-secondary hover:text-brand transition-colors" to="/login">History</Link>
              <Link className="text-text-secondary hover:text-brand transition-colors" to="/login">Profile</Link>
            </nav>
            <span 
              onClick={() => navigate('/login')}
              className="material-symbols-outlined text-brand cursor-pointer hover:bg-bg p-2 rounded-full transition-colors"
            >
              notifications
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow pt-24 pb-32">
        <div className="px-6 md:px-12 max-w-[1280px] mx-auto w-full">
          {children}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-card border-t border-border py-8 text-center text-xs text-text-secondary select-none w-full">
        <p>&copy; {new Date().getFullYear()} RecruitSafe Inc. All rights reserved.</p>
      </footer>

    </div>
  );
};

export default Layout;
