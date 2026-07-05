import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../services/api';
import Layout from '../components/common/Layout';
import FileUploader from '../components/analysis/FileUploader';
import { 
  FileText, 
  Mail, 
  Globe, 
  Upload, 
  Image as ImageIcon, 
  ShieldAlert, 
  AlertTriangle,
  Play,
  CheckCircle,
  HelpCircle
} from 'lucide-react';

const NewAnalysisPage = () => {
  const [activeTab, setActiveTab] = useState('text'); // 'text', 'email', 'url', 'pdf', 'image'
  const [content, setContent] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  
  // Loading & Pipeline progress states
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisId, setAnalysisId] = useState(null);
  const [progressStep, setProgressStep] = useState(0);
  const [error, setError] = useState('');

  const navigate = useNavigate();

  const tabs = [
    { id: 'text', name: 'Job Description', icon: FileText, placeholder: 'Paste the raw job description here...' },
    { id: 'email', name: 'Recruiter Email', icon: Mail, placeholder: 'Paste the recruiter\'s email content here (include headers if possible)...' },
    { id: 'url', name: 'Company Website', icon: Globe, placeholder: 'Enter the company\'s official website URL (e.g., https://example.com)...' },
    { id: 'pdf', name: 'PDF Offer Letter', icon: Upload },
    { id: 'image', name: 'Screenshot / Image', icon: ImageIcon },
  ];

  const pipelineSteps = [
    "Uploading submission and registering job check...",
    "Extracting text details and cleaning horizontal whitespace...",
    "Running domain intelligence, WHOIS, and SSL queries...",
    "Parsing recruiter email and checking typosquatting indicators...",
    "Scanning rule-based triggers and matching financial fraud keywords...",
    "Consulting Gemini AI reasoning engine...",
    "Calculating composite trust score and safety audit recommendations..."
  ];

  useEffect(() => {
    // Clear content when changing tabs
    setContent('');
    setSelectedFile(null);
    setError('');
  }, [activeTab]);

  // Simulate pipeline step changes during backend polling
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
      }, 2500);
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
        setError('Connection lost while checking analysis status. Please check your internet or retry.');
      }
    }, 2000);
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setError('');
    setIsAnalyzing(true);
    setProgressStep(0);

    const formData = new FormData();
    formData.append('input_type', activeTab);

    if (['text', 'email', 'url'].includes(activeTab)) {
      if (!content || !content.trim()) {
        setError('Please fill in the input content field.');
        setIsAnalyzing(false);
        return;
      }
      formData.append('content', content);
    } else {
      if (!selectedFile) {
        setError('Please select a file to upload first.');
        setIsAnalyzing(false);
        return;
      }
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
      
      // Start polling the status
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
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Error Callout */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-start gap-3 rounded-xl bg-red-50 p-4 text-sm text-red-700 border border-red-100 shadow-sm"
          >
            <AlertTriangle className="h-5 w-5 shrink-0 text-red-500 mt-0.5" />
            <div className="space-y-1">
              <p className="font-bold">Check Failed</p>
              <p className="text-xs text-red-600/90 leading-relaxed">{error}</p>
            </div>
          </motion.div>
        )}

        <AnimatePresence mode="wait">
          {!isAnalyzing ? (
            <motion.div
              key="input-stage"
              initial={{ opacity: 0, scale: 0.99 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.99 }}
              className="rounded-2xl bg-white p-8 shadow-sm border border-slate-200/80"
            >
              <div className="mb-8">
                <h2 className="text-xl font-bold text-slate-800">Job Scam Scan Analyzer</h2>
                <p className="text-xs text-slate-400 font-medium mt-1">
                  Choose your input format, paste or upload, and our scanner will analyze company domains, text indicators, and AI trust scoring.
                </p>
              </div>

              {/* Tabs list selectors */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-2.5 mb-8">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  const isSelected = activeTab === tab.id;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`flex flex-col items-center justify-center gap-2 py-4 rounded-xl border font-bold text-[10px] uppercase tracking-wider transition-all duration-200 cursor-pointer ${
                        isSelected 
                          ? 'border-brand-500 bg-brand-500/5 text-brand-600 ring-2 ring-brand-500/10' 
                          : 'border-slate-200 text-slate-400 hover:border-slate-350 hover:bg-slate-50/50 hover:text-slate-600'
                      }`}
                    >
                      <Icon className={`h-5 w-5 ${isSelected ? 'text-brand-500' : 'text-slate-400'}`} />
                      <span>{tab.name}</span>
                    </button>
                  );
                })}
              </div>

              {/* Form Input fields */}
              <form onSubmit={handleAnalyze} className="space-y-8">
                <div>
                  {['text', 'email'].includes(activeTab) && (
                    <textarea
                      required
                      rows={8}
                      value={content}
                      onChange={(e) => setContent(e.target.value)}
                      placeholder={tabs.find((t) => t.id === activeTab)?.placeholder}
                      className="w-full rounded-xl border border-slate-200 p-4 text-sm text-slate-850 outline-none transition-all placeholder:text-slate-400 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 resize-y min-h-[160px]"
                    />
                  )}

                  {activeTab === 'url' && (
                    <div className="relative">
                      <input
                        required
                        type="text"
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        placeholder={tabs.find((t) => t.id === activeTab)?.placeholder}
                        className="w-full rounded-xl border border-slate-200 py-3.5 pl-12 pr-4 text-sm text-slate-850 outline-none transition-all placeholder:text-slate-400 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10"
                      />
                      <Globe className="absolute left-4 top-3.5 h-5 w-5 text-slate-400" />
                    </div>
                  )}

                  {activeTab === 'pdf' && (
                    <FileUploader
                      allowedType="pdf"
                      maxSizeBytes={20 * 1024 * 1024} // 20MB
                      onFileSelected={setSelectedFile}
                      selectedFile={selectedFile}
                      onClearFile={() => setSelectedFile(null)}
                    />
                  )}

                  {activeTab === 'image' && (
                    <FileUploader
                      allowedType="image"
                      maxSizeBytes={10 * 1024 * 1024} // 10MB
                      onFileSelected={setSelectedFile}
                      selectedFile={selectedFile}
                      onClearFile={() => setSelectedFile(null)}
                    />
                  )}
                </div>

                <div className="flex justify-end pt-2 border-t border-slate-100">
                  <button
                    type="submit"
                    className="flex items-center gap-2 rounded-xl bg-brand-500 hover:bg-brand-600 text-white font-bold text-sm px-6 py-3.5 shadow-lg shadow-brand-500/20 transition-all hover:scale-[1.02] cursor-pointer"
                  >
                    <Play className="h-4 w-4 fill-white stroke-none" />
                    <span>Analyze Now</span>
                  </button>
                </div>
              </form>
            </motion.div>
          ) : (
            // Processing Screen
            <motion.div
              key="loading-stage"
              initial={{ opacity: 0, scale: 0.99 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.99 }}
              className="rounded-2xl bg-white p-12 shadow-sm border border-slate-200/80 flex flex-col items-center justify-center text-center space-y-8 min-h-[400px]"
            >
              {/* Spinner */}
              <div className="relative flex items-center justify-center">
                <div className="h-20 w-20 animate-spin rounded-full border-4 border-slate-100 border-t-brand-500"></div>
                <div className="absolute h-10 w-10 flex items-center justify-center">
                  <ShieldAlert className="h-6 w-6 text-brand-500 animate-pulse" />
                </div>
              </div>

              {/* Progress Text */}
              <div className="space-y-3 max-w-md">
                <h3 className="text-lg font-bold text-slate-800">Job Scam Check in Progress</h3>
                <div className="h-1.5 w-64 bg-slate-100 rounded-full mx-auto overflow-hidden relative">
                  <motion.div 
                    className="h-full bg-brand-500 rounded-full absolute left-0 top-0"
                    initial={{ width: '5%' }}
                    animate={{ width: `${(progressStep + 1) * (100 / pipelineSteps.length)}%` }}
                    transition={{ duration: 1.5 }}
                  />
                </div>
                
                <AnimatePresence mode="wait">
                  <motion.p
                    key={progressStep}
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -5 }}
                    className="text-xs text-slate-500 font-semibold italic min-h-[16px]"
                  >
                    {pipelineSteps[progressStep]}
                  </motion.p>
                </AnimatePresence>
              </div>

              <div className="text-xs text-slate-400 font-medium leading-relaxed max-w-sm pt-4 border-t border-slate-50">
                Please keep this tab open. The multi-signal scanner runs asynchronously to query domains and perform scoring checks.
              </div>
            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </Layout>
  );
};

export default NewAnalysisPage;
