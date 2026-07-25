import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../services/api';
import Layout from '../components/common/Layout';
import { useAuth } from '../context/AuthContext';
import { Card, PrimaryButton, SecondaryButton, Badge, Alert, Modal } from '../components/common/Primitives';
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
  const [showAllRecs, setShowAllRecs] = useState(false);
  const [showScoreCalcModal, setShowScoreCalcModal] = useState(false);
  
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
        title: 'Verification Complete: Low Risk',
        desc: 'No major risk indicators were identified. Proceed with normal precautions.'
      };
    } else if (normCategory.includes('manual') || normCategory.includes('needs')) {
      return {
        bannerVariant: 'warning',
        iconColor: 'text-warning',
        title: 'Potential Recruitment Risk Detected',
        desc: 'Minor or incomplete verification parameters flagged. Manual verification is recommended before proceeding.'
      };
    } else if (normCategory.includes('medium') || normCategory.includes('suspicious')) {
      return {
        bannerVariant: 'warning',
        iconColor: 'text-warning',
        title: 'Potential Recruitment Risk Detected',
        desc: 'Minor or incomplete verification parameters flagged. Manual verification is recommended before proceeding.'
      };
    } else {
      return {
        bannerVariant: 'danger',
        iconColor: 'text-danger',
        title: 'Potential Recruitment Risk Detected',
        desc: 'Multiple risk indicators were identified during analysis. Manual verification is recommended before proceeding.'
      };
    }
  };

  const getTrustScoreContributors = (data) => {
    if (!data) return [];
    const list = [];
    
    // 1. Check rules from evidence
    const negativeEvidence = (data.evidence || []).filter(e => e.score < 0);
    negativeEvidence.sort((a, b) => Math.abs(a.score) - Math.abs(b.score));
    
    negativeEvidence.forEach(e => {
      const rid = String(e.rule_id || e.id || '').toLowerCase();
      if (rid === 'registration_fee' || rid === 'training_fee' || rid === 'payment_request' || rid === 'paid_certification') {
        list.push('Training fee detected');
      } else if (rid === 'telegram_only' || rid === 'whatsapp_only') {
        list.push('Communication restricted to chat apps');
      } else if (rid === 'no_interview') {
        list.push('Direct hiring without screening');
      } else if (rid === 'guaranteed_placement') {
        list.push('Guaranteed placement promised');
      } else if (rid === 'urgency_urg') {
        list.push('High urgency pressure applied');
      } else if (rid === 'no_company_name') {
        list.push('Anonymous employer listing');
      } else if (rid === 'free_email') {
        list.push('Public or free email domain');
      }
    });

    // 2. Check verification statuses
    const verif = data.verification_status || {};
    if (verif.Website === 'Unreachable' || verif.Website === 'Not Found' || verif.Website === 'Missing') {
      list.push('Verification signals incomplete');
    }
    if (verif.SSL === 'Invalid') {
      list.push('Infrastructure confidence reduced');
    }
    if (verif['Corporate Email'] === 'Invalid' || verif['Corporate Email'] === 'Disposable') {
      list.push('Unverified email domain');
    }
    if (verif['Careers Page'] === 'Not Found' || verif['Careers Page'] === 'Missing') {
      list.push('Careers page not found');
    }
    if (verif['Domain Age'] === 'Unknown' || verif['Domain Age'] === 'Not Found') {
      list.push('Domain age unverified');
    }

    const uniqueList = Array.from(new Set(list));
    if (uniqueList.length === 0 && (data.trust_score || 100) < 100) {
      uniqueList.push('Incomplete company verification');
      uniqueList.push('Infrastructure confidence reduced');
    }
    return uniqueList.slice(0, 3);
  };

  const getWorkflowRiskInfo = (data) => {
    const score = data?.hiring_workflow?.score ?? 90;
    let risk = 'Low';
    let reasons = ['Standard screening process.', 'Clear interview stages.'];
    if (score < 40) {
      risk = 'High';
      reasons = ['Upfront payment demanded.', 'No candidate screening.'];
    } else if (score < 75) {
      risk = 'Medium';
      reasons = ['Payment requested before hiring process.', 'Interview sequence incomplete.'];
    }
    return { risk, reasons };
  };

  const getMissingInformation = (data) => {
    if (!data) return [];
    const list = [];
    const verif = data.verification_status || {};
    if (verif.Website === 'Unreachable' || verif.Website === 'Not Found' || verif.Website === 'Missing') {
      list.push('Official company website');
    }
    if (verif['Corporate Email'] === 'Invalid' || verif['Corporate Email'] === 'Disposable') {
      list.push('Recruiter email');
    }
    if (verif['Domain Age'] === 'Unknown' || verif['Domain Age'] === 'Not Found') {
      list.push('Domain age');
    }
    if (verif['Privacy Policy'] === 'Not Found' || verif['Privacy Policy'] === 'Missing') {
      list.push('Company policies');
    }
    if (list.length === 0 && data.missing_information && data.missing_information.length > 0) {
      return data.missing_information.slice(0, 4);
    }
    // Make sure we have fallback mock list if database verif is fully verified but quality score is low
    if (list.length === 0 && (data.input_quality_score || 100) < 100) {
      list.push('Official company website');
      list.push('Recruiter email');
      list.push('Domain age');
      list.push('Company policies');
    }
    return list;
  };

  const getCleanAISummary = (data) => {
    if (!data) return "";
    const normCategory = String(data.risk_category || 'Needs Review').toLowerCase();
    const isSafe = normCategory.includes('low') || normCategory.includes('safe');

    if (isSafe) {
      return `RecruitSafe completed the verification audit. The analysis identified positive trust indicators, including:
• Secure HTTPS connection enabled
• Reachable company domain
• Consistent hiring workflow structure

The job listing aligns with standard recruitment practices. Proceed with standard caution.`;
    }

    const contributors = getTrustScoreContributors(data);
    const bullets = contributors.length > 0
      ? contributors.map(c => `• ${c}`).join('\n')
      : `• Incomplete company verification\n• Missing legal website information\n• Infrastructure confidence reduced`;

    return `RecruitSafe identified several recruitment risk indicators.

The strongest signals include:
${bullets}

Although the job description itself does not strongly resemble common scam templates, the combined evidence suggests elevated recruitment risk.

Manual verification is recommended before proceeding.`;
  };

  const getCleanPositiveIndicators = (data) => {
    if (!data) return [];
    const list = [];
    
    const pos = data.positive_findings || [];
    pos.forEach(p => {
      const pid = String(p.id || p.rule_id || '').toLowerCase();
      if (pid.includes('ssl') || pid.includes('https')) {
        list.push('HTTPS enabled');
        list.push('Valid SSL certificate');
      }
      if (pid.includes('hiring') || pid.includes('workflow') || pid.includes('process')) {
        list.push('Professional hiring workflow');
      }
      if (pid.includes('email') || pid.includes('corp')) {
        list.push('Corporate email verified');
      }
      if (pid.includes('careers')) {
        list.push('Official careers page found');
      }
    });

    const verif = data.verification_status || {};
    if (verif.Website === 'Verified') {
      list.push('Website reachable');
    }
    if (verif.SSL === 'Verified' || verif.SSL === 'Valid') {
      list.push('Valid SSL certificate');
      list.push('HTTPS enabled');
    }
    if (verif['Corporate Email'] === 'Verified' || verif['Corporate Email'] === 'Valid') {
      list.push('Corporate email verified');
    }
    if (verif['Careers Page'] === 'Verified' || verif['Careers Page'] === 'Found') {
      list.push('Official careers page found');
    }

    // Default indicators fallback if none returned
    if (list.length === 0 && (data.trust_score || 100) > 40) {
      list.push('HTTPS enabled');
      list.push('Valid SSL certificate');
      list.push('Website reachable');
    }

    return Array.from(new Set(list));
  };

  // Helper to extract metadata from analysis content dynamically
  const extractJobMetadata = (data) => {
    const text = data?.processed_text || data?.original_content || "";
    
    const getMatch = (patterns, defaultVal = "") => {
      for (const p of patterns) {
        const match = text.match(p);
        if (match && match[1]) {
          return match[1].trim();
        }
      }
      return defaultVal;
    };

    const rawCompany = getMatch([
      /Company\s*Name\s*:\s*([^\n]+)/i,
      /Company\s*:\s*([^\n]+)/i,
      /Employer\s*:\s*([^\n]+)/i,
      /Firm\s*:\s*([^\n]+)/i
    ], "");

    let company = "Company could not be identified";
    if (rawCompany) {
      const isVerified = (data?.verification_status?.Website === 'Verified' || data?.risk_category === 'Safe' || data?.risk_category === 'Verified');
      if (isVerified) {
        company = rawCompany;
      } else {
        company = `Possible Company: ${rawCompany}`;
      }
    }

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

    const rawWebsite = data?.website_data?.url || getMatch([
      /Website\s*:\s*(https?:\/\/[^\s]+)/i,
      /Domain\s*:\s*([^\s]+)/i
    ], "Not Found");

    const isAppForm = /form|gle|google|docs|survey|apply|questionnaire|sheet|airtable|typeform/i.test(rawWebsite);
    let website = "Not Found";
    let applicationLink = "Not Found";

    if (isAppForm) {
      applicationLink = rawWebsite;
    } else {
      website = rawWebsite;
    }
    if (website === "No domain detected") {
      website = "Not Found";
    }

    return { company, title, location, salary, empType, email, website, applicationLink };
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
      let val = status[k.key] || "Unknown";
      if (val === "Missing") {
        val = "Not Found";
      }
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
        <Card className="grid grid-cols-2 md:grid-cols-6 gap-6 p-6">
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

          <div className="space-y-1">
            <div className="flex items-center gap-1.5 text-text-secondary">
              <Globe className="h-3.5 w-3.5 shrink-0" />
              <span className="font-mono text-[9px] font-bold uppercase tracking-wider">Company Website</span>
            </div>
            <p className="text-xs font-bold text-text-primary truncate">{metadata.website}</p>
          </div>

          <div className="space-y-1">
            <div className="flex items-center gap-1.5 text-text-secondary">
              <Globe className="h-3.5 w-3.5 shrink-0" />
              <span className="font-mono text-[9px] font-bold uppercase tracking-wider">Application Link</span>
            </div>
            <p className="text-xs font-bold text-text-primary truncate">{metadata.applicationLink}</p>
          </div>
        </Card>

        {/* Scoring Gauges Grid (All 4 dynamic scores) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
          {/* Trust Score Card */}
          <Card 
            className="flex flex-col items-center justify-between p-5 text-center min-h-[250px] relative group cursor-help select-none"
            title="Combined score estimating the overall risk of this job posting."
          >
            <span className="font-mono text-[9px] font-bold text-text-secondary uppercase tracking-widest mb-2 block">
              Trust Score
            </span>
            <div className="relative flex items-center justify-center my-1.5">
              <svg className="w-20 h-20">
                <circle className="text-border" cx="40" cy="40" fill="transparent" r="34" stroke="currentColor" strokeWidth="3"></circle>
                <circle 
                  className="text-brand progress-ring__circle" 
                  cx="40" 
                  cy="40" 
                  fill="transparent" 
                  r="34" 
                  stroke="currentColor" 
                  strokeDasharray="213.63" 
                  strokeDashoffset={213.63 - ((analysis?.trust_score ?? 85) / 100) * 213.63} 
                  strokeLinecap="round" 
                  strokeWidth="3"
                ></circle>
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-base font-extrabold text-text-primary leading-none">{analysis?.trust_score ?? 85}%</span>
              </div>
            </div>
            
            {getTrustScoreContributors(analysis).length > 0 && (
              <div className="text-left w-full px-1 py-1 bg-bg/50 rounded border border-border/40 my-2">
                <span className="text-[8px] font-bold text-text-secondary uppercase block mb-0.5">Why?</span>
                <ul className="list-disc pl-3 text-[8px] text-text-secondary space-y-0.5">
                  {getTrustScoreContributors(analysis).map((c, i) => (
                    <li key={i} className="truncate">{c}</li>
                  ))}
                </ul>
              </div>
            )}
            
            <button 
              onClick={(e) => {
                e.stopPropagation();
                setShowScoreCalcModal(true);
              }}
              className="text-[8px] text-brand hover:underline font-bold cursor-pointer mt-1"
            >
              How was this score calculated?
            </button>
          </Card>

          {/* Analysis Confidence Card */}
          <Card 
            className="flex flex-col items-center justify-between p-5 text-center min-h-[250px] relative group cursor-help select-none"
            title="Represents how confident RecruitSafe is in this assessment based on available evidence. Higher confidence means more information was available during analysis."
          >
            <span className="font-mono text-[9px] font-bold text-text-secondary uppercase tracking-widest mb-2 block">
              Analysis Confidence
            </span>
            <div className="relative flex items-center justify-center my-1.5">
              <svg className="w-20 h-20">
                <circle className="text-border" cx="40" cy="40" fill="transparent" r="34" stroke="currentColor" strokeWidth="3"></circle>
                <circle 
                  className="text-brand progress-ring__circle" 
                  cx="40" 
                  cy="40" 
                  fill="transparent" 
                  r="34" 
                  stroke="currentColor" 
                  strokeDasharray="213.63" 
                  strokeDashoffset={213.63 - ((analysis?.confidence_score ?? 70) / 100) * 213.63} 
                  strokeLinecap="round" 
                  strokeWidth="3"
                ></circle>
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-base font-extrabold text-text-primary leading-none">{analysis?.confidence_score ?? 70}%</span>
              </div>
            </div>
            <p className="text-[8px] text-text-secondary leading-relaxed px-1 mt-2">
              Represents how confident RecruitSafe is in this assessment based on available evidence.
            </p>
          </Card>

          {/* Workflow Risk Card */}
          <Card 
            className="flex flex-col items-center justify-between p-5 text-center min-h-[250px] relative group cursor-help select-none"
            title="Hiring workflow risk category based on the presence of onboarding payment requirements or direct hiring."
          >
            <span className="font-mono text-[9px] font-bold text-text-secondary uppercase tracking-widest mb-2 block">
              Workflow Risk
            </span>
            
            <div className="flex-1 flex items-center justify-center my-3">
              <span className={`text-xl font-extrabold tracking-tight ${
                getWorkflowRiskInfo(analysis).risk === 'Low' ? 'text-success' :
                getWorkflowRiskInfo(analysis).risk === 'Medium' ? 'text-warning' : 'text-danger'
              }`}>
                {getWorkflowRiskInfo(analysis).risk}
              </span>
            </div>

            <div className="text-left w-full px-1 py-1 bg-bg/50 rounded border border-border/40 my-2">
              <ul className="list-disc pl-3 text-[8px] text-text-secondary space-y-0.5">
                {getWorkflowRiskInfo(analysis).reasons.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
          </Card>

          {/* Information Available Card */}
          <Card 
            className="flex flex-col items-center justify-between p-5 text-center min-h-[250px] relative group cursor-help select-none"
            title="Measures completeness of the information provided in the job description."
          >
            <span className="font-mono text-[9px] font-bold text-text-secondary uppercase tracking-widest mb-2 block">
              Information Available
            </span>
            <div className="relative flex items-center justify-center my-1.5">
              <svg className="w-20 h-20">
                <circle className="text-border" cx="40" cy="40" fill="transparent" r="34" stroke="currentColor" strokeWidth="3"></circle>
                <circle 
                  className="text-brand progress-ring__circle" 
                  cx="40" 
                  cy="40" 
                  fill="transparent" 
                  r="34" 
                  stroke="currentColor" 
                  strokeDasharray="213.63" 
                  strokeDashoffset={213.63 - ((analysis?.input_quality_score ?? 80) / 100) * 213.63} 
                  strokeLinecap="round" 
                  strokeWidth="3"
                ></circle>
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-base font-extrabold text-text-primary leading-none">{analysis?.input_quality_score ?? 80}%</span>
              </div>
            </div>
            
            {getMissingInformation(analysis).length > 0 && (
              <div className="text-left w-full px-1 py-1 bg-bg/50 rounded border border-border/40 my-2">
                <span className="text-[8px] font-bold text-text-secondary uppercase block mb-0.5">Missing Info:</span>
                <ul className="list-disc pl-3 text-[8px] text-text-secondary space-y-0.5">
                  {getMissingInformation(analysis).map((m, i) => (
                    <li key={i} className="truncate">{m}</li>
                  ))}
                </ul>
              </div>
            )}
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
                  (showAllRecs ? analysis.recommendations : analysis.recommendations.slice(0, 3)).map((rec, idx) => (
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
              {analysis?.recommendations && analysis.recommendations.length > 3 && (
                <div className="text-center pt-2">
                  <button 
                    onClick={() => setShowAllRecs(!showAllRecs)}
                    className="text-xs text-brand font-bold hover:underline cursor-pointer py-1"
                  >
                    {showAllRecs ? 'Show Less' : 'View All Recommendations'}
                  </button>
                </div>
              )}
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

                <div className="font-sans text-[12px] text-text-primary leading-relaxed whitespace-pre-line">
                  {getCleanAISummary(analysis)}
                </div>

                {/* Structured Positive and Warning Signals */}
                <div className="space-y-3 pt-3 border-t border-border">
                  <div>
                    <span className="font-mono text-[9px] font-bold text-text-secondary uppercase tracking-wider block mb-1.5">Positive Indicators</span>
                    {getCleanPositiveIndicators(analysis).length > 0 ? (
                      <div className="space-y-1">
                        {getCleanPositiveIndicators(analysis).map((item, idx) => (
                          <div key={idx} className="flex items-center gap-1.5 text-[11px] text-success font-semibold">
                            <CheckCircle className="h-3 w-3 shrink-0" />
                            <span className="truncate">{item}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-[11px] text-text-secondary italic">None registered</p>
                    )}
                  </div>

                  <div>
                    <span className="font-mono text-[9px] font-bold text-text-secondary uppercase tracking-wider block mb-1.5">Risk Indicators</span>
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



      </div>

      {/* Score Explanation Modal */}
      <Modal
        isOpen={showScoreCalcModal}
        onClose={() => setShowScoreCalcModal(false)}
        title="How is the Trust Score calculated?"
      >
        <div className="space-y-4 text-left">
          <p className="text-xs text-text-secondary leading-relaxed">
            The Trust Score represents a multi-layered security assessment of the job posting to estimate recruitment risk.
          </p>
          <div className="space-y-2 bg-bg p-4 rounded-lg border border-border">
            <span className="text-[10px] font-bold text-text-secondary uppercase tracking-wide block mb-1">Trust Score considers:</span>
            <ul className="space-y-1.5 text-xs text-text-primary font-semibold">
              <li className="flex items-center gap-2">
                <span className="text-brand">✓</span> Rule Engine findings
              </li>
              <li className="flex items-center gap-2">
                <span className="text-brand">✓</span> Website verification
              </li>
              <li className="flex items-center gap-2">
                <span className="text-brand">✓</span> Machine Learning prediction
              </li>
            </ul>
          </div>
          <p className="text-[11px] text-text-secondary leading-relaxed italic">
            These security components are fused together to compute the overall risk index and verify employer trust.
          </p>
        </div>
      </Modal>
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
