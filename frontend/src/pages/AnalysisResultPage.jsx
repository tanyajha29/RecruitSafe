import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../services/api';
import Layout from '../components/common/Layout';
import { 
  ShieldCheck, 
  ShieldAlert, 
  AlertTriangle, 
  ArrowLeft, 
  Download, 
  Trash2, 
  FileText, 
  Clock, 
  CheckCircle,
  ChevronDown,
  ChevronUp,
  Cpu,
  Fingerprint,
  Globe,
  Mail,
  Calendar,
  Check
} from 'lucide-react';

const AnalysisResultPage = () => {
  const { id: analysisId } = useParams();
  const navigate = useNavigate();
  
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Accordion toggle states
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(true);
  const [showWebsiteDetails, setShowWebsiteDetails] = useState(false);
  const [showEmailDetails, setShowEmailDetails] = useState(false);
  const [showTrace, setShowTrace] = useState(false);
  
  // Recommendations checked status state (for user interactive checklist)
  const [checkedRecommendations, setCheckedRecommendations] = useState({});

  const fetchAnalysisDetails = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get(`/api/analyze/${analysisId}`);
      setAnalysis(response.data);
    } catch (err) {
      console.error(err);
      setError('Could not retrieve job analysis details. It may have been deleted or doesn\'t exist.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalysisDetails();
  }, [analysisId]);

  const handleDownloadPDF = async () => {
    if (!analysis) return;
    try {
      const response = await api.get(`/api/report/${analysisId}`, {
        responseType: 'blob',
      });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = `RecruitSafe_Report_${analysisId}.pdf`;
      link.click();
    } catch (err) {
      console.error('PDF download failed:', err);
      alert('Failed to generate/download the PDF report document. Please try again.');
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to permanently delete this scan from your history? This action cannot be undone.')) {
      return;
    }
    try {
      await api.delete(`/api/analyze/${analysisId}`);
      navigate('/dashboard');
    } catch (err) {
      console.error('Delete failed:', err);
      alert('Failed to delete this report. Please try again.');
    }
  };

  const toggleRecommendation = (index) => {
    setCheckedRecommendations((prev) => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const getRiskCategoryStyles = (category) => {
    switch (category) {
      case 'Safe':
        return {
          bg: 'bg-emerald-50 dark:bg-emerald-950/30 border-emerald-100 dark:border-emerald-900/50 text-emerald-600 dark:text-emerald-400',
          text: 'text-emerald-500 dark:text-emerald-400',
          stroke: '#10B981',
          shadow: 'shadow-emerald-500/10'
        };
      case 'Needs Verification':
        return {
          bg: 'bg-amber-50 dark:bg-amber-950/30 border-amber-100 dark:border-amber-900/50 text-amber-605 dark:text-amber-400',
          text: 'text-amber-500 dark:text-amber-400',
          stroke: '#F59E0B',
          shadow: 'shadow-amber-500/10'
        };
      case 'Suspicious':
        return {
          bg: 'bg-orange-50 dark:bg-orange-950/30 border-orange-100 dark:border-orange-900/50 text-orange-600 dark:text-orange-400',
          text: 'text-orange-500 dark:text-orange-400',
          stroke: '#F97316',
          shadow: 'shadow-orange-500/10'
        };
      case 'High Risk':
        return {
          bg: 'bg-red-50 dark:bg-red-955/30 border-red-105 dark:border-red-900/50 text-red-600 dark:text-red-400',
          text: 'text-red-500 dark:text-red-400',
          stroke: '#EF4444',
          shadow: 'shadow-red-500/10'
        };
      default:
        return {
          bg: 'bg-slate-50 dark:bg-slate-800/40 border-slate-105 dark:border-slate-800/50 text-slate-500 dark:text-slate-405',
          text: 'text-slate-400 dark:text-slate-500',
          stroke: '#64748B',
          shadow: 'shadow-slate-500/10'
        };
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'high': return 'text-red-650 dark:text-red-400 bg-red-55/40 dark:bg-red-955/20 border-red-100 dark:border-red-900/40';
      case 'medium': return 'text-orange-600 dark:text-orange-405 bg-orange-50 dark:bg-orange-955/20 border-orange-100 dark:border-orange-900/40';
      case 'low': return 'text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-800/40 border-slate-100 dark:border-slate-800/50';
      default: return 'text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-800/40 border-slate-100 dark:border-slate-800/50';
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="space-y-8 max-w-6xl mx-auto">
          <div className="h-10 w-full rounded-xl animate-shimmer"></div>
          <div className="h-48 w-full rounded-2xl animate-shimmer"></div>
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div className="lg:col-span-8 space-y-6">
              <div className="h-32 rounded-2xl animate-shimmer"></div>
              <div className="h-64 rounded-2xl animate-shimmer"></div>
            </div>
            <div className="lg:col-span-4 h-96 rounded-2xl animate-shimmer"></div>
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <motion.div 
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-md mx-auto py-16 flex flex-col items-center justify-center text-center space-y-4"
        >
          <AlertTriangle className="h-12 w-12 text-red-500 animate-pulse" />
          <h3 className="text-lg font-bold text-slate-850 dark:text-slate-100">Report Unavailable</h3>
          <p className="text-slate-500 dark:text-slate-400 text-sm leading-relaxed">{error}</p>
          <Link
            to="/dashboard"
            className="flex items-center gap-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-bold text-xs px-5 py-3 transition-colors cursor-pointer"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Dashboard</span>
          </Link>
        </motion.div>
      </Layout>
    );
  }

  const riskStyles = getRiskCategoryStyles(analysis?.risk_category);

  return (
    <Layout>
      <div className="space-y-8 max-w-6xl mx-auto">
        
        {/* Navigation Action Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <Link
            to="/history"
            className="flex items-center gap-1.5 text-xs font-bold text-slate-400 dark:text-slate-550 hover:text-slate-700 dark:hover:text-slate-350 transition-colors"
          >
            <ArrowLeft className="h-4.5 w-4.5" />
            <span>Back to History</span>
          </Link>
          
          <div className="flex items-center gap-3.5 w-full sm:w-auto">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleDownloadPDF}
              className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 rounded-xl border border-slate-205 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-slate-350 dark:hover:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-705 dark:text-slate-300 font-bold text-xs px-4.5 py-3 transition-colors cursor-pointer"
            >
              <Download className="h-4 w-4 text-slate-500 dark:text-slate-400" />
              <span>Export PDF Audit</span>
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleDelete}
              className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 rounded-xl border border-red-200 dark:border-red-950 bg-red-50/20 dark:bg-red-955/10 hover:bg-red-50 dark:hover:bg-red-900/20 hover:border-red-300 dark:hover:border-red-900 text-red-650 dark:text-red-400 font-bold text-xs px-4.5 py-3 transition-colors cursor-pointer"
            >
              <Trash2 className="h-4 w-4" />
              <span>Delete Scan</span>
            </motion.button>
          </div>
        </div>

        {/* Top Summary Card */}
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45 }}
          className="rounded-2xl bg-white dark:bg-slate-900 p-6 md:p-8 shadow-sm border border-slate-200/80 dark:border-slate-800/80 grid grid-cols-1 md:grid-cols-12 gap-8 items-center transition-colors duration-300"
        >
          {/* Circular Gauge */}
          <div className="md:col-span-4 flex justify-center relative">
            <svg width="170" height="170" viewBox="0 0 100 100" className="transform -rotate-90">
              <circle cx="50" cy="50" r="42" fill="transparent" stroke="#F1F5F9" strokeWidth="7" className="dark:stroke-slate-800" />
              <motion.circle
                cx="50"
                cy="50"
                r="42"
                fill="transparent"
                stroke={riskStyles.stroke}
                strokeWidth="7.5"
                strokeLinecap="round"
                strokeDasharray={`${2 * Math.PI * 42}`}
                initial={{ strokeDashoffset: 2 * Math.PI * 42 }}
                animate={{ strokeDashoffset: (2 * Math.PI * 42) * (1 - (analysis?.trust_score || 0) / 100) }}
                transition={{ duration: 1.0, ease: 'easeOut' }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
              <span className="text-4xl font-black text-slate-850 dark:text-white tracking-tight">{analysis?.trust_score}</span>
              <span className="text-[9px] text-slate-400 dark:text-slate-500 font-bold uppercase tracking-wider mt-0.5">Trust Score</span>
            </div>
          </div>

          {/* Core Metrics Summary */}
          <div className="md:col-span-8 space-y-5 text-center md:text-left">
            <div>
              <span className={`inline-flex items-center rounded-full border px-3.5 py-1 text-[10px] font-black uppercase tracking-wider ${riskStyles.bg}`}>
                {analysis?.risk_category} Verdict
              </span>
              <h2 className="text-2xl font-black text-slate-850 dark:text-slate-100 tracking-tight mt-3">Job Legitimacy Audit</h2>
              
              <div className="flex flex-wrap items-center justify-center md:justify-start gap-y-1.5 gap-x-3.5 text-xs text-slate-450 dark:text-slate-500 font-bold mt-2">
                <span className="flex items-center gap-1"><FileText className="h-3.5 w-3.5" /> Source: {analysis?.input_type}</span>
                <span className="h-1 w-1 rounded-full bg-slate-300 dark:bg-slate-700 hidden sm:inline"></span>
                <span className="flex items-center gap-1"><Calendar className="h-3.5 w-3.5" /> Checked: {new Date(analysis?.created_at).toLocaleDateString()}</span>
                <span className="h-1 w-1 rounded-full bg-slate-300 dark:bg-slate-700 hidden sm:inline"></span>
                <span className="flex items-center gap-1"><Clock className="h-3.5 w-3.5" /> Probability: {analysis?.scam_probability}%</span>
              </div>
            </div>

            {/* V2.1 Score Indicators */}
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-slate-50 dark:bg-slate-850/45 border border-slate-100 dark:border-slate-800/60 rounded-2xl p-3 text-center">
                <p className="text-[9px] text-slate-455 dark:text-slate-500 font-black uppercase tracking-wider">Confidence</p>
                <p className="text-base font-black text-slate-800 dark:text-slate-205 mt-0.5">{analysis?.confidence_score ?? '100'}%</p>
              </div>
              <div className="bg-slate-50 dark:bg-slate-850/45 border border-slate-100 dark:border-slate-800/60 rounded-2xl p-3 text-center">
                <p className="text-[9px] text-slate-455 dark:text-slate-500 font-black uppercase tracking-wider">Input Quality</p>
                <p className="text-base font-black text-slate-800 dark:text-slate-205 mt-0.5">{analysis?.input_quality_score ?? '100'}/100</p>
              </div>
              <div className="bg-slate-50 dark:bg-slate-850/45 border border-slate-100 dark:border-slate-800/60 rounded-2xl p-3 text-center">
                <p className="text-[9px] text-slate-455 dark:text-slate-500 font-black uppercase tracking-wider">AI consensus</p>
                <p className="text-base font-black text-slate-800 dark:text-slate-205 mt-0.5">{analysis?.agreement_score ?? '100'}%</p>
              </div>
            </div>

            {/* Scanned Source Block snippet */}
            <div className="bg-slate-50 dark:bg-slate-850/45 border border-slate-100 dark:border-slate-800/60 rounded-2xl p-3.5 text-left">
              <p className="text-[10px] text-slate-450 dark:text-slate-500 font-black uppercase tracking-wider">Scanned Snippet</p>
              <p className="text-xs font-semibold text-slate-700 dark:text-slate-350 mt-1 line-clamp-1">
                {analysis?.original_content || "Text Input Block"}
              </p>
            </div>
          </div>
        </motion.div>

        {/* Detailed Core Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Left Column: AI Reasoning and Evidence checklists */}
          <div className="lg:col-span-8 space-y-8">

            {/* Verification Status Footprint Panel */}
            <motion.div 
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, delay: 0.05 }}
              className="rounded-2xl bg-white dark:bg-slate-900 p-6 md:p-8 shadow-sm border border-slate-200/80 dark:border-slate-800/80 space-y-6 transition-colors duration-300"
            >
              <div className="flex items-center gap-2 text-indigo-600 dark:text-indigo-400 pb-4 border-b border-slate-100 dark:border-slate-800/80">
                <ShieldCheck className="h-5.5 w-5.5" />
                <h3 className="text-base font-bold text-slate-855 dark:text-slate-100">Employer Footprint Verification Status</h3>
              </div>
              
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3.5">
                {analysis?.verification_status ? (
                  Object.entries(analysis.verification_status).map(([key, state]) => {
                    const stateUpper = state.toUpperCase();
                    let pillColor = 'bg-slate-50 dark:bg-slate-850 text-slate-650 dark:text-slate-400 border-slate-200 dark:border-slate-800';
                    if (['VERIFIED', 'VALID', 'REACHABLE', 'VALID HTTPS'].includes(stateUpper)) {
                      pillColor = 'bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400 border-emerald-100 dark:border-emerald-900/40';
                    } else if (['PARTIALLY VERIFIED', 'DETECTED BUT NOT VERIFIED'].includes(stateUpper)) {
                      pillColor = 'bg-amber-50 dark:bg-amber-950/20 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-900/40';
                    } else if (['INVALID', 'UNREACHABLE', 'NOT FOUND', 'DISPOSABLE EMAIL'].includes(stateUpper)) {
                      pillColor = 'bg-red-50 dark:bg-red-950/20 text-red-650 dark:text-red-400 border-red-100 dark:border-red-900/40';
                    } else if (['UNKNOWN', 'FREE EMAIL', 'NOT PRESENT'].includes(stateUpper)) {
                      pillColor = 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-500 border-slate-200 dark:border-slate-700/60';
                    }

                    return (
                      <div key={key} className="flex flex-col p-3 rounded-2xl border border-slate-150 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-850/20 justify-between items-center text-center space-y-2">
                        <p className="text-[9px] font-black text-slate-400 dark:text-slate-550 truncate max-w-full">{key}</p>
                        <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[8px] font-black uppercase tracking-wide leading-none ${pillColor}`}>
                          {state}
                        </span>
                      </div>
                    );
                  })
                ) : (
                  <p className="col-span-5 text-center text-slate-400 text-xs py-4">No verification footprint details available.</p>
                )}
              </div>
            </motion.div>
            
            {/* AI Summary and Explanation */}
            <motion.div 
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, delay: 0.1 }}
              className="rounded-2xl bg-white dark:bg-slate-900 p-6 md:p-8 shadow-sm border border-slate-200/80 dark:border-slate-800/80 space-y-6 transition-colors duration-300"
            >
              <div className="flex items-center gap-2 text-indigo-600 dark:text-indigo-400 pb-4 border-b border-slate-105 dark:border-slate-800/80">
                <Cpu className="h-5.5 w-5.5" />
                <h3 className="text-base font-bold text-slate-855 dark:text-slate-100">AI Reasoning Output</h3>
              </div>

              <div className="space-y-5">
                <div>
                  <h4 className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Executive Summary</h4>
                  <p className="text-sm font-semibold text-slate-700 dark:text-slate-300 leading-relaxed mt-1.5">
                    {analysis?.ai_summary || "Analyzing details..."}
                  </p>
                </div>

                <div>
                  <h4 className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Consensus Alignment Explanation</h4>
                  <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mt-1.5">
                    {analysis?.agreement_explanation || "Consensus details being evaluated..."}
                  </p>
                </div>

                <div>
                  <h4 className="text-xs font-bold text-slate-400 dark:text-slate-550 uppercase tracking-wider">Semantic Risk Explanation</h4>
                  <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mt-1.5">
                    {analysis?.risk_explanation || "Generating explanation..."}
                  </p>
                </div>
              </div>
            </motion.div>

            {/* Technical scan evidence list Accordion */}
            <motion.div 
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, delay: 0.15 }}
              className="rounded-2xl bg-white dark:bg-slate-900 p-6 md:p-8 shadow-sm border border-slate-200/80 dark:border-slate-800/80 space-y-6 transition-colors duration-300"
            >
              <button
                onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
                className="flex items-center justify-between w-full text-left pb-4 border-b border-slate-100 dark:border-slate-800/80 cursor-pointer"
              >
                <div className="flex items-center gap-2 text-indigo-600 dark:text-indigo-400">
                  <Fingerprint className="h-5.5 w-5.5" />
                  <h3 className="text-base font-bold text-slate-855 dark:text-slate-100">Technical Evidence & Indicators</h3>
                </div>
                {showTechnicalDetails ? <ChevronUp className="h-5 w-5 text-slate-400 dark:text-slate-500" /> : <ChevronDown className="h-5 w-5 text-slate-400 dark:text-slate-500" />}
              </button>

              <AnimatePresence>
                {showTechnicalDetails && (
                  <motion.div 
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="space-y-4 pt-2 overflow-hidden"
                  >
                    {analysis?.evidence.length === 0 ? (
                      <p className="text-slate-400 dark:text-slate-500 text-sm font-semibold text-center py-8">
                        No rule violations or domain anomalies triggered in this scan.
                      </p>
                    ) : (
                      <div className="space-y-3.5">
                        {analysis?.evidence.map((item, index) => (
                          <div key={index} className="rounded-2xl border border-slate-200/60 dark:border-slate-805 p-4 space-y-2 bg-white dark:bg-slate-900/50">
                            <div className="flex items-start justify-between gap-4">
                              <h4 className="text-sm font-extrabold text-slate-800 dark:text-slate-200">{item.factor_name}</h4>
                              <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[9px] font-black uppercase tracking-wider shrink-0 ${getSeverityColor(item.severity)}`}>
                                {item.severity} severity
                              </span>
                            </div>
                            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{item.description}</p>
                            <p className="text-[10px] text-slate-405 dark:text-slate-500 font-bold uppercase tracking-wider mt-1">
                              Deduction: {item.points_deducted === 0 ? '0 (Informational)' : `-${item.points_deducted} points`}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Website metadata Details accordion */}
            {analysis?.website_data && (
              <motion.div 
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.45, delay: 0.2 }}
                className="rounded-2xl bg-white dark:bg-slate-900 p-6 md:p-8 shadow-sm border border-slate-200/80 dark:border-slate-800/80 space-y-6 transition-colors duration-300"
              >
                <button
                  onClick={() => setShowWebsiteDetails(!showWebsiteDetails)}
                  className="flex items-center justify-between w-full text-left pb-4 border-b border-slate-105 dark:border-slate-800/80 cursor-pointer"
                >
                  <div className="flex items-center gap-2 text-indigo-600 dark:text-indigo-400">
                    <Globe className="h-5.5 w-5.5" />
                    <h3 className="text-base font-bold text-slate-855 dark:text-slate-100">Domain & SSL Metadata</h3>
                  </div>
                  {showWebsiteDetails ? <ChevronUp className="h-5 w-5 text-slate-400 dark:text-slate-500" /> : <ChevronDown className="h-5 w-5 text-slate-400 dark:text-slate-500" />}
                </button>

                <AnimatePresence>
                  {showWebsiteDetails && (
                    <motion.div 
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2 text-sm leading-relaxed overflow-hidden"
                    >
                      <div className="space-y-3">
                        <h4 className="text-xs font-bold text-slate-400 dark:text-slate-550 uppercase tracking-wider">Domain Registration</h4>
                        
                        {analysis.website_data.whois?.whois_failed ? (
                          <p className="text-slate-400 dark:text-slate-500 text-xs font-semibold">WHOIS record lookup failed or domain registration metadata unavailable.</p>
                        ) : (
                          <div className="space-y-2 text-xs">
                            <p className="text-slate-500 dark:text-slate-400 font-semibold">
                              Age: <span className="font-bold text-slate-800 dark:text-slate-200">{analysis.website_data.whois?.domain_age_days ?? 'Unknown'} days</span>
                            </p>
                            <p className="text-slate-505 dark:text-slate-400 font-semibold">
                              Registrar: <span className="font-bold text-slate-800 dark:text-slate-200 truncate block max-w-xs">{analysis.website_data.whois?.registrar ?? 'Unknown'}</span>
                            </p>
                            <p className="text-slate-505 dark:text-slate-400 font-semibold">
                              Registered: <span className="font-bold text-slate-800 dark:text-slate-205">
                                {analysis.website_data.whois?.registration_date ? new Date(analysis.website_data.whois.registration_date).toLocaleDateString() : 'Unknown'}
                              </span>
                            </p>
                            <p className="text-slate-505 dark:text-slate-400 font-semibold">
                              Country: <span className="font-bold text-slate-800 dark:text-slate-200">{analysis.website_data.whois?.country ?? 'Unknown'}</span>
                            </p>
                          </div>
                        )}
                      </div>

                      {/* SSL Certificates */}
                      <div className="space-y-3">
                        <h4 className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">SSL Security</h4>
                        <div className="space-y-2 text-xs">
                          <p className="text-slate-505 dark:text-slate-400 font-semibold flex items-center gap-1.5">
                            SSL Connection: 
                            <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[9px] font-bold ${
                              analysis.website_data.ssl?.has_valid_ssl 
                                ? 'bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-405 border border-emerald-100 dark:border-emerald-900/40' 
                                : 'bg-red-50 dark:bg-red-950/20 text-red-655 dark:text-red-400 border border-red-100 dark:border-red-900/40'
                            }`}>
                              {analysis.website_data.ssl?.has_valid_ssl ? 'Valid HTTPS' : 'Missing SSL / HTTP'}
                            </span>
                          </p>
                          <p className="text-slate-505 dark:text-slate-405 font-semibold">
                            Issuer: <span className="font-bold text-slate-800 dark:text-slate-200 truncate block max-w-xs">{analysis.website_data.ssl?.issuer ?? 'Unknown'}</span>
                          </p>
                          <p className="text-slate-505 dark:text-slate-405 font-semibold">
                            Expires: <span className="font-bold text-slate-800 dark:text-slate-205">
                              {analysis.website_data.ssl?.expiration_date ? new Date(analysis.website_data.ssl.expiration_date).toLocaleDateString() : 'Unknown'}
                            </span>
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )}

            {/* Email details Accordion */}
            {analysis?.email_data && (
              <motion.div 
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.45, delay: 0.25 }}
                className="rounded-2xl bg-white dark:bg-slate-900 p-6 md:p-8 shadow-sm border border-slate-200/80 dark:border-slate-800/80 space-y-6 transition-colors duration-300"
              >
                <button
                  onClick={() => setShowEmailDetails(!showEmailDetails)}
                  className="flex items-center justify-between w-full text-left pb-4 border-b border-slate-100 dark:border-slate-800/80 cursor-pointer"
                >
                  <div className="flex items-center gap-2 text-indigo-600 dark:text-indigo-400">
                    <Mail className="h-5.5 w-5.5" />
                    <h3 className="text-base font-bold text-slate-855 dark:text-slate-100">Recruiter Email Validation</h3>
                  </div>
                  {showEmailDetails ? <ChevronUp className="h-5 w-5 text-slate-400 dark:text-slate-550" /> : <ChevronDown className="h-5 w-5 text-slate-400 dark:text-slate-550" />}
                </button>

                <AnimatePresence>
                  {showEmailDetails && (
                    <motion.div 
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2 text-sm leading-relaxed overflow-hidden"
                    >
                      <div className="space-y-3">
                        <h4 className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Email Sender Checks</h4>
                        <div className="space-y-2 text-xs text-slate-505 dark:text-slate-400 font-semibold">
                          <p>Address: <span className="font-bold text-slate-800 dark:text-slate-200">{analysis.email_data.sender_email}</span></p>
                          <p className="flex items-center gap-1.5">
                            DNS Domain Check: 
                            <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[9px] font-bold ${
                              analysis.email_data.domain_exists 
                                ? 'bg-emerald-50 dark:bg-emerald-950/20 text-emerald-650 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-900/40' 
                                : 'bg-red-50 dark:bg-red-955/20 text-red-600 dark:text-red-400 border border-red-100 dark:border-red-900/40'
                            }`}>
                              {analysis.email_data.domain_exists ? 'Domain Exists' : 'Dead Domain / Fake'}
                            </span>
                          </p>
                          <p className="flex items-center gap-1.5">
                            Mail Server Domain: 
                            <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[9px] font-bold ${
                              analysis.email_data.is_free_email 
                                ? 'bg-orange-55 dark:bg-orange-950/20 text-orange-600 dark:text-orange-400 border border-orange-100 dark:border-indigo-900/40' 
                                : (analysis.email_data.is_disposable ? 'bg-red-50 dark:bg-red-955/20 text-red-600 dark:text-red-400 border border-red-100 dark:border-red-900/40' : 'bg-slate-55 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border border-slate-105 dark:border-slate-700/60')
                            }`}>
                              {analysis.email_data.is_free_email ? 'Free Public Domain' : (analysis.email_data.is_disposable ? 'Disposable Mail' : 'Corporate Mail')}
                            </span>
                          </p>
                        </div>
                      </div>

                      {analysis.email_data.typosquatting_check && (
                        <div className="space-y-3">
                          <h4 className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Typosquatting Check</h4>
                          <div className="space-y-2 text-xs text-slate-500 dark:text-slate-405 font-semibold">
                            <p className="flex items-center gap-1.5">
                              Similarity Match: 
                              <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[9px] font-bold ${
                                analysis.email_data.typosquatting_check.is_exact_match 
                                  ? 'bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-900/40' 
                                  : (analysis.email_data.typosquatting_check.is_suspicious_typosquatting ? 'bg-red-50 dark:bg-red-955/20 text-red-600 dark:text-red-400 border border-red-100 dark:border-red-900/40' : 'bg-orange-50 dark:bg-orange-950/20 text-orange-605 dark:text-orange-400 border border-orange-105 dark:border-orange-900/40')
                              }`}>
                                {analysis.email_data.typosquatting_check.is_exact_match ? 'Exact Match' : (analysis.email_data.typosquatting_check.is_suspicious_typosquatting ? 'Suspicious Lookalike' : 'Domain Mismatch')}
                              </span>
                            </p>
                            {analysis.email_data.typosquatting_check.reason && (
                              <p className="text-slate-600 dark:text-slate-400 italic bg-slate-50 dark:bg-slate-850/50 p-2.5 rounded-xl border border-slate-100 dark:border-slate-800/80 mt-2 font-medium">
                                {analysis.email_data.typosquatting_check.reason}
                              </p>
                            )}
                          </div>
                        </div>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )}

            {/* Developer Decision Trace */}
            {analysis?.decision_trace && analysis.decision_trace.length > 0 && (
              <motion.div 
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.45, delay: 0.3 }}
                className="rounded-2xl bg-white dark:bg-slate-900 p-6 shadow-sm border border-slate-200/80 dark:border-slate-800/80 space-y-4 transition-colors duration-300"
              >
                <button 
                  onClick={() => setShowTrace(!showTrace)}
                  className="flex items-center justify-between w-full pb-3 border-b border-slate-100 dark:border-slate-850 cursor-pointer"
                >
                  <div className="flex items-center gap-2 text-slate-500">
                    <Cpu className="h-5 w-5" />
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-350">Developer Decision Trace</h4>
                  </div>
                  {showTrace ? <ChevronUp className="h-4.5 w-4.5 text-slate-400" /> : <ChevronDown className="h-4.5 w-4.5 text-slate-400" />}
                </button>
                
                <AnimatePresence>
                  {showTrace && (
                    <motion.div 
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="bg-slate-950 dark:bg-black rounded-xl p-4 font-mono text-[10px] text-emerald-400 space-y-1.5 overflow-x-auto max-h-60"
                    >
                      {analysis.decision_trace.map((step, idx) => (
                        <div key={idx} className="flex gap-2">
                          <span className="text-slate-505 select-none">[{idx + 1}]</span>
                          <span>{step}</span>
                        </div>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )}

          </div>

          {/* Right Column: Diligence Checklist */}
          <div className="lg:col-span-4 space-y-6">
            <motion.div 
              initial={{ opacity: 0, x: 15 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.45, delay: 0.2 }}
              className="rounded-2xl bg-white dark:bg-slate-900 p-6 shadow-sm border border-slate-200/80 dark:border-slate-800/80 transition-colors duration-300"
            >
              <h3 className="text-base font-bold text-slate-855 dark:text-slate-100 mb-4 pb-3 border-b border-slate-50 dark:border-slate-800">Diligence Checklist</h3>
              <p className="text-[10px] text-slate-400 dark:text-slate-505 font-semibold mb-6">
                Perform these verified security checks before sending personal documents or payments. Check them off as you go.
              </p>

              {analysis?.recommendations.length === 0 ? (
                <p className="text-slate-455 dark:text-slate-500 text-xs font-semibold text-center py-4">No recommendations generated.</p>
              ) : (
                <div className="space-y-4">
                  {analysis?.recommendations.map((item, index) => {
                    const isChecked = !!checkedRecommendations[index];
                    return (
                      <div 
                        key={index} 
                        onClick={() => toggleRecommendation(index)}
                        className={`flex items-start gap-3 p-3.5 rounded-xl border transition-all cursor-pointer ${
                          isChecked 
                            ? 'bg-slate-50/50 dark:bg-slate-950/20 border-slate-200/80 dark:border-slate-800/80 opacity-70' 
                            : 'bg-white dark:bg-slate-900/60 border-slate-100 dark:border-slate-800 hover:border-slate-200 dark:hover:border-slate-700'
                        }`}
                      >
                        <button
                          type="button"
                          className={`h-5 w-5 rounded border flex items-center justify-center shrink-0 mt-0.5 transition-colors cursor-pointer ${
                            isChecked 
                              ? 'bg-indigo-650 border-indigo-650 text-white' 
                              : 'border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 hover:border-indigo-500'
                          }`}
                        >
                          {isChecked && <Check className="h-3.5 w-3.5 stroke-[3]" />}
                        </button>
                        <span className={`text-xs font-semibold leading-relaxed select-none ${
                          isChecked ? 'line-through text-slate-400 dark:text-slate-500 font-semibold' : 'text-slate-700 dark:text-slate-300'
                        }`}>
                          {item}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </motion.div>
          </div>

        </div>

      </div>
    </Layout>
  );
};

export default AnalysisResultPage;
