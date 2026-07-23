import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, ArrowRight, Activity, ShieldAlert, BadgeCheck } from 'lucide-react';
import { PrimaryButton, SecondaryButton, Card } from '../components/common/Primitives';

const LandingPage = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-bg text-text-primary font-sans flex flex-col justify-between transition-colors duration-300">
      
      {/* TopAppBar */}
      <header className="fixed top-0 w-full z-50 bg-card border-b border-border select-none">
        <nav className="flex justify-between items-center px-6 md:px-12 py-4 max-w-[1280px] mx-auto w-full">
          <div 
            onClick={() => navigate('/')}
            className="flex items-center gap-3 cursor-pointer active:scale-95 transition-transform"
          >
            <ShieldCheck className="h-7 w-7 text-brand stroke-[2.5]" />
            <span className="font-sans text-xl font-semibold tracking-tight">RecruitSafe</span>
          </div>

          <div className="hidden md:flex items-center gap-8 font-mono text-[13px] font-bold tracking-wide">
            <Link to="/" className="text-brand">Home</Link>
            <a href="#features" className="text-text-secondary hover:text-brand transition-colors">Features</a>
            <a href="#enterprise" className="text-text-secondary hover:text-brand transition-colors">Enterprise</a>
          </div>

          <div className="flex items-center gap-4">
            <span className="material-symbols-outlined text-text-secondary cursor-pointer hover:bg-bg p-2 rounded-full transition-colors select-none">
              notifications
            </span>
            <PrimaryButton 
              onClick={() => navigate(isAuthenticated ? "/dashboard" : "/register")}
              className="text-xs px-4 py-2"
            >
              {isAuthenticated ? "Dashboard" : "Get Started"}
            </PrimaryButton>
          </div>
        </nav>
      </header>

      {/* Main Hero Section */}
      <main className="pt-24 flex-1 flex flex-col justify-center">
        
        {/* Hero Section */}
        <section className="relative min-h-[80vh] flex items-center px-6 md:px-12 max-w-[1280px] mx-auto overflow-hidden w-full">
          <div className="grid lg:grid-cols-2 gap-16 items-center z-10 w-full py-12">
            
            {/* Left Content */}
            <div className="space-y-8 text-left">
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-brand-light border border-brand/20 rounded-full select-none">
                <span className="w-2 h-2 rounded-full bg-success animate-pulse"></span>
                <span className="font-mono text-[11px] font-bold text-brand uppercase tracking-widest">
                  AI Detection Active
                </span>
              </div>
              
              <h1 className="font-sans text-4xl sm:text-5xl md:text-[48px] font-extrabold leading-tight tracking-tight">
                Job search with absolute confidence.
              </h1>
              
              <p className="font-sans text-[16px] leading-relaxed text-text-secondary max-w-md">
                The first intelligent security layer for modern recruitment. We verify every recruiter, analyze every offer, and shield you from phishing with enterprise-grade AI.
              </p>
              
              <div className="flex flex-wrap gap-4 pt-4">
                <PrimaryButton
                  onClick={() => navigate('/analysis/new')}
                  className="px-8 py-3.5 text-sm"
                >
                  <span>Start Scanning</span>
                  <ArrowRight className="h-4 w-4" />
                </PrimaryButton>
                <a
                  href="#features"
                  className="bg-card border border-border text-text-primary hover:bg-bg/50 px-8 py-3.5 rounded-lg font-mono text-[13px] font-bold transition-all active:scale-95 text-center flex items-center justify-center shadow-sm"
                >
                  How it works
                </a>
              </div>
            </div>

            {/* Right Graphic Widget */}
            <div className="relative hidden lg:block select-none">
              <div className="bg-card border border-border p-8 rounded-xl relative z-10 shadow-lg">
                <div className="flex items-center justify-between mb-8">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-brand-light flex items-center justify-center border border-brand/20">
                      <ShieldCheck className="h-5 w-5 text-brand" />
                    </div>
                    <div className="text-left">
                      <p className="font-mono text-[13px] font-bold text-text-primary">Verification Scan</p>
                      <p className="font-mono text-[11px] text-text-secondary">Global Talent Solutions Inc.</p>
                    </div>
                  </div>
                  <span className="font-mono text-[11px] text-success bg-success/15 px-3 py-1 border border-success/30 rounded-full font-bold">
                    LEGITIMATE
                  </span>
                </div>

                <div className="space-y-4">
                  <div className="h-1.5 w-full bg-bg overflow-hidden rounded-full border border-border">
                    <div className="h-full bg-brand w-[85%] transition-all duration-1000"></div>
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-bg p-3 border border-border rounded-lg text-center">
                      <p className="font-mono text-[10px] text-text-secondary mb-1 uppercase tracking-wider">DOMAIN</p>
                      <p className="font-sans text-xs font-bold text-success">SECURE</p>
                    </div>
                    <div className="bg-bg p-3 border border-border rounded-lg text-center">
                      <p className="font-mono text-[10px] text-text-secondary mb-1 uppercase tracking-wider">ID MATCH</p>
                      <p className="font-sans text-xs font-bold text-text-primary">98%</p>
                    </div>
                    <div className="bg-bg p-3 border border-border rounded-lg text-center">
                      <p className="font-mono text-[10px] text-text-secondary mb-1 uppercase tracking-wider">METADATA</p>
                      <p className="font-sans text-xs font-bold text-text-primary">CLEAN</p>
                    </div>
                  </div>
                </div>
              </div>
              {/* Decorative back layers */}
              <div className="absolute -top-12 -right-12 w-64 h-64 bg-brand/5 rounded-full blur-3xl"></div>
              <div className="absolute -bottom-8 -left-8 w-48 h-48 bg-brand/5 rounded-full blur-3xl"></div>
            </div>

          </div>
        </section>

        {/* Trust Indicators */}
        <section className="py-12 border-y border-border bg-card/40 select-none">
          <div className="max-w-[1280px] mx-auto px-6 md:px-12 w-full">
            <p className="font-mono text-[10px] text-text-secondary uppercase tracking-[0.2em] text-center mb-8 font-bold">
              Trusted by cybersecurity professionals from
            </p>
            <div className="flex flex-wrap justify-center items-center gap-12 md:gap-24 opacity-60 grayscale hover:opacity-100 transition-all font-bold tracking-tighter text-lg text-text-secondary">
              <span>VERIDIAN</span>
              <span>ARKTYPE</span>
              <span>PHALANX</span>
              <span>SENTINEL</span>
              <span>AETHER</span>
            </div>
          </div>
        </section>

        {/* Features Bento Grid */}
        <section id="features" className="py-32 px-6 md:px-12 max-w-[1280px] mx-auto w-full">
          <div className="text-center mb-20 space-y-4">
            <h2 className="font-sans text-3xl font-bold tracking-tight text-text-primary">Uncompromising Protection</h2>
            <p className="font-sans text-[16px] text-text-secondary max-w-2xl mx-auto leading-relaxed">
              RecruitSafe operates at the intersection of OSINT and AI logic engines to provide real-time defense against recruitment fraud.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            {/* Recruiter Verification */}
            <div className="md:col-span-8 bg-card border border-border p-10 flex flex-col justify-between hover:border-brand transition-colors group rounded-xl">
              <div className="max-w-md text-left">
                <div className="w-12 h-12 rounded-lg bg-brand-light flex items-center justify-center border border-brand/20 mb-6">
                  <BadgeCheck className="h-6 w-6 text-brand" />
                </div>
                <h3 className="font-sans text-xl font-bold text-text-primary mb-4">Recruiter Verification</h3>
                <p className="font-sans text-[15px] text-text-secondary leading-relaxed">
                  Cross-reference digital identities across LinkedIn, official corporate domains, and global identity databases to ensure you're talking to a real human.
                </p>
              </div>
              <div className="mt-8 flex items-center gap-2 text-brand font-mono text-[13px] font-bold cursor-pointer select-none">
                <span>Learn about Identity-Score™</span>
                <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>

            {/* Offer Analysis */}
            <div className="md:col-span-4 bg-card border border-border p-10 flex flex-col hover:border-brand transition-colors group rounded-xl text-left">
              <div className="w-12 h-12 rounded-lg bg-brand-light flex items-center justify-center border border-brand/20 mb-6">
                <Activity className="h-6 w-6 text-brand" />
              </div>
              <h3 className="font-sans text-xl font-bold text-text-primary mb-4">Offer Analysis</h3>
              <p className="font-sans text-[15px] text-text-secondary leading-relaxed">
                Our LLM analyzes contract language for suspicious clauses, unrealistic compensation, and fraudulent payment requests.
              </p>
            </div>

            {/* Phishing Protection */}
            <div className="md:col-span-4 bg-card border border-border p-10 flex flex-col hover:border-brand transition-colors group rounded-xl text-left">
              <div className="w-12 h-12 rounded-lg bg-brand-light flex items-center justify-center border border-brand/20 mb-6">
                <ShieldAlert className="h-6 w-6 text-brand" />
              </div>
              <h3 className="font-sans text-xl font-bold text-text-primary mb-4">Phishing Guard</h3>
              <p className="font-sans text-[15px] text-text-secondary leading-relaxed">
                Instant notification if a recruiter link redirects to a known malicious landing page or data harvesting site.
              </p>
            </div>

            {/* Global Network */}
            <div className="md:col-span-8 bg-card border border-border p-10 flex items-center gap-10 hover:border-brand transition-colors group relative overflow-hidden rounded-xl text-left">
              <div className="z-10 flex-1">
                <h3 className="font-sans text-xl font-bold text-text-primary mb-4">Community Threat Intelligence</h3>
                <p className="font-sans text-[15px] text-text-secondary max-w-sm leading-relaxed">
                  Join a global network of job seekers sharing real-time scam data to protect the entire ecosystem.
                </p>
              </div>
              <div className="hidden md:block w-48 h-48 bg-gradient-to-br from-brand/5 to-transparent rounded-full absolute -right-12 -bottom-12 blur-2xl select-none"></div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-32 px-6 md:px-12 select-none">
          <div className="max-w-4xl mx-auto bg-card border border-border p-16 text-center relative rounded-xl shadow-sm">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-bg px-4 flex items-center justify-center">
              <div className="w-14 h-14 bg-brand-light border border-brand/20 rounded-full flex items-center justify-center">
                <ShieldCheck className="h-7 w-7 text-brand" />
              </div>
            </div>
            
            <h2 className="font-sans text-3xl md:text-[40px] font-bold leading-tight text-text-primary mb-6 mt-4">
              Secure your professional future today.
            </h2>
            
            <p className="font-sans text-[16px] text-text-secondary mb-10 max-w-xl mx-auto leading-relaxed">
              Join 10,000+ professionals who use RecruitSafe to navigate the modern job market without fear.
            </p>
            
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <PrimaryButton 
                onClick={() => navigate('/register')}
                className="px-10 py-4 text-sm"
              >
                Create Free Account
              </PrimaryButton>
              <SecondaryButton 
                onClick={() => navigate('/analysis/new')}
                className="px-10 py-4 text-sm"
              >
                View Safety Report
              </SecondaryButton>
            </div>
          </div>
        </section>

      </main>

      {/* Footer */}
      <footer className="bg-card border-t border-border pt-16 pb-12 px-6 md:px-12 select-none w-full text-left">
        <div className="max-w-[1280px] mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-12 mb-16">
            <div className="col-span-2 space-y-4">
              <div className="flex items-center gap-3">
                <ShieldCheck className="h-6 w-6 text-brand" />
                <span className="font-sans text-xl font-bold tracking-tight text-text-primary">RecruitSafe</span>
              </div>
              <p className="font-sans text-xs text-text-secondary max-w-xs leading-relaxed">
                Restoring integrity to the global job market through advanced AI models and recruiter verification loops.
              </p>
            </div>
            
            <div>
              <h4 className="font-mono text-[11px] font-bold text-text-primary mb-4 uppercase tracking-widest">Product</h4>
              <ul className="space-y-3 font-sans text-xs text-text-secondary">
                <li><a className="hover:text-brand transition-colors" href="#">Scanner</a></li>
                <li><a className="hover:text-brand transition-colors" href="#">Verify API</a></li>
                <li><a className="hover:text-brand transition-colors" href="#">Safety Index</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-mono text-[11px] font-bold text-text-primary mb-4 uppercase tracking-widest">Company</h4>
              <ul className="space-y-3 font-sans text-xs text-text-secondary">
                <li><a className="hover:text-brand transition-colors" href="#">About</a></li>
                <li><a className="hover:text-brand transition-colors" href="#">Blog</a></li>
                <li><a className="hover:text-brand transition-colors" href="#">Careers</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-mono text-[11px] font-bold text-text-primary mb-4 uppercase tracking-widest">Support</h4>
              <ul className="space-y-3 font-sans text-xs text-text-secondary">
                <li><a className="hover:text-brand transition-colors" href="#">Help Center</a></li>
                <li><a className="hover:text-brand transition-colors" href="#">Safety Guide</a></li>
                <li><a className="hover:text-brand transition-colors" href="#">Contact</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-mono text-[11px] font-bold text-text-primary mb-4 uppercase tracking-widest">Legal</h4>
              <ul className="space-y-3 font-sans text-xs text-text-secondary">
                <li><a className="hover:text-brand transition-colors" href="#">Privacy</a></li>
                <li><a className="hover:text-brand transition-colors" href="#">Terms</a></li>
                <li><a className="hover:text-brand transition-colors" href="#">Security</a></li>
              </ul>
            </div>
          </div>
          
          <div className="flex flex-col md:flex-row justify-between items-center border-t border-border pt-8 gap-4">
            <p className="font-mono text-[10px] text-text-secondary font-bold">© {new Date().getFullYear()} RecruitSafe Inc. All rights reserved.</p>
            <div className="flex gap-6 text-text-secondary">
              <a className="hover:text-brand transition-colors" href="#"><span className="material-symbols-outlined text-sm">public</span></a>
              <a className="hover:text-brand transition-colors" href="#"><span className="material-symbols-outlined text-sm">share</span></a>
              <a className="hover:text-brand transition-colors" href="#"><span className="material-symbols-outlined text-sm">alternate_email</span></a>
            </div>
          </div>
        </div>
      </footer>
      
    </div>
  );
};

export default LandingPage;
