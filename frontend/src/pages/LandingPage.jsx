import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ShieldAlert, 
  Sparkles, 
  FileText, 
  CheckCircle, 
  Globe, 
  Mail, 
  ShieldCheck, 
  Lock, 
  FileLock, 
  Layers,
  ArrowRight
} from 'lucide-react';

const LandingPage = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1, delayChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1, transition: { duration: 0.45, ease: "easeOut" } }
  };

  return (
    <div className="min-h-screen bg-darkbg-950 text-white relative overflow-hidden font-sans">
      {/* Background ambient glowing blobs */}
      <div className="absolute top-[-20%] left-[-10%] h-[600px] w-[600px] rounded-full bg-brand-500/10 blur-[150px] pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-5%] h-[500px] w-[500px] rounded-full bg-indigo-500/10 blur-[120px] pointer-events-none"></div>

      {/* Navigation Header */}
      <header className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between border-b border-slate-800/40 relative z-10">
        <div className="flex items-center gap-2 font-bold text-2xl text-brand-500">
          <ShieldCheck className="h-7 w-7 stroke-[2.5]" />
          <span className="text-white">RecruitSafe</span>
        </div>
        <nav className="hidden md:flex items-center gap-8 text-sm font-semibold text-slate-400">
          <a href="#features" className="hover:text-white transition-colors">Features</a>
          <a href="#workflow" className="hover:text-white transition-colors">How It Works</a>
          <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
          <a href="#about" className="hover:text-white transition-colors">About</a>
        </nav>
        <div className="flex items-center gap-4">
          <Link to="/login" className="text-sm font-bold text-slate-300 hover:text-white transition-colors">
            Login
          </Link>
          <Link
            to="/register"
            className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-bold text-white shadow-lg shadow-brand-500/20 hover:bg-brand-600 transition-all cursor-pointer"
          >
            Sign Up
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-24 relative z-10">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center"
        >
          {/* Hero Left */}
          <div className="lg:col-span-7 space-y-8 text-center lg:text-left">
            <motion.div
              variants={itemVariants}
              className="inline-flex items-center gap-2 rounded-full border border-brand-500/30 bg-brand-500/10 px-4 py-1.5 text-xs font-bold text-brand-300 uppercase tracking-wider"
            >
              <Sparkles className="h-3.5 w-3.5 fill-brand-300/20" />
              <span>Version 1.0 Live</span>
            </motion.div>

            <motion.h1
              variants={itemVariants}
              className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-[1.1] text-white"
            >
              AI-Powered <br />
              <span className="bg-gradient-to-r from-brand-500 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
                Job Scam Detector
              </span>
            </motion.h1>

            <motion.p
              variants={itemVariants}
              className="text-lg text-slate-400 max-w-xl mx-auto lg:mx-0 leading-relaxed"
            >
              Analyze job offers, recruiter emails, company websites, and documents to detect employment fraud before sharing your personal details.
            </motion.p>

            <motion.div variants={itemVariants} className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4">
              <Link
                to="/register"
                className="flex items-center gap-2 rounded-lg bg-brand-500 px-6 py-3.5 text-sm font-bold text-white shadow-xl shadow-brand-500/30 hover:bg-brand-600 transition-all group cursor-pointer"
              >
                <span>Get Started Free</span>
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Link>
              <a
                href="#features"
                className="rounded-lg border border-slate-700 bg-slate-800/30 px-6 py-3.5 text-sm font-bold text-slate-300 hover:bg-slate-800 hover:text-white transition-colors cursor-pointer"
              >
                Learn More
              </a>
            </motion.div>

            {/* Quick Metrics */}
            <motion.div
              variants={itemVariants}
              className="pt-8 grid grid-cols-2 sm:grid-cols-4 gap-6 border-t border-slate-800/40"
            >
              <div>
                <p className="text-2xl font-black text-white">10K+</p>
                <p className="text-xs text-slate-500 mt-1 uppercase font-bold tracking-wider">Jobs Checked</p>
              </div>
              <div>
                <p className="text-2xl font-black text-brand-400">98.6%</p>
                <p className="text-xs text-slate-500 mt-1 uppercase font-bold tracking-wider">Detection Rate</p>
              </div>
              <div>
                <p className="text-2xl font-black text-white">5K+</p>
                <p className="text-xs text-slate-500 mt-1 uppercase font-bold tracking-wider">Happy Users</p>
              </div>
              <div>
                <p className="text-2xl font-black text-brand-400">24/7</p>
                <p className="text-xs text-slate-500 mt-1 uppercase font-bold tracking-wider">Active Shield</p>
              </div>
            </motion.div>
          </div>

          {/* Hero Right - Shield Visual */}
          <div className="lg:col-span-5 flex justify-center relative">
            {/* Glowing background ring */}
            <div className="absolute inset-0 m-auto h-72 w-72 rounded-full border border-brand-500/20 bg-brand-500/5 animate-pulse blur-xl"></div>
            
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.6, ease: "easeOut" }}
              className="relative p-8 rounded-3xl bg-slate-900/60 border border-slate-800/60 shadow-2xl backdrop-blur-md"
            >
              <div className="relative flex items-center justify-center h-48 w-48 rounded-2xl bg-gradient-to-br from-brand-600/30 to-purple-600/30 border border-brand-500/30">
                <ShieldCheck className="h-24 w-24 text-brand-400 stroke-[1.25]" />
              </div>
              
              {/* Animated small indicator badges orbiting */}
              <div className="absolute -top-3 -right-3 flex items-center gap-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 px-3 py-1.5 text-xs text-emerald-400 font-bold shadow-lg">
                <CheckCircle className="h-3.5 w-3.5 fill-emerald-500/20" />
                <span>SSL Verified</span>
              </div>
              
              <div className="absolute -bottom-3 -left-3 flex items-center gap-1.5 rounded-lg bg-red-500/10 border border-red-500/30 px-3 py-1.5 text-xs text-red-400 font-bold shadow-lg">
                <ShieldAlert className="h-3.5 w-3.5 fill-red-500/20" />
                <span>Scam Flagged</span>
              </div>
            </motion.div>
          </div>
        </motion.div>

        {/* Feature Cards Grid Section */}
        <section id="features" className="pt-32 pb-8">
          <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
            <h2 className="text-xs uppercase tracking-widest font-black text-brand-500">Key Pillars</h2>
            <p className="text-3xl sm:text-4xl font-extrabold text-white">Multi-Source Verification & AI Intelligence</p>
            <p className="text-sm text-slate-400">
              Unlike generic chatbots, RecruitSafe runs a rigorous multi-factor check combining rule engines with cybersecurity heuristics.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800/40 hover:border-slate-800 hover:bg-slate-900/60 transition-all group">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-brand-500/10 border border-brand-500/20 text-brand-400 mb-6 group-hover:scale-105 transition-transform">
                <Layers className="h-5 w-5" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Multi-Input Analysis</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Paste raw job descriptions, upload offer letter PDFs, screenshots, recruiter emails, or paste corporate website URLs.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800/40 hover:border-slate-800 hover:bg-slate-900/60 transition-all group">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-brand-500/10 border border-brand-500/20 text-brand-400 mb-6 group-hover:scale-105 transition-transform">
                <Sparkles className="h-5 w-5" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">AI-Powered Detection</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Gemini API provides explainable natural language reasoning, job summarization, red flag tagging, and custom security recommendations.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800/40 hover:border-slate-800 hover:bg-slate-900/60 transition-all group">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-brand-500/10 border border-brand-500/20 text-brand-400 mb-6 group-hover:scale-105 transition-transform">
                <Globe className="h-5 w-5" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Website Intelligence</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Queries domain registration age via WHOIS servers, validates SSL certificate chains, redirects, and meta definitions.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800/40 hover:border-slate-800 hover:bg-slate-900/60 transition-all group">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-brand-500/10 border border-brand-500/20 text-brand-400 mb-6 group-hover:scale-105 transition-transform">
                <Mail className="h-5 w-5" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Email Verification</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Scans email header domains, matches recruiter address vs official company site domain, and filters disposable or free mail services.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800/40 hover:border-slate-800 hover:bg-slate-900/60 transition-all group">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-brand-500/10 border border-brand-500/20 text-brand-400 mb-6 group-hover:scale-105 transition-transform">
                <FileLock className="h-5 w-5" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Privacy-First Architecture</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                All uploaded images and PDFs are used solely for text extraction and immediately deleted from local disk after execution.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800/40 hover:border-slate-800 hover:bg-slate-900/60 transition-all group">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-brand-500/10 border border-brand-500/20 text-brand-400 mb-6 group-hover:scale-105 transition-transform">
                <FileText className="h-5 w-5" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Detailed Report Downloads</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Generate professional PDF analysis reports incorporating trust scores, scam probabilities, and breakdown logs to save and share.
              </p>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-darkbg-950/60 border-t border-slate-850/40 py-8 text-center text-xs text-slate-500 relative z-10">
        <p>&copy; {new Date().getFullYear()} RecruitSafe Platform. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default LandingPage;
