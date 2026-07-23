import React from 'react';
import { ShieldCheck } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

const AuthLayout = ({ children, title, subtitle }) => {
  const { theme } = useTheme();

  return (
    <div className="min-h-screen bg-bg text-text-primary font-sans flex transition-colors duration-300">
      
      {/* Left side: Premium dark branding panel (hidden on mobile/tablet) */}
      <div className="hidden lg:flex lg:w-1/2 bg-[#111315] text-[#F8F8F8] p-16 flex-col justify-between relative overflow-hidden select-none border-r border-white/5">
        {/* Subtle background glow */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#8B5E3C]/10 rounded-full blur-3xl" />
        <div className="absolute bottom-10 -right-20 w-80 h-80 bg-[#8B5E3C]/5 rounded-full blur-2xl" />

        {/* Branding header */}
        <div className="flex items-center gap-3 relative z-10">
          <ShieldCheck className="h-8 w-8 text-brand stroke-[2.5]" />
          <span className="font-sans text-2xl font-bold tracking-tight text-white">RecruitSafe</span>
        </div>

        {/* Core illustration and checklist */}
        <div className="space-y-12 relative z-10 max-w-md my-auto">
          <div className="space-y-4">
            <h2 className="text-3xl font-bold leading-tight text-white">
              Verify your next career move with confidence.
            </h2>
            <p className="text-sm text-[#A3A3A3] leading-relaxed">
              RecruitSafe uses advanced heuristic domain mapping and artificial intelligence to shield job seekers from phishing campaigns, data harvesting, and financial scam outreach.
            </p>
          </div>

          {/* Features list */}
          <ul className="space-y-4 text-sm font-semibold text-[#F8F8F8] text-left">
            <li className="flex items-center gap-3">
              <span className="material-symbols-outlined text-brand" style={{ fontVariationSettings: "'FILL' 1" }}>verified</span>
              <span>Detect Fake Recruiters</span>
            </li>
            <li className="flex items-center gap-3">
              <span className="material-symbols-outlined text-brand" style={{ fontVariationSettings: "'FILL' 1" }}>verified</span>
              <span>Verify Company Domains</span>
            </li>
            <li className="flex items-center gap-3">
              <span className="material-symbols-outlined text-brand" style={{ fontVariationSettings: "'FILL' 1" }}>verified</span>
              <span>Analyze Offer Letters</span>
            </li>
            <li className="flex items-center gap-3">
              <span className="material-symbols-outlined text-brand" style={{ fontVariationSettings: "'FILL' 1" }}>verified</span>
              <span>AI Scam Detection</span>
            </li>
          </ul>

          {/* Statistics Grid */}
          <div className="grid grid-cols-3 gap-6 pt-6 border-t border-white/10 text-left">
            <div>
              <p className="text-2xl font-extrabold text-white">50K+</p>
              <p className="text-[10px] text-[#A3A3A3] font-bold uppercase tracking-wider mt-1">Analyses</p>
            </div>
            <div>
              <p className="text-2xl font-extrabold text-white">98%</p>
              <p className="text-[10px] text-[#A3A3A3] font-bold uppercase tracking-wider mt-1">Accuracy</p>
            </div>
            <div>
              <p className="text-2xl font-extrabold text-white">24/7</p>
              <p className="text-[10px] text-[#A3A3A3] font-bold uppercase tracking-wider mt-1">Protection</p>
            </div>
          </div>
        </div>

        {/* Footer brand details */}
        <div className="text-xs text-[#6B7280] relative z-10 text-left">
          &copy; {new Date().getFullYear()} RecruitSafe Inc. Enterprise Grade Security.
        </div>
      </div>

      {/* Right side: Modern login/signup form area */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 sm:p-12 md:p-16 overflow-y-auto">
        <div className="w-full max-w-md mx-auto space-y-8 py-8 animate-in fade-in slide-in-from-bottom-3 duration-500 text-left">
          
          {/* Header */}
          <div className="space-y-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-text-primary">{title}</h1>
            {subtitle && <p className="text-sm text-text-secondary">{subtitle}</p>}
          </div>

          {/* Form Content */}
          {children}

        </div>
      </div>

    </div>
  );
};

export default AuthLayout;
