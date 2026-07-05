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
  HelpCircle,
  ArrowRight,
  Sparkles
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
    { id: 'text', name: 'Job Description', icon: FileText, desc: 'Paste raw job posting text details', placeholder: 'Paste the raw job description here...' },
    { id: 'email', name: 'Recruiter Email', icon: Mail, desc: 'Analyze recruiter messages for phishing links', placeholder: 'Paste the recruiter\'s email content here (include headers if possible)...' },
    { id: 'url', name: 'Company Website', icon: Globe, desc: 'Check SSL and WHOIS registration age', placeholder: 'Enter the company\'s official website URL (e.g., https://example.com)...' },
    { id: 'pdf', name: 'PDF Offer Letter', icon: Upload, desc: 'Scan document text metadata for fraud clues' },
    { id: 'image', name: 'Screenshot / Image', icon: ImageIcon, desc: 'OCR scan of screenshots or banners' },
  ];

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
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              className="flex items-start gap-3 rounded-2xl bg-red-50 dark:bg-red-950/20 p-4 text-sm text-red-700 dark:text-red-400 border border-red-100 dark:border-red-900/40 shadow-sm"
            >
              <AlertTriangle className="h-5 w-5 shrink-0 text-red-500 mt-0.5" />
              <div className="space-y-1">
                <p className="font-bold">Check Failed</p>
                <p className="text-xs text-red-650 dark:text-red-400/90 leading-relaxed">{error}</p>
              </div>
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
              className="rounded-2xl bg-white dark:bg-slate-900 p-8 shadow-sm border border-slate-200/80 dark:border-slate-800/80 transition-colors duration-300"
            >
              <div className="mb-8">
                <div className="inline-flex items-center gap-1 bg-indigo-50 dark:bg-indigo-950/30 text-indigo-600 dark:text-indigo-400 px-3 py-1 rounded-full text-xs font-bold mb-3">
                  <Sparkles className="h-3.5 w-3.5" />
                  <span>Real-time Scans</span>
                </div>
                <h2 className="text-xl font-bold text-slate-850 dark:text-slate-100">Job Scam Scan Analyzer</h2>
                <p className="text-xs text-slate-400 dark:text-slate-500 font-medium mt-1">
                  Choose your input format, paste or upload, and our scanner will analyze company domains, text indicators, and AI trust scoring.
                </p>
              </div>

              {/* Tabs list selectors */}
              <div className="grid grid-cols-1 md:grid-cols-5 gap-3.5 mb-8">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  const isSelected = activeTab === tab.id;
                  return (
                    <motion.button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className={`flex flex-col items-center justify-center gap-2.5 py-4 px-3 rounded-2xl border font-bold text-[10px] uppercase tracking-wider transition-all duration-300 cursor-pointer ${
                        isSelected 
                          ? 'border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/30 text-indigo-605 dark:text-indigo-400 shadow-sm ring-4 ring-indigo-500/10' 
                          : 'border-slate-200 dark:border-slate-805 text-slate-400 dark:text-slate-500 hover:border-slate-350 dark:hover:border-slate-700 hover:bg-slate-50/50 dark:hover:bg-slate-800/30 hover:text-slate-650 dark:hover:text-slate-300'
                      }`}
                    >
                      <Icon className={`h-5 w-5 ${isSelected ? 'text-indigo-650 dark:text-indigo-400' : 'text-slate-400 dark:text-slate-500'}`} />
                      <span className="text-center">{tab.name}</span>
                    </motion.button>
                  );
                })}
              </div>

              {/* Form Input fields */}
              <form onSubmit={handleAnalyze} className="space-y-6">
                <div className="relative">
                  {['text', 'email'].includes(activeTab) && (
                    <textarea
                      required
                      rows={8}
                      value={content}
                      onChange={(e) => setContent(e.target.value)}
                      placeholder={tabs.find((t) => t.id === activeTab)?.placeholder}
                      className="w-full rounded-2xl border border-slate-205 dark:border-slate-800 p-5 text-sm text-slate-800 dark:text-slate-200 bg-white dark:bg-slate-900/60 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-600 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 resize-y min-h-[160px]"
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
                        className="w-full rounded-2xl border border-slate-205 dark:border-slate-800 py-4 pl-12 pr-5 text-sm text-slate-800 dark:text-slate-200 bg-white dark:bg-slate-900/60 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-600 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
                      />
                      <Globe className="absolute left-4 top-4 h-5 w-5 text-slate-405 dark:text-slate-600" />
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

                <div className="flex justify-end pt-4 border-t border-slate-100 dark:border-slate-800/80">
                  <motion.button
                    type="submit"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="flex items-center gap-2 rounded-2xl bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-600 dark:hover:bg-indigo-505 text-white font-bold text-sm px-6 py-3.5 shadow-lg shadow-indigo-600/15 dark:shadow-none transition-colors cursor-pointer"
                  >
                    <Play className="h-4 w-4 fill-white stroke-none" />
                    <span>Analyze Now</span>
                  </motion.button>
                </div>
              </form>
            </motion.div>
          ) : (
            // Processing Screen
            <motion.div
              key="loading-stage"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              className="rounded-2xl bg-white dark:bg-slate-900 p-12 shadow-sm border border-slate-200/80 dark:border-slate-800/80 flex flex-col items-center justify-center text-center space-y-8 min-h-[400px] transition-colors duration-300"
            >
              {/* Spinner */}
              <div className="relative flex items-center justify-center">
                <div className="h-20 w-20 animate-spin rounded-full border-4 border-slate-100 dark:border-slate-800 border-t-indigo-600"></div>
                <div className="absolute h-10 w-10 flex items-center justify-center">
                  <ShieldAlert className="h-6 w-6 text-indigo-600 animate-pulse" />
                </div>
              </div>

              {/* Progress Text */}
              <div className="space-y-4 max-w-md w-full">
                <h3 className="text-lg font-bold text-slate-850 dark:text-slate-100">Job Scam Check in Progress</h3>
                <div className="h-2 w-64 bg-slate-100 dark:bg-slate-800 rounded-full mx-auto overflow-hidden relative">
                  <motion.div 
                    className="h-full bg-indigo-605 rounded-full absolute left-0 top-0"
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
                    className="text-xs text-slate-500 dark:text-slate-400 font-semibold italic min-h-[16px]"
                  >
                    {pipelineSteps[progressStep]}
                  </motion.p>
                </AnimatePresence>
              </div>

              <div className="text-xs text-slate-400 dark:text-slate-500 font-medium leading-relaxed max-w-sm pt-4 border-t border-slate-100 dark:border-slate-800">
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
