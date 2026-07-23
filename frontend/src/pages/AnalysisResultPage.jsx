import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../services/api';
import Layout from '../components/common/Layout';
import { useAuth } from '../context/AuthContext';
import { Card, PrimaryButton, SecondaryButton, Badge, Alert, Modal, Timeline } from '../components/common/Primitives';
import { 
  Download, 
  Trash2,
  CheckCircle,
  XCircle,
  HelpCircle,
  Fingerprint,
  Globe,
  Mail,
  Building,
  Briefcase,
  MapPin,
  CircleDollarSign,
  FileText,
  FileCheck2,
  AlertTriangle
} from 'lucide-react';

const AnalysisResultPage = () => {
  const { id: analysisId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAuthModal, setShowAuthModal] = useState(false);
  
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
      alert('Failed to download the PDF report document.');
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to permanently delete this scan?')) {
      return;
    }
    try {
      await api.delete(`/api/analyze/${analysisId}`);
      navigate(isAuthenticated ? '/dashboard' : '/');
    } catch (err) {
      console.error(err);
      alert('Failed to delete this report.');
    }
  };

  const getRiskDetails = (category) => {
    const normCategory = String(category || 'Needs Manual Verification').toLowerCase();
    if (normCategory.includes('low') || normCategory.includes('safe')) {
      return {
        bannerVariant: 'success',
        iconColor: 'text-success',
        title: 'Security Assessment: Low Risk / Safe',
        desc: 'Verification parameters indicate a standard outreach profile. Proceed with caution.'
      };
    } else if (normCategory.includes('manual') || normCategory.includes('needs')) {
      return {
        bannerVariant: 'warning',
        iconColor: 'text-warning',
        title: 'Security Assessment: Needs Manual Verification',
        desc: 'Registry discrepancies flagged. Complete manual domain validation before proceeding.'
      };
    } else if (normCategory.includes('medium') || normCategory.includes('suspicious')) {
      return {
        bannerVariant: 'warning',
        iconColor: 'text-warning',
        title: 'Security Assessment: Suspicious / Medium Risk Detected',
        desc: 'Linguistic heuristics or domain checks matched verified spam patterns.'
      };
    } else {
      return {
        bannerVariant: 'danger',
        iconColor: 'text-danger',
        title: 'Security Assessment: High Risk Detected',
        desc: 'Recruiter spoofing or payment baiting verified. Do not share sensitive details.'
      };
    }
  };

  // Helper to extract metadata from analysis content dynamically
  const extractJobMetadata = (data) => {
    const text = data?.processed_text || data?.original_content || "";
    
    const getMatch = (patterns, defaultVal = "Not detected") => {
      for (const p of patterns) {
        const match = text.match(p);
        if (match && match[1]) {
          return match[1].trim();
        }
      }
      return defaultVal;
    };

    const company = getMatch([
      /Company\s*Name\s*:\s*([^\n]+)/i,
      /Company\s*:\s*([^\n]+)/i,
      /Employer\s*:\s*([^\n]+)/i,
      /Firm\s*:\s*([^\n]+)/i
    ], "Unspecified Company");

    const title = getMatch([
      /Job\s*Title\s*:\s*([^\n]+)/i,
      /Role\s*:\s*([^\n]+)/i,
      /Position\s*:\s*([^\n]+)/i,
      /Job\s*:\s*([^\n]+)/i
    ], "Recruitment Outreach");

    const location = getMatch([
      /Location\s*:\s*([^\n]+)/i,
      /City\s*:\s*([^\n]+)/i,
      /Address\s*:\s*([^\n]+)/i,
      /Workplace\s*:\s*([^\n]+)/i
    ], "Remote / Unspecified");

    const salary = getMatch([
      /Salary\s*:\s*([^\n]+)/i,
      /Pay\s*:\s*([^\n]+)/i,
      /Compensation\s*:\s*([^\n]+)/i,
      /Stipend\s*:\s*([^\n]+)/i,
      /Rate\s*:\s*([^\n]+)/i
    ], "Not disclosed");

    const empType = getMatch([
      /Employment\s*Type\s*:\s*([^\n]+)/i,
      /Job\s*Type\s*:\s*([^\n]+)/i,
      /Type\s*:\s*([^\n]+)/i
    ], text.toLowerCase().includes("full-time") ? "Full-time" : text.toLowerCase().includes("part-time") ? "Part-time" : text.toLowerCase().includes("contract") ? "Contract" : "Unspecified");

    const email = data?.email_data?.sender_email || getMatch([
      /Email\s*:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/i,
      /Contact\s*:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/i
    ], "No email detected");

    const website = data?.website_data?.url || getMatch([
      /Website\s*:\s*(https?:\/\/[^\s]+)/i,
      /Domain\s*:\s*([^\s]+)/i
    ], "No domain detected");

    return { company, title, location, salary, empType, email, website };
  };

  const getVerificationStatusItems = (data) => {
    const status = data?.verification_status || {};
    
    // Status helper
    const getStatusType = (val) => {
      if (!val || val === "Unknown") return "unverified";
      if (["Unreachable", "Invalid", "Not Found"].includes(val)) return "failed";
      return "passed";
    };

    const keys = [
      { label: "Company Website", key: "Website" },
      { label: "Corporate Email", key: "Corporate Email" },
      { label: "WHOIS", key: "WHOIS" },
      { label: "DNS", key: "DNS" },
      { label: "SSL", key: "SSL" },
      { label: "LinkedIn", key: "LinkedIn" },
      { label: "Privacy Policy", key: "Privacy Policy" },
      { label: "Careers Page", key: "Careers Page" },
      { label: "Domain Age", key: "Domain Age" }
    ];

    return keys.map((k) => {
      const val = status[k.key] || "Unknown";
      return {
        label: k.label,
        value: val,
        status: getStatusType(val)
      };
    });
  };

  const getRiskBadgeVariant = (category) => {
    const norm = String(category || 'Needs Manual Verification').toLowerCase();
    if (norm.includes('low') || norm.includes('safe')) return 'success';
    if (norm.includes('manual') || norm.includes('needs') || norm.includes('medium') || norm.includes('suspicious')) return 'warning';
    return 'danger';
  };

  const getTimelineItems = (data) => {
    return [
      { label: 'INPUT', title: 'Payload ingested securely.', active: true },
      { label: 'AI ANALYSIS', title: 'Deep semantic reasoning execution completed.', active: true },
      { label: 'VERIFICATION', title: 'MX registry records and WHOIS registrations parsed.', active: true },
      { label: 'RULE ENGINE', title: 'Scam signature scan resolved.', active: true },
      { label: 'FINAL VERDICT', title: `Risk category computed as ${data?.risk_category || 'Needs Manual Verification'}.`, active: true },
      { label: 'REPORT GENERATED', title: 'Secure RecruitSafe audit report compiled.', active: true }
    ];
  };

  if (loading) {
    return (
      <Layout>
        <div className="space-y-6 max-w-[1280px] mx-auto py-12 animate-pulse select-none">
          <div className="h-24 bg-card rounded-xl border border-border"></div>
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            <div className="md:col-span-7 h-96 bg-card rounded-xl border border-border"></div>
            <div className="md:col-span-5 h-96 bg-card rounded-xl border border-border"></div>
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="max-w-md mx-auto py-16 flex flex-col items-center justify-center text-center space-y-4">
          <span className="material-symbols-outlined text-danger text-5xl">warning</span>
          <h3 className="font-sans text-xl font-bold">Report Unavailable</h3>
          <p className="text-text-secondary text-sm">{error}</p>
          <Link to="/" className="bg-brand text-white px-6 py-2 rounded-lg font-mono text-xs font-bold shadow-sm">
            Back Home
          </Link>
        </div>
      </Layout>
    );
  }

  const riskDetails = getRiskDetails(analysis?.risk_category);
  const metadata = extractJobMetadata(analysis);
  const verificationItems = getVerificationStatusItems(analysis);
  const timelineItems = getTimelineItems(analysis);

  return (
    <Layout>
      <div className="space-y-6 select-none max-w-[1280px] mx-auto text-left">
        
        {/* Warning Banner */}
        <div className="animate-in fade-in slide-in-from-top-4 duration-700">
          <div className="border rounded-xl p-5 flex flex-col md:flex-row items-center gap-5 relative overflow-hidden bg-card border-border">
            <div className="bg-bg p-3.5 rounded-full border border-border shrink-0">
              <span className={`material-symbols-outlined text-3xl ${riskDetails.iconColor}`} style={{ fontVariationSettings: "'FILL' 1" }}>
                {analysis?.risk_category?.toLowerCase().includes('low') || analysis?.risk_category?.toLowerCase().includes('safe') ? 'verified' : 'gpp_bad'}
              </span>
            </div>
            <div className="text-center md:text-left flex-1 space-y-0.5">
              <h1 className="font-sans text-xl font-extrabold text-text-primary tracking-tight">{riskDetails.title}</h1>
              <p className="font-sans text-xs text-text-secondary leading-relaxed">{riskDetails.desc}</p>
            </div>
            
            <div className="flex gap-2.5 shrink-0">
              {!isAuthenticated && (
                <PrimaryButton 
                  onClick={() => setShowAuthModal(true)}
                  className="px-4 py-2 text-xs"
                >
                  Save Report
                </PrimaryButton>
              )}
              <SecondaryButton 
                onClick={handleDownloadPDF}
                className="px-4 py-2 text-xs"
              >
                <Download className="h-4 w-4" />
                <span>Download Report</span>
              </SecondaryButton>
              {isAuthenticated && (
                <button 
                  onClick={handleDelete}
                  className="px-3 py-2 bg-danger/10 hover:bg-danger/20 text-danger border border-danger/20 rounded-lg cursor-pointer transition-colors"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Dynamic Metadata Details Card */}
        <Card className="grid grid-cols-2 md:grid-cols-5 gap-6 p-6">
          <div className="space-y-1">
            <div className="flex items-center gap-1.5 text-text-secondary">
              <Building className="h-3.5 w-3.5 shrink-0" />
              <span className="font-mono text-[9px] font-bold uppercase tracking-wider">Company</span>
            </div>
            <p className="text-xs font-bold text-text-primary truncate">{metadata.company}</p>
          </div>

          <div className="space-y-1">
            <div className="flex items-center gap-1.5 text-text-secondary">
              <Briefcase className="h-3.5 w-3.5 shrink-0" />
              <span className="font-mono text-[9px] font-bold uppercase tracking-wider">Job Title</span>
            </div>
            <p className="text-xs font-bold text-text-primary truncate">{metadata.title}</p>
          </div>

          <div className="space-y-1">
            <div className="flex items-center gap-1.5 text-text-secondary">
              <MapPin className="h-3.5 w-3.5 shrink-0" />
              <span className="font-mono text-[9px] font-bold uppercase tracking-wider">Location</span>
            </div>
            <p className="text-xs font-bold text-text-primary truncate">{metadata.location}</p>
          </div>

          <div className="space-y-1">
            <div className="flex items-center gap-1.5 text-text-secondary">
              <CircleDollarSign className="h-3.5 w-3.5 shrink-0" />
              <span className="font-mono text-[9px] font-bold uppercase tracking-wider">Salary Details</span>
            </div>
            <p className="text-xs font-bold text-text-primary truncate">{metadata.salary}</p>
          </div>

          <div className="col-span-2 md:col-span-1 space-y-1">
            <div className="flex items-center gap-1.5 text-text-secondary">
              <Globe className="h-3.5 w-3.5 shrink-0" />
              <span className="font-mono text-[9px] font-bold uppercase tracking-wider">Official Domain</span>
            </div>
            <p className="text-xs font-bold text-text-primary truncate">{metadata.website}</p>
          </div>
        </Card>

        {/* Scoring Gauges Grid (All 4 dynamic scores) */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <Card className="flex flex-col items-center justify-center p-4 text-center h-[220px]">
            <span className="font-mono text-[9px] font-bold text-text-secondary uppercase tracking-widest mb-3">
              Trust Score
            </span>
            <div className="relative flex items-center justify-center">
              <svg className="w-24 h-24">
                <circle className="text-border" cx="48" cy="48" fill="transparent" r="40" stroke="currentColor" strokeWidth="3"></circle>
                <circle 
                  className="text-brand progress-ring__circle" 
                  cx="48" 
                  cy="48" 
                  fill="transparent" 
                  r="40" 
                  stroke="currentColor" 
                  strokeDasharray="251.32" 
                  strokeDashoffset={251.32 - ((analysis?.trust_score ?? 85) / 100) * 251.32} 
                  strokeLinecap="round" 
                  strokeWidth="3"
                ></circle>
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-lg font-extrabold text-text-primary leading-none">{analysis?.trust_score ?? 85}%</span>
              </div>
            </div>
            <p className="text-[10px] text-text-secondary mt-3">Calculated safety indicators</p>
          </Card>

          <Card className="flex flex-col items-center justify-center p-4 text-center h-[220px]">
            <span className="font-mono text-[9px] font-bold text-text-secondary uppercase tracking-widest mb-3">
              Confidence Score
            </span>
            <div className="relative flex items-center justify-center">
              <svg className="w-24 h-24">
                <circle className="text-border" cx="48" cy="48" fill="transparent" r="40" stroke="currentColor" strokeWidth="3"></circle>
                <circle 
                  className="text-brand progress-ring__circle" 
                  cx="48" 
                  cy="48" 
                  fill="transparent" 
                  r="40" 
                  stroke="currentColor" 
                  strokeDasharray="251.32" 
                  strokeDashoffset={251.32 - ((analysis?.confidence_score ?? 70) / 100) * 251.32} 
                  strokeLinecap="round" 
                  strokeWidth="3"
                ></circle>
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-lg font-extrabold text-text-primary leading-none">{analysis?.confidence_score ?? 70}%</span>
              </div>
            </div>
            <p className="text-[10px] text-text-secondary mt-3">Data completeness index</p>
          </Card>

          <Card className="flex flex-col items-center justify-center p-4 text-center h-[220px]">
            <span className="font-mono text-[9px] font-bold text-text-secondary uppercase tracking-widest mb-3">
              Workflow Score
            </span>
            <div className="relative flex items-center justify-center">
              <svg className="w-24 h-24">
                <circle className="text-border" cx="48" cy="48" fill="transparent" r="40" stroke="currentColor" strokeWidth="3"></circle>
                <circle 
                  className="text-brand progress-ring__circle" 
                  cx="48" 
                  cy="48" 
                  fill="transparent" 
                  r="40" 
                  stroke="currentColor" 
                  strokeDasharray="251.32" 
                  strokeDashoffset={251.32 - ((analysis?.hiring_workflow?.score ?? 90) / 100) * 251.32} 
                  strokeLinecap="round" 
                  strokeWidth="3"
                ></circle>
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-lg font-extrabold text-text-primary leading-none">{analysis?.hiring_workflow?.score ?? 90}%</span>
              </div>
            </div>
            <p className="text-[10px] text-text-secondary mt-3">Hiring workflow structure</p>
          </Card>

          <Card className="flex flex-col items-center justify-center p-4 text-center h-[220px]">
            <span className="font-mono text-[9px] font-bold text-text-secondary uppercase tracking-widest mb-3">
              Input Quality
            </span>
            <div className="relative flex items-center justify-center">
              <svg className="w-24 h-24">
                <circle className="text-border" cx="48" cy="48" fill="transparent" r="40" stroke="currentColor" strokeWidth="3"></circle>
                <circle 
                  className="text-brand progress-ring__circle" 
                  cx="48" 
                  cy="48" 
                  fill="transparent" 
                  r="40" 
                  stroke="currentColor" 
                  strokeDasharray="251.32" 
                  strokeDashoffset={251.32 - ((analysis?.input_quality_score ?? 80) / 100) * 251.32} 
                  strokeLinecap="round" 
                  strokeWidth="3"
                ></circle>
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-lg font-extrabold text-text-primary leading-none">{analysis?.input_quality_score ?? 80}%</span>
              </div>
            </div>
            <p className="text-[10px] text-text-secondary mt-3">Information richness factor</p>
          </Card>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          
          {/* Left Column: Diagnostics Checklist (7 / 12) */}
          <div className="lg:col-span-7 space-y-6 flex flex-col justify-between">
            
            {/* Investigation Verification Panel */}
            <Card className="p-0 overflow-hidden flex-1">
              <div className="px-6 py-4 border-b border-border bg-bg/50 flex justify-between items-center">
                <h2 className="font-mono text-[10px] font-bold uppercase tracking-widest text-text-secondary">
                  Verification Status Panel
                </h2>
                <Badge variant={getRiskBadgeVariant(analysis?.risk_category)}>
                  {analysis?.risk_category || 'Needs Manual Verification'}
                </Badge>
              </div>

              <div className="divide-y divide-border">
                {verificationItems.map((item, idx) => (
                  <div key={idx} className="px-6 py-3 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="shrink-0 select-none">
                        {item.status === 'passed' ? (
                          <CheckCircle className="h-4.5 w-4.5 text-success" />
                        ) : item.status === 'failed' ? (
                          <XCircle className="h-4.5 w-4.5 text-danger" />
                        ) : (
                          <HelpCircle className="h-4.5 w-4.5 text-text-secondary/40" />
                        )}
                      </div>
                      <span className="text-xs font-bold text-text-primary">{item.label}</span>
                    </div>
                    <span className={`text-xs font-mono font-bold ${
                      item.status === 'passed' ? 'text-success' : item.status === 'failed' ? 'text-danger' : 'text-text-secondary'
                    }`}>
                      {item.value}
                    </span>
                  </div>
                ))}
              </div>
            </Card>

            {/* Recommendations */}
            <Card className="space-y-4 mt-6">
              <div className="flex items-center gap-2">
                <FileCheck2 className="h-4.5 w-4.5 text-brand" />
                <h2 className="font-sans text-[15px] font-bold text-text-primary">Actionable Recommendations</h2>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                {analysis?.recommendations && analysis.recommendations.length > 0 ? (
                  analysis.recommendations.map((rec, idx) => (
                    <div key={idx} className="p-4 border border-border rounded-lg bg-bg">
                      <h4 className="font-sans text-xs text-text-primary font-bold mb-1">
                        Diligence Instruction #{idx + 1}
                      </h4>
                      <p className="font-sans text-[11px] text-text-secondary leading-relaxed">
                        {rec}
                      </p>
                    </div>
                  ))
                ) : (
                  <>
                    <div className="p-4 border border-border rounded-lg bg-bg">
                      <h4 className="font-sans text-xs text-text-primary font-bold mb-1">Contact Verification</h4>
                      <p className="font-sans text-[11px] text-text-secondary leading-relaxed">
                        Validate sender email addresses against official corporate registry records.
                      </p>
                    </div>
                    <div className="p-4 border border-border rounded-lg bg-bg">
                      <h4 className="font-sans text-xs text-text-primary font-bold mb-1">No Fee Disbursal</h4>
                      <p className="font-sans text-[11px] text-text-secondary leading-relaxed">
                        Refrain from issuing payments for onboarding laptops or licensing material fees.
                      </p>
                    </div>
                  </>
                )}
              </div>
            </Card>

          </div>

          {/* Right Column: AI Explanations & Evidence Preview (5 / 12) */}
          <div className="lg:col-span-5 space-y-6 flex flex-col justify-between">
            
            {/* Detailed AI Explanation */}
            <Card className="relative overflow-hidden group border-brand/20 flex-1 flex flex-col justify-between p-6 text-left">
              <div className="absolute -top-24 -right-24 w-48 h-48 bg-brand/5 rounded-full blur-3xl transition-transform group-hover:scale-150 duration-1000"></div>
              
              <div className="relative z-10 space-y-5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Fingerprint className="h-4.5 w-4.5 text-brand" />
                    <h3 className="font-mono text-[10px] font-bold text-brand uppercase tracking-widest">AI Forensic Executive Summary</h3>
                  </div>
                </div>

                <p className="font-sans text-[13px] text-text-primary italic leading-relaxed">
                  "{analysis?.ai_summary || analysis?.risk_explanation || "Our heuristics scan determined some unverified signals require inspection."}"
                </p>

                {/* Structured Positive and Warning Signals */}
                <div className="space-y-3 pt-3 border-t border-border">
                  <div>
                    <span className="font-mono text-[9px] font-bold text-text-secondary uppercase tracking-wider block mb-1.5">Positive Indicators</span>
                    {analysis?.positive_findings && analysis.positive_findings.length > 0 ? (
                      <div className="space-y-1">
                        {analysis.positive_findings.slice(0, 3).map((item, idx) => (
                          <div key={idx} className="flex items-center gap-1.5 text-[11px] text-success font-semibold">
                            <CheckCircle className="h-3 w-3 shrink-0" />
                            <span className="truncate">{item.title || item.factor_name}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-[11px] text-text-secondary italic">None registered</p>
                    )}
                  </div>

                  <div>
                    <span className="font-mono text-[9px] font-bold text-text-secondary uppercase tracking-wider block mb-1.5">Red Flags Flagged</span>
                    {analysis?.red_flags && analysis.red_flags.length > 0 ? (
                      <div className="space-y-1">
                        {analysis.red_flags.slice(0, 3).map((item, idx) => (
                          <div key={idx} className="flex items-center gap-1.5 text-[11px] text-danger font-semibold">
                            <AlertTriangle className="h-3 w-3 shrink-0" />
                            <span className="truncate">{item.title}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-[11px] text-text-secondary italic">No critical flags raised</p>
                    )}
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-border flex flex-wrap gap-1.5 mt-4">
                <span className="bg-brand-light text-brand font-mono text-[9px] font-bold px-2 py-0.5 rounded border border-brand/20 uppercase tracking-wider">
                  Engine v2.2
                </span>
                <span className="bg-bg text-text-secondary font-mono text-[9px] font-bold px-2 py-0.5 rounded border border-border uppercase tracking-wider">
                  {analysis?.input_type || 'TEXT'} Scan
                </span>
              </div>
            </Card>

            {/* Evidence Document Preview Layout */}
            <Card className="p-0 overflow-hidden mt-6 text-left">
              <div className="p-6 bg-bg/50 border-b border-border text-center select-none">
                <div className="max-w-[280px] mx-auto bg-card border border-border rounded-lg shadow-sm p-4 relative font-sans space-y-4">
                  {/* Watermark stamp */}
                  <div className="absolute top-2 right-2 border-2 border-brand/20 text-brand/20 rounded font-mono text-[8px] font-bold px-1 rotate-12 select-none uppercase">
                    RecruitSafe
                  </div>
                  
                  <div className="flex items-center gap-2 border-b border-border pb-2">
                    <FileText className="h-4.5 w-4.5 text-brand" />
                    <div className="text-left">
                      <p className="font-mono text-[8px] font-bold text-text-secondary">AI REPORT AUDIT</p>
                      <p className="text-[9px] font-bold text-text-primary max-w-[120px] truncate">{metadata.company}</p>
                    </div>
                  </div>

                  <div className="space-y-2 text-left">
                    <div className="flex justify-between text-[8px] font-mono text-text-secondary">
                      <span>Trust Rating</span>
                      <span className="font-bold text-text-primary">{analysis?.trust_score ?? 85}%</span>
                    </div>
                    <div className="flex justify-between text-[8px] font-mono text-text-secondary">
                      <span>Confidence</span>
                      <span className="font-bold text-text-primary">{analysis?.confidence_score ?? 70}%</span>
                    </div>
                    <div className="flex justify-between text-[8px] font-mono text-text-secondary">
                      <span>Input Quality</span>
                      <span className="font-bold text-text-primary">{analysis?.input_quality_score ?? 80}%</span>
                    </div>
                  </div>

                  <div className="flex justify-between items-center pt-2 border-t border-border">
                    <span className="font-mono text-[7px] text-text-secondary uppercase">Safety Verdict</span>
                    <Badge variant={getRiskBadgeVariant(analysis?.risk_category)} className="text-[7px] px-1 py-0.5">
                      {analysis?.risk_category || 'Needs Review'}
                    </Badge>
                  </div>
                </div>
              </div>
              <div className="p-4 flex justify-between items-center select-none bg-card">
                <span className="font-sans text-xs text-text-secondary truncate max-w-xs font-semibold">
                  RecruitSafe_Evidence_{analysisId?.slice(0, 6) || 'Report'}.pdf
                </span>
                <button 
                  onClick={handleDownloadPDF}
                  className="material-symbols-outlined text-brand hover:bg-bg p-2 rounded-lg border border-border transition-colors cursor-pointer"
                >
                  download
                </button>
              </div>
            </Card>

          </div>

        </div>

        {/* Timeline / History */}
        <Card className="space-y-5">
          <h3 className="font-mono text-[10px] font-bold text-text-secondary uppercase tracking-widest">
            AI Scans Investigation Timeline
          </h3>
          <Timeline items={timelineItems} />
        </Card>

      </div>

      {/* Guest Save Report Modal */}
      <Modal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        title="Save Your Analysis"
      >
        <div className="space-y-6 text-center">
          <p className="text-sm text-text-secondary leading-relaxed">
            Your analysis is complete! Create a free RecruitSafe account to save this report, track your history, and access it from any device.
          </p>

          <div className="flex flex-col gap-3 pt-2">
            <PrimaryButton 
              onClick={() => navigate('/register', { state: { from: { pathname: `/analysis/${analysisId}` } } })}
              className="w-full py-3"
            >
              Create Free Account
            </PrimaryButton>
            <SecondaryButton 
              onClick={() => navigate('/login', { state: { from: { pathname: `/analysis/${analysisId}` } } })}
              className="w-full py-3"
            >
              Sign In
            </SecondaryButton>
            <button 
              onClick={() => setShowAuthModal(false)}
              className="text-xs text-text-secondary font-semibold hover:text-brand transition-colors cursor-pointer py-1"
            >
              Continue as Guest
            </button>
          </div>
        </div>
      </Modal>

    </Layout>
  );
};

export default AnalysisResultPage;
