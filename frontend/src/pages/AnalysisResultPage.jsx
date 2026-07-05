import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
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
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Cpu,
  Fingerprint,
  Globe,
  Mail
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
      // Create download link
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
          bg: 'bg-emerald-50 border-emerald-100 text-emerald-600',
          text: 'text-emerald-500',
          stroke: '#10B981',
          shadow: 'shadow-emerald-550/15'
        };
      case 'Needs Verification':
        return {
          bg: 'bg-yellow-50 border-yellow-100 text-yellow-600',
          text: 'text-yellow-500',
          stroke: '#EAB308',
          shadow: 'shadow-yellow-550/15'
        };
      case 'Suspicious':
        return {
          bg: 'bg-orange-50 border-orange-100 text-orange-600',
          text: 'text-orange-500',
          stroke: '#F97316',
          shadow: 'shadow-orange-550/15'
        };
      case 'High Risk':
        return {
          bg: 'bg-red-50 border-red-100 text-red-600',
          text: 'text-red-500',
          stroke: '#EF4444',
          shadow: 'shadow-red-550/15'
        };
      default:
        return {
          bg: 'bg-slate-50 border-slate-100 text-slate-500',
          text: 'text-slate-400',
          stroke: '#64748B',
          shadow: 'shadow-slate-550/10'
        };
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'high': return 'text-red-500 bg-red-50 border-red-100';
      case 'medium': return 'text-orange-500 bg-orange-50 border-orange-100';
      case 'low': return 'text-slate-500 bg-slate-50 border-slate-100';
      default: return 'text-slate-500 bg-slate-50 border-slate-100';
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex h-96 w-full items-center justify-center">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-brand-500 border-t-transparent"></div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="max-w-md mx-auto py-12 flex flex-col items-center justify-center text-center space-y-4">
          <AlertTriangle className="h-12 w-12 text-red-500" />
          <h3 className="text-lg font-bold text-slate-800">Report Unavailable</h3>
          <p className="text-slate-550 text-sm leading-relaxed">{error}</p>
          <Link
            to="/dashboard"
            className="flex items-center gap-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs px-4 py-2.5 transition-colors cursor-pointer"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Dashboard</span>
          </Link>
        </div>
      </Layout>
    );
  }

  const riskStyles = getRiskCategoryStyles(analysis?.risk_category);
  const totalDeductions = 100 - (analysis?.trust_score || 0);

  return (
    <Layout>
      <div className="space-y-8 max-w-6xl mx-auto">
        
        {/* Navigation Action Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <Link
            to="/history"
            className="flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-slate-700 transition-colors"
          >
            <ArrowLeft className="h-4.5 w-4.5" />
            <span>Back to History</span>
          </Link>
          
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <button
              onClick={handleDownloadPDF}
              className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 rounded-lg border border-slate-200 bg-white hover:border-slate-350 hover:bg-slate-50 text-slate-700 font-bold text-xs px-4 py-2.5 transition-all cursor-pointer"
            >
              <Download className="h-4 w-4 text-slate-500" />
              <span>Export PDF Audit</span>
            </button>
            <button
              onClick={handleDelete}
              className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 rounded-lg border border-red-200 bg-red-50/20 hover:bg-red-50 hover:border-red-300 text-red-600 font-bold text-xs px-4 py-2.5 transition-all cursor-pointer"
            >
              <Trash2 className="h-4 w-4" />
              <span>Delete Scan</span>
            </button>
          </div>
        </div>

        {/* Top Summary Card (Trust score, gauge, metadata) */}
        <div className="rounded-2xl bg-white p-6 md:p-8 shadow-sm border border-slate-200/80 grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
          {/* Circular Gauge */}
          <div className="md:col-span-4 flex justify-center relative">
            <svg width="160" height="160" viewBox="0 0 100 100" className="transform -rotate-90">
              <circle cx="50" cy="50" r="42" fill="transparent" stroke="#F1F5F9" strokeWidth="8" />
              <motion.circle
                cx="50"
                cy="50"
                r="42"
                fill="transparent"
                stroke={riskStyles.stroke}
                strokeWidth="8"
                strokeDasharray={`${2 * Math.PI * 42}`}
                initial={{ strokeDashoffset: 2 * Math.PI * 42 }}
                animate={{ strokeDashoffset: (2 * Math.PI * 42) * (1 - (analysis?.trust_score || 0) / 100) }}
                transition={{ duration: 0.8, ease: 'easeOut' }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
              <p className="text-4xl font-black text-slate-800">{analysis?.trust_score}</p>
              <p className="text-[9px] text-slate-400 font-bold uppercase tracking-wider mt-0.5">Trust Score</p>
            </div>
          </div>

          {/* Core Metrics Summary */}
          <div className="md:col-span-8 space-y-4 text-center md:text-left">
            <div>
              <span className={`inline-flex items-center rounded-full border px-3 py-0.5 text-xs font-bold ${riskStyles.bg}`}>
                {analysis?.risk_category} Verdict
              </span>
              <h2 className="text-xl font-bold text-slate-800 mt-2">Job Legitimacy Audit</h2>
              <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider mt-1 flex items-center justify-center md:justify-start gap-3">
                <span>Format: {analysis?.input_type}</span>
                <span className="h-1.5 w-1.5 rounded-full bg-slate-300"></span>
                <span>Scam Probability: {analysis?.scam_probability}%</span>
              </p>
            </div>

            {/* Snippet box */}
            <div className="bg-slate-50 border border-slate-100 rounded-xl p-3 text-left">
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Scanned Content Source</p>
              <p className="text-xs font-medium text-slate-700 mt-1 truncate">
                {analysis?.original_content || "Text Input Block"}
              </p>
            </div>
          </div>
        </div>

        {/* Detailed Core Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Left Column: AI Reasoning and Evidence checklists */}
          <div className="lg:col-span-8 space-y-8">
            
            {/* AI Summary and Explanation */}
            <div className="rounded-2xl bg-white p-6 md:p-8 shadow-sm border border-slate-200/80 space-y-6">
              <div className="flex items-center gap-2 text-brand-600 pb-4 border-b border-slate-100">
                <Cpu className="h-5.5 w-5.5" />
                <h3 className="text-base font-bold text-slate-800">AI Reasoning Output</h3>
              </div>

              <div className="space-y-4">
                <div>
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Executive Summary</h4>
                  <p className="text-sm font-medium text-slate-700 leading-relaxed mt-1">
                    {analysis?.ai_summary || "Analyzing details..."}
                  </p>
                </div>

                <div>
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Semantic Risk Explanation</h4>
                  <p className="text-sm text-slate-655 leading-relaxed mt-1">
                    {analysis?.risk_explanation || "Generating explanation..."}
                  </p>
                </div>
              </div>
            </div>

            {/* Technical scan evidence list Accordion */}
            <div className="rounded-2xl bg-white p-6 md:p-8 shadow-sm border border-slate-200/80 space-y-6">
              <button
                onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
                className="flex items-center justify-between w-full text-left pb-4 border-b border-slate-100 cursor-pointer"
              >
                <div className="flex items-center gap-2 text-brand-600">
                  <Fingerprint className="h-5.5 w-5.5" />
                  <h3 className="text-base font-bold text-slate-800">Technical Evidence & Indicators</h3>
                </div>
                {showTechnicalDetails ? <ChevronUp className="h-5 w-5 text-slate-400" /> : <ChevronDown className="h-5 w-5 text-slate-400" />}
              </button>

              {showTechnicalDetails && (
                <div className="space-y-4 pt-2">
                  {analysis?.evidence.length === 0 ? (
                    <p className="text-slate-400 text-sm font-medium text-center py-6">
                      No rule violations or domain anomalies triggered in this scan.
                    </p>
                  ) : (
                    <div className="space-y-3">
                      {analysis?.evidence.map((item, index) => (
                        <div key={index} className="rounded-xl border border-slate-200/60 p-4 space-y-2">
                          <div className="flex items-start justify-between gap-4">
                            <h4 className="text-sm font-bold text-slate-800">{item.factor_name}</h4>
                            <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider shrink-0 ${getSeverityColor(item.severity)}`}>
                              {item.severity} severity
                            </span>
                          </div>
                          <p className="text-xs text-slate-500 leading-relaxed">{item.description}</p>
                          <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider mt-1">
                            Deduction: -{item.points_deducted} points
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Website metadata Details accordion (If website URL checked) */}
            {analysis?.website_data && (
              <div className="rounded-2xl bg-white p-6 md:p-8 shadow-sm border border-slate-200/80 space-y-6">
                <button
                  onClick={() => setShowWebsiteDetails(!showWebsiteDetails)}
                  className="flex items-center justify-between w-full text-left pb-4 border-b border-slate-100 cursor-pointer"
                >
                  <div className="flex items-center gap-2 text-brand-600">
                    <Globe className="h-5.5 w-5.5" />
                    <h3 className="text-base font-bold text-slate-800">Domain & SSL Metadata</h3>
                  </div>
                  {showWebsiteDetails ? <ChevronUp className="h-5 w-5 text-slate-400" /> : <ChevronDown className="h-5 w-5 text-slate-400" />}
                </button>

                {showWebsiteDetails && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2 text-sm leading-relaxed">
                    {/* Domain WHOIS */}
                    <div className="space-y-3">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Domain Registration</h4>
                      
                      {analysis.website_data.whois?.whois_failed ? (
                        <p className="text-slate-400 text-xs font-medium">WHOIS record lookup failed or domain is unregistered.</p>
                      ) : (
                        <div className="space-y-1.5 text-xs">
                          <p className="text-slate-500 font-medium">
                            Age: <span className="font-bold text-slate-800">{analysis.website_data.whois?.domain_age_days ?? 'Unknown'} days</span>
                          </p>
                          <p className="text-slate-500 font-medium">
                            Registrar: <span className="font-bold text-slate-800 truncate block max-w-xs">{analysis.website_data.whois?.registrar ?? 'Unknown'}</span>
                          </p>
                          <p className="text-slate-500 font-medium">
                            Registered: <span className="font-bold text-slate-800">
                              {analysis.website_data.whois?.registration_date ? new Date(analysis.website_data.whois.registration_date).toLocaleDateString() : 'Unknown'}
                            </span>
                          </p>
                          <p className="text-slate-500 font-medium">
                            Country: <span className="font-bold text-slate-800">{analysis.website_data.whois?.country ?? 'Unknown'}</span>
                          </p>
                        </div>
                      )}
                    </div>

                    {/* SSL Certificates */}
                    <div className="space-y-3">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">SSL Security</h4>
                      <div className="space-y-1.5 text-xs">
                        <p className="text-slate-500 font-medium flex items-center gap-1.5">
                          SSL Connection: 
                          <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-bold ${
                            analysis.website_data.ssl?.has_valid_ssl 
                              ? 'bg-emerald-50 text-emerald-600 border border-emerald-100' 
                              : 'bg-red-50 text-red-600 border border-red-100'
                          }`}>
                            {analysis.website_data.ssl?.has_valid_ssl ? 'Valid HTTPS' : 'Missing SSL / HTTP'}
                          </span>
                        </p>
                        <p className="text-slate-500 font-medium">
                          Issuer: <span className="font-bold text-slate-800 truncate block max-w-xs">{analysis.website_data.ssl?.issuer ?? 'Unknown'}</span>
                        </p>
                        <p className="text-slate-500 font-medium">
                          Expires: <span className="font-bold text-slate-800">
                            {analysis.website_data.ssl?.expiration_date ? new Date(analysis.website_data.ssl.expiration_date).toLocaleDateString() : 'Unknown'}
                          </span>
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Email details Accordion */}
            {analysis?.email_data && (
              <div className="rounded-2xl bg-white p-6 md:p-8 shadow-sm border border-slate-200/80 space-y-6">
                <button
                  onClick={() => setShowEmailDetails(!showEmailDetails)}
                  className="flex items-center justify-between w-full text-left pb-4 border-b border-slate-100 cursor-pointer"
                >
                  <div className="flex items-center gap-2 text-brand-600">
                    <Mail className="h-5.5 w-5.5" />
                    <h3 className="text-base font-bold text-slate-800">Recruiter Email Validation</h3>
                  </div>
                  {showEmailDetails ? <ChevronUp className="h-5 w-5 text-slate-400" /> : <ChevronDown className="h-5 w-5 text-slate-400" />}
                </button>

                {showEmailDetails && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2 text-sm leading-relaxed">
                    <div className="space-y-3">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Email Sender Checks</h4>
                      <div className="space-y-1.5 text-xs text-slate-500 font-medium">
                        <p>Address: <span className="font-bold text-slate-800">{analysis.email_data.sender_email}</span></p>
                        <p className="flex items-center gap-1.5">
                          DNS Domain Check: 
                          <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-bold ${
                            analysis.email_data.domain_exists 
                              ? 'bg-emerald-50 text-emerald-600 border border-emerald-100' 
                              : 'bg-red-50 text-red-600 border border-red-100'
                          }`}>
                            {analysis.email_data.domain_exists ? 'Domain Exists' : 'Dead Domain / Fake'}
                          </span>
                        </p>
                        <p className="flex items-center gap-1.5">
                          Mail Server Domain: 
                          <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-bold ${
                            analysis.email_data.is_free_email 
                              ? 'bg-orange-50 text-orange-600 border border-orange-100' 
                              : (analysis.email_data.is_disposable ? 'bg-red-50 text-red-600 border border-red-100' : 'bg-slate-50 text-slate-500 border border-slate-100')
                          }`}>
                            {analysis.email_data.is_free_email ? 'Free Public Domain' : (analysis.email_data.is_disposable ? 'Disposable Mail' : 'Corporate Mail')}
                          </span>
                        </p>
                      </div>
                    </div>

                    {analysis.email_data.typosquatting_check && (
                      <div className="space-y-3">
                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Typosquatting Check</h4>
                        <div className="space-y-1.5 text-xs text-slate-500 font-medium">
                          <p className="flex items-center gap-1.5">
                            Similarity Match: 
                            <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-bold ${
                              analysis.email_data.typosquatting_check.is_exact_match 
                                ? 'bg-emerald-50 text-emerald-600 border border-emerald-100' 
                                : (analysis.email_data.typosquatting_check.is_suspicious_typosquatting ? 'bg-red-50 text-red-600 border border-red-100' : 'bg-orange-50 text-orange-600 border border-orange-100')
                            }`}>
                              {analysis.email_data.typosquatting_check.is_exact_match ? 'Exact Match' : (analysis.email_data.typosquatting_check.is_suspicious_typosquatting ? 'Suspicious Lookalike' : 'Domain Mismatch')}
                            </span>
                          </p>
                          {analysis.email_data.typosquatting_check.reason && (
                            <p className="text-slate-600 italic bg-slate-50 p-2 rounded-lg border border-slate-100 mt-2">
                              {analysis.email_data.typosquatting_check.reason}
                            </p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

          </div>

          {/* Right Column: Interactive Safety Recommendations */}
          <div className="lg:col-span-4 space-y-6">
            <div className="rounded-2xl bg-white p-6 shadow-sm border border-slate-200/80">
              <h3 className="text-base font-bold text-slate-800 mb-4 pb-3 border-b border-slate-50">Diligence Checklist</h3>
              <p className="text-[10px] text-slate-400 font-semibold mb-6">
                Perform these verified security checks before sending personal documents or payments. Check them off as you go.
              </p>

              {analysis?.recommendations.length === 0 ? (
                <p className="text-slate-450 text-xs font-semibold text-center py-4">No recommendations generated.</p>
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
                            ? 'bg-slate-50/50 border-slate-200/80 opacity-70' 
                            : 'bg-white border-slate-100 hover:border-slate-200'
                        }`}
                      >
                        <button
                          type="button"
                          className={`h-5 w-5 rounded border flex items-center justify-center shrink-0 mt-0.5 transition-colors cursor-pointer ${
                            isChecked 
                              ? 'bg-brand-500 border-brand-500 text-white' 
                              : 'border-slate-300 bg-white hover:border-brand-400'
                          }`}
                        >
                          {isChecked && <CheckCircle className="h-4.5 w-4.5 stroke-[2.5]" />}
                        </button>
                        <span className={`text-xs font-medium leading-relaxed select-none ${
                          isChecked ? 'line-through text-slate-400 font-semibold' : 'text-slate-700'
                        }`}>
                          {item}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

        </div>

      </div>
    </Layout>
  );
};

export default AnalysisResultPage;
