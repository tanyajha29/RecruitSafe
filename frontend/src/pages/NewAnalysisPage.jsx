import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../services/api';
import Layout from '../components/common/Layout';
import FileUploader from '../components/analysis/FileUploader';
import { Card, PrimaryButton, InputField, Alert } from '../components/common/Primitives';
import { 
  ShieldAlert, 
  AlertTriangle,
  Play,
  Sparkles,
  Link as LinkIcon,
  Mail,
  FileText
} from 'lucide-react';

const NewAnalysisPage = () => {
  const [activeTab, setActiveTab] = useState('email'); // 'link', 'email', 'document'
  const [content, setContent] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  
  // Loading & Pipeline progress states
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisId, setAnalysisId] = useState(null);
  const [progressStep, setProgressStep] = useState(0);
  const [error, setError] = useState('');

  const navigate = useNavigate();

  const pipelineSteps = [
    "Uploading submission and registering job check...",
    "Extracting text details and cleaning horizontal whitespace...",
    "Running domain intelligence, WHOIS, and SSL queries...",
    "Parsing recruiter email and checking typosquatting indicators...",
    "Scanning rule-based triggers and matching financial fraud keywords...",
    "Consulting Llama AI reasoning engine...",
    "Calculating composite trust score and safety audit recommendations..."
  ];

  useEffect(() => {
    setContent('');
    setSelectedFile(null);
    setError('');
  }, [activeTab]);

  useEffect(() => {
    let interval;
    if (isAnalyzing) {
      interval = setInterval(() => {
        setProgressStep((prev) => {
          if (prev < pipelineSteps.length - 1) {
            return prev + 1;
          }
          return prev;
        });
      }, 2000);
    } else {
      setProgressStep(0);
    }
    return () => clearInterval(interval);
  }, [isAnalyzing]);

  const pollAnalysisStatus = async (id) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await api.get(`/api/analyze/${id}`);
        const data = response.data;
        
        if (data.status === 'completed') {
          clearInterval(pollInterval);
          setIsAnalyzing(false);
          navigate(`/analysis/${id}`);
        } else if (data.status === 'failed') {
          clearInterval(pollInterval);
          setIsAnalyzing(false);
          setError(data.error_message || 'The analysis pipeline failed to evaluate the job check.');
        }
      } catch (err) {
        console.error('Error polling status:', err);
        clearInterval(pollInterval);
        setIsAnalyzing(false);
        setError('Connection lost while checking analysis status.');
      }
    }, 2000);
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setError('');
    setIsAnalyzing(true);
    setProgressStep(0);

    const formData = new FormData();

    if (activeTab === 'link') {
      if (!content || !content.trim()) {
        setError('Please enter a job posting URL.');
        setIsAnalyzing(false);
        return;
      }
      formData.append('input_type', 'url');
      formData.append('content', content);
    } else if (activeTab === 'email') {
      if (!content || !content.trim()) {
        setError('Please paste job description or email text content.');
        setIsAnalyzing(false);
        return;
      }
      formData.append('input_type', 'email');
      formData.append('content', content);
    } else {
      // Document upload
      if (!selectedFile) {
        setError('Please select a document file to upload.');
        setIsAnalyzing(false);
        return;
      }
      const ext = selectedFile.name.split('.').pop().toLowerCase();
      const isPDF = ext === 'pdf';
      formData.append('input_type', isPDF ? 'pdf' : 'image');
      formData.append('file', selectedFile);
    }

    try {
      const response = await api.post('/api/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      const { analysis_id } = response.data;
      setAnalysisId(analysis_id);
      pollAnalysisStatus(analysis_id);
    } catch (err) {
      console.error('Analysis submission failed:', err);
      setIsAnalyzing(false);
      setError(
        err.response?.data?.detail || 
        'An error occurred during submission. Please try again.'
      );
    }
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-8 select-none">
        
        {/* Error Callout */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
            >
              <Alert variant="danger" onClose={() => setError('')}>
                {error}
              </Alert>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence mode="wait">
          {!isAnalyzing ? (
            <motion.div
              key="input-stage"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              className="space-y-12"
            >
              {/* Header Section */}
              <div className="text-center space-y-4">
                <h1 className="font-sans text-3xl font-extrabold text-text-primary tracking-tight">New Analysis</h1>
                <p className="font-sans text-[16px] text-text-secondary max-w-lg mx-auto">
                  Submit recruiter communications or job descriptions for intelligent fraud detection.
                </p>
              </div>

              {/* Submission Canvas */}
              <Card className="p-0 overflow-hidden text-left">
                {/* Tabs Menu */}
                <div className="flex border-b border-border relative">
                  <button 
                    onClick={() => setActiveTab('link')}
                    className={`flex-1 py-4 font-mono text-[13px] font-bold transition-colors flex items-center justify-center gap-2 cursor-pointer ${
                      activeTab === 'link' ? 'text-brand' : 'text-text-secondary hover:bg-bg/50'
                    }`}
                  >
                    <LinkIcon className="h-4.5 w-4.5" />
                    <span>Link</span>
                    {activeTab === 'link' && <div className="absolute bottom-[-1px] left-0 w-full bg-brand h-[2px]"></div>}
                  </button>

                  <button 
                    onClick={() => setActiveTab('email')}
                    className={`flex-1 py-4 font-mono text-[13px] font-bold transition-colors flex items-center justify-center gap-2 cursor-pointer relative ${
                      activeTab === 'email' ? 'text-brand' : 'text-text-secondary hover:bg-bg/50'
                    }`}
                  >
                    <Mail className="h-4.5 w-4.5" />
                    <span>Email Content</span>
                    {activeTab === 'email' && <div className="absolute bottom-[-1px] left-0 w-full bg-brand h-[2px]"></div>}
                  </button>

                  <button 
                    onClick={() => setActiveTab('document')}
                    className={`flex-1 py-4 font-mono text-[13px] font-bold transition-colors flex items-center justify-center gap-2 cursor-pointer ${
                      activeTab === 'document' ? 'text-brand' : 'text-text-secondary hover:bg-bg/50'
                    }`}
                  >
                    <FileText className="h-4.5 w-4.5" />
                    <span>Document Upload</span>
                    {activeTab === 'document' && <div className="absolute bottom-[-1px] left-0 w-full bg-brand h-[2px]"></div>}
                  </button>
                </div>

                {/* Content Area */}
                <div className="p-8">
                  {/* Email & Text Area Section */}
                  {activeTab === 'email' && (
                    <form onSubmit={handleAnalyze} className="space-y-6 text-left">
                      <div className="relative group">
                        <textarea 
                          required
                          value={content}
                          onChange={(e) => setContent(e.target.value)}
                          maxLength={5000}
                          className="w-full h-80 bg-bg border border-border rounded-lg p-6 font-sans text-sm text-text-primary focus:outline-none focus:ring-1 focus:ring-brand focus:border-brand transition-all placeholder:text-text-secondary/40 resize-none" 
                          placeholder="Paste job description or email here..."
                        />
                        <div className="absolute bottom-4 right-4 flex items-center gap-3">
                          <span className="font-mono text-[10px] text-text-secondary font-semibold">{content.length} / 5000 characters</span>
                        </div>
                      </div>

                      <div className="flex flex-col md:flex-row items-center justify-between gap-6 pt-4">
                        <div className="flex items-center gap-4 text-text-secondary">
                          <div className="flex items-center gap-2 px-3 py-1.5 bg-bg rounded-full border border-border">
                            <span className="material-symbols-outlined text-[16px] text-brand">shield</span>
                            <span className="font-mono text-[11px] font-bold">Privacy Mode Active</span>
                          </div>
                          <div className="flex items-center gap-2 px-3 py-1.5 bg-bg rounded-full border border-border">
                            <span className="material-symbols-outlined text-[16px] text-brand">bolt</span>
                            <span className="font-mono text-[11px] font-bold">Real-time Check</span>
                          </div>
                        </div>
                        <PrimaryButton 
                          type="submit"
                          className="w-full md:w-auto px-8 py-3 text-sm"
                        >
                          <span>Verify Now</span>
                          <span className="material-symbols-outlined text-sm">arrow_forward</span>
                        </PrimaryButton>
                      </div>
                    </form>
                  )}

                  {/* Link Input Section */}
                  {activeTab === 'link' && (
                    <form onSubmit={handleAnalyze} className="space-y-6 py-8">
                      <div className="relative text-left">
                        <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-text-secondary/40">link</span>
                        <input 
                          required
                          value={content}
                          onChange={(e) => setContent(e.target.value)}
                          className="w-full pl-12 pr-4 py-4 bg-bg border border-border rounded-lg font-sans text-sm text-text-primary focus:outline-none focus:ring-1 focus:ring-brand focus:border-brand transition-all" 
                          placeholder="https://linkedin.com/jobs/view/..." 
                          type="text"
                        />
                      </div>
                      <p className="text-center font-mono text-[11px] text-text-secondary font-semibold">Paste the URL of a LinkedIn, Indeed, or company job posting.</p>
                      <PrimaryButton 
                        type="submit"
                        className="w-full py-3"
                      >
                        Analyze Link
                      </PrimaryButton>
                    </form>
                  )}

                  {/* Document Upload Section */}
                  {activeTab === 'document' && (
                    <form onSubmit={handleAnalyze} className="space-y-6">
                      <FileUploader
                        allowedType="pdf"
                        maxSizeBytes={10 * 1024 * 1024} // 10MB
                        onFileSelected={setSelectedFile}
                        selectedFile={selectedFile}
                        onClearFile={() => setSelectedFile(null)}
                      />
                      
                      <div className="flex justify-end pt-4 border-t border-border">
                        <PrimaryButton 
                          type="submit"
                          className="w-full md:w-auto px-8 py-3 text-sm"
                        >
                          Verify Document
                        </PrimaryButton>
                      </div>
                    </form>
                  )}
                </div>
              </Card>

              {/* Recent Analysis Preview */}
              <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
                <Card className="col-span-1 md:col-span-2">
                  <div className="flex justify-between items-center mb-6">
                    <h4 className="font-mono text-[11px] font-bold text-text-secondary tracking-widest uppercase">Analysis Insights</h4>
                    <span className="material-symbols-outlined text-text-secondary/40">info</span>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="flex items-center gap-4 p-3 bg-bg rounded-lg border border-border">
                      <div className="w-2 h-10 bg-danger rounded-full shrink-0"></div>
                      <div>
                        <p className="text-sm font-bold text-text-primary">Phishing Link Detected</p>
                        <p className="font-mono text-[10px] text-text-secondary mt-0.5">High-risk domain identified in last 24h</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4 p-3 bg-bg rounded-lg border border-border">
                      <div className="w-2 h-10 bg-success rounded-full shrink-0"></div>
                      <div>
                        <p className="text-sm font-bold text-text-primary">Verified Corporate Recruiter</p>
                        <p className="font-mono text-[10px] text-text-secondary mt-0.5">Domain matched with official registry</p>
                      </div>
                    </div>
                  </div>
                </Card>

                <Card className="col-span-1 flex flex-col items-center justify-center text-center">
                  <div className="relative w-24 h-24 mb-4 select-none">
                    <svg className="w-full h-full transform -rotate-90">
                      <circle className="text-border" cx="48" cy="48" fill="transparent" r="40" stroke="currentColor" strokeWidth="4"></circle>
                      <circle className="text-brand progress-ring__circle" cx="48" cy="48" fill="transparent" r="40" stroke="currentColor" strokeDasharray="251.2" strokeDashoffset="62.8" strokeWidth="4"></circle>
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center font-sans text-lg font-bold text-text-primary">75%</div>
                  </div>
                  <p className="font-mono text-[11px] text-brand font-bold mb-0.5">Safety Index</p>
                  <p className="font-mono text-[10px] text-text-secondary font-semibold">Community trust score</p>
                </Card>
              </div>
            </motion.div>
          ) : (
            // Processing Screen
            <motion.div
              key="loading-stage"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              className="rounded-2xl bg-card p-12 shadow-sm border border-border flex flex-col items-center justify-center text-center space-y-8 min-h-[400px]"
            >
              <div className="relative flex items-center justify-center">
                <div className="h-20 w-20 animate-spin rounded-full border-4 border-border border-t-brand"></div>
                <div className="absolute h-10 w-10 flex items-center justify-center">
                  <ShieldAlert className="h-6 w-6 text-brand animate-pulse" />
                </div>
              </div>

              <div className="space-y-4 max-w-md w-full">
                <h3 className="font-sans text-lg font-bold text-text-primary">Job Scam Check in Progress</h3>
                <div className="h-2 w-64 bg-bg border border-border rounded-full mx-auto overflow-hidden relative">
                  <motion.div 
                    className="h-full bg-brand rounded-full absolute left-0 top-0"
                    initial={{ width: '5%' }}
                    animate={{ width: `${(progressStep + 1) * (100 / pipelineSteps.length)}%` }}
                    transition={{ duration: 1.2 }}
                  />
                </div>
                
                <AnimatePresence mode="wait">
                  <motion.p
                    key={progressStep}
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -5 }}
                    className="font-mono text-[10px] text-text-secondary italic min-h-[16px] font-bold"
                  >
                    {pipelineSteps[progressStep]}
                  </motion.p>
                </AnimatePresence>
              </div>

              <div className="font-mono text-[10px] text-text-secondary font-bold leading-relaxed max-w-sm pt-4 border-t border-border">
                Please keep this tab open. The multi-signal scanner runs checks asynchronously to query domains and perform scoring.
              </div>
            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </Layout>
  );
};

export default NewAnalysisPage;
