import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, Image as ImageIcon, X, AlertCircle } from 'lucide-react';

const FileUploader = ({ allowedType, maxSizeBytes, onFileSelected, selectedFile, onClearFile }) => {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState('');
  const inputRef = useRef(null);

  const getFormatHelpText = () => {
    return allowedType === 'pdf' ? 'PDF (max 20MB)' : 'PNG, JPG, JPEG (max 10MB)';
  };

  const validateAndSelectFile = (file) => {
    setError('');
    if (!file) return;

    // Check extension
    const ext = file.name.split('.').pop().toLowerCase();
    const isPDF = ext === 'pdf';
    const isImage = ['png', 'jpg', 'jpeg'].includes(ext);

    if (allowedType === 'pdf' && !isPDF) {
      setError('Invalid file type. Please upload a PDF document.');
      return;
    }
    if (allowedType === 'image' && !isImage) {
      setError('Invalid file type. Please upload a PNG, JPG, or JPEG image.');
      return;
    }

    // Check size
    if (file.size > maxSizeBytes) {
      const maxMb = maxSizeBytes / (1024 * 1024);
      setError(`File is too large. Maximum allowed size is ${maxMb}MB.`);
      return;
    }

    onFileSelected(file);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSelectFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndSelectFile(e.target.files[0]);
    }
  };

  const triggerFileInput = () => {
    inputRef.current.click();
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = 2;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-4">
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-xs font-semibold text-red-600 border border-red-100"
        >
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </motion.div>
      )}

      <input
        ref={inputRef}
        type="file"
        className="hidden"
        accept={allowedType === 'pdf' ? '.pdf' : '.png,.jpg,.jpeg'}
        onChange={handleChange}
      />

      <AnimatePresence mode="wait">
        {!selectedFile ? (
          <motion.div
            key="dropzone"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            onClick={triggerFileInput}
            className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center gap-3 cursor-pointer transition-all ${
              dragActive 
                ? 'border-brand-500 bg-brand-500/5' 
                : 'border-slate-200 hover:border-slate-350 hover:bg-slate-50/50'
            }`}
          >
            <div className="h-12 w-12 rounded-full bg-slate-50 flex items-center justify-center border border-slate-100 text-slate-400">
              <Upload className="h-6 w-6 stroke-[1.75]" />
            </div>
            
            <div className="text-center">
              <p className="text-sm font-bold text-slate-700">
                Drag & drop a file here or <span className="text-brand-600 hover:text-brand-500 transition-colors">browse files</span>
              </p>
              <p className="text-xs text-slate-400 mt-1 font-medium">{getFormatHelpText()}</p>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="file-details"
            initial={{ scale: 0.98, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.98, opacity: 0 }}
            className="flex items-center justify-between rounded-xl border border-slate-200 p-4 bg-slate-50/50"
          >
            <div className="flex items-center gap-3 min-w-0">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-brand-50 text-brand-500 border border-brand-100 shrink-0">
                {allowedType === 'pdf' ? (
                  <FileText className="h-5 w-5" />
                ) : (
                  <ImageIcon className="h-5 w-5" />
                )}
              </div>
              <div className="min-w-0">
                <p className="text-sm font-bold text-slate-700 truncate">{selectedFile.name}</p>
                <p className="text-xs text-slate-400 mt-0.5 font-semibold uppercase tracking-wider">
                  {formatFileSize(selectedFile.size)}
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onClearFile();
              }}
              className="h-8 w-8 rounded-lg hover:bg-slate-100 flex items-center justify-center text-slate-400 hover:text-slate-600 transition-colors cursor-pointer"
            >
              <X className="h-4 w-4" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FileUploader;
