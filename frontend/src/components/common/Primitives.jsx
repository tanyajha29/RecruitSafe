import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Primary Button
export const PrimaryButton = ({ children, className = '', ...props }) => (
  <button
    className={`bg-brand hover:bg-[#754f32] text-white font-mono text-[13px] font-bold rounded-lg px-5 py-2.5 active:scale-98 transition-all cursor-pointer shadow-sm flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
    {...props}
  >
    {children}
  </button>
);

// Secondary Button
export const SecondaryButton = ({ children, className = '', ...props }) => (
  <button
    className={`bg-card border border-border text-text-primary hover:bg-bg/50 font-mono text-[13px] font-bold rounded-lg px-5 py-2.5 active:scale-98 transition-all cursor-pointer shadow-sm flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
    {...props}
  >
    {children}
  </button>
);

// Input Field
export const InputField = ({ label, error, className = '', ...props }) => (
  <div className="flex flex-col gap-1.5 w-full text-left">
    {label && <label className="font-mono text-[11px] font-bold text-text-secondary uppercase tracking-wider">{label}</label>}
    <input
      className={`bg-bg border border-border text-text-primary placeholder:text-text-secondary/40 rounded-lg px-4 py-3 focus:outline-none focus:ring-1 focus:ring-brand focus:border-brand transition-all w-full text-[14px] ${error ? 'border-danger focus:ring-danger focus:border-danger' : ''} ${className}`}
      {...props}
    />
    {error && <span className="font-mono text-[11px] text-danger">{error}</span>}
  </div>
);

// Text Area Field
export const TextArea = ({ label, error, className = '', ...props }) => (
  <div className="flex flex-col gap-1.5 w-full text-left">
    {label && <label className="font-mono text-[11px] font-bold text-text-secondary uppercase tracking-wider">{label}</label>}
    <textarea
      className={`bg-bg border border-border text-text-primary placeholder:text-text-secondary/40 rounded-lg p-4 focus:outline-none focus:ring-1 focus:ring-brand focus:border-brand transition-all w-full text-[14px] resize-none ${error ? 'border-danger focus:ring-danger focus:border-danger' : ''} ${className}`}
      {...props}
    />
    {error && <span className="font-mono text-[11px] text-danger">{error}</span>}
  </div>
);

// Premium Card
export const Card = ({ children, className = '', ...props }) => (
  <div
    className={`bg-card border border-border rounded-xl p-6 shadow-sm text-text-primary transition-all duration-300 ${className}`}
    {...props}
  >
    {children}
  </div>
);

// Section Title
export const SectionTitle = ({ children, subtitle, className = '', ...props }) => (
  <div className={`space-y-1 text-left ${className}`} {...props}>
    <h2 className="font-sans text-xl font-bold text-text-primary tracking-tight">{children}</h2>
    {subtitle && <p className="font-sans text-sm text-text-secondary">{subtitle}</p>}
  </div>
);

// Empty State Indicator
export const EmptyState = ({ icon: Icon, title, description, actionText, onAction, className = '' }) => (
  <div className={`flex flex-col items-center justify-center text-center p-12 border border-dashed border-border rounded-xl bg-card/50 ${className}`}>
    {Icon && <Icon className="h-10 w-10 text-text-secondary/45 mb-4 stroke-[1.5]" />}
    <h3 className="font-sans text-base font-bold text-text-primary mb-1">{title}</h3>
    <p className="font-sans text-sm text-text-secondary max-w-sm mb-6 leading-relaxed">{description}</p>
    {actionText && onAction && (
      <PrimaryButton onClick={onAction}>
        {actionText}
      </PrimaryButton>
    )}
  </div>
);

// Badge Status indicator
export const Badge = ({ children, variant = 'info', className = '' }) => {
  const styles = {
    info: 'bg-brand/10 text-brand border-brand/20',
    success: 'bg-success/10 text-success border-success/20',
    warning: 'bg-warning/10 text-warning border-warning/20',
    danger: 'bg-danger/10 text-danger border-danger/20',
    neutral: 'bg-text-secondary/10 text-text-secondary border-text-secondary/20',
  };
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full border text-[11px] font-mono font-medium uppercase tracking-wider ${styles[variant] || styles.info} ${className}`}>
      {children}
    </span>
  );
};

// Alert Info Callout
export const Alert = ({ children, title, variant = 'danger', onClose, className = '' }) => {
  const styles = {
    success: 'bg-success/5 border-success/30 text-success',
    warning: 'bg-warning/5 border-warning/30 text-warning',
    danger: 'bg-danger/5 border-danger/30 text-danger',
    info: 'bg-brand/5 border-brand/30 text-brand',
  };
  return (
    <div className={`border rounded-xl p-4 flex gap-3 text-left relative overflow-hidden ${styles[variant]} ${className}`}>
      <div className="flex-1 space-y-1">
        {title && <p className="font-sans text-[15px] font-bold leading-tight">{title}</p>}
        <div className="font-sans text-sm opacity-90 leading-relaxed">{children}</div>
      </div>
      {onClose && (
        <button onClick={onClose} className="text-current opacity-60 hover:opacity-100 transition-opacity self-start cursor-pointer">
          <span className="material-symbols-outlined text-sm">close</span>
        </button>
      )}
    </div>
  );
};

// Modal Shell
export const Modal = ({ isOpen, onClose, title, children, className = '' }) => (
  <AnimatePresence>
    {isOpen && (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        />
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className={`bg-card border border-border p-6 rounded-xl max-w-md w-full shadow-xl z-10 text-left relative ${className}`}
        >
          <div className="flex justify-between items-center mb-6">
            {title && <h3 className="font-sans text-lg font-bold text-text-primary">{title}</h3>}
            <button onClick={onClose} className="text-text-secondary hover:text-text-primary transition-colors cursor-pointer">
              <span className="material-symbols-outlined">close</span>
            </button>
          </div>
          {children}
        </motion.div>
      </div>
    )}
  </AnimatePresence>
);

// Progress Timeline Check
export const Timeline = ({ items = [], className = '' }) => (
  <div className={`relative space-y-8 before:content-[''] before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-[1px] before:bg-border ${className}`}>
    {items.map((item, index) => (
      <div key={index} className="relative pl-10 text-left">
        <div className="absolute left-0 top-1 w-6 h-6 rounded-full bg-card border border-border flex items-center justify-center">
          <div className={`w-2 h-2 rounded-full ${item.active ? 'bg-brand' : 'bg-text-secondary/40'}`} />
        </div>
        <div>
          <p className="font-mono text-[11px] text-text-secondary mb-1 uppercase tracking-widest">{item.label}</p>
          <p className="font-sans text-[15px] font-semibold text-text-primary">{item.title}</p>
          {item.description && <p className="font-sans text-xs text-text-secondary mt-1 leading-relaxed">{item.description}</p>}
        </div>
      </div>
    ))}
  </div>
);

// Radial Safety Index progress
export const ScoreRing = ({ score = 85, label = 'SAFE', className = '' }) => {
  const radius = 88;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  return (
    <div className={`relative flex items-center justify-center ${className}`}>
      <svg className="w-48 h-48">
        <circle className="text-border" cx="96" cy="96" fill="transparent" r={radius} stroke="currentColor" strokeWidth="4"></circle>
        <circle
          className="text-brand transition-all duration-1000 ease-out progress-ring__circle"
          cx="96"
          cy="96"
          fill="transparent"
          r={radius}
          stroke="currentColor"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          strokeWidth="4"
        ></circle>
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-sans text-[48px] font-bold text-text-primary leading-none">{score}%</span>
        <span className="font-mono text-[11px] font-bold text-text-secondary mt-1.5 uppercase tracking-wider">{label}</span>
      </div>
    </div>
  );
};
