import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '../services/api';
import Layout from '../components/common/Layout';
import { 
  FileText, 
  ShieldAlert, 
  Shield, 
  Plus, 
  AlertTriangle,
  ArrowRight,
  RefreshCw,
  Clock
} from 'lucide-react';

const DashboardPage = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const fetchDashboardData = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get('/api/dashboard');
      setStats(response.data);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError('Could not load statistics. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const getRiskBadgeStyles = (category) => {
    switch (category) {
      case 'Safe':
        return 'bg-emerald-50 text-emerald-600 border-emerald-100';
      case 'Needs Verification':
        return 'bg-yellow-50 text-yellow-600 border-yellow-100';
      case 'Suspicious':
        return 'bg-orange-50 text-orange-600 border-orange-100';
      case 'High Risk':
        return 'bg-red-50 text-red-600 border-red-100';
      default:
        return 'bg-slate-50 text-slate-500 border-slate-100';
    }
  };

  const getRiskDotColor = (category) => {
    switch (category) {
      case 'Safe': return 'bg-emerald-500';
      case 'Needs Verification': return 'bg-yellow-500';
      case 'Suspicious': return 'bg-orange-500';
      case 'High Risk': return 'bg-red-500';
      default: return 'bg-slate-400';
    }
  };

  // Helper to render pure SVG Donut Chart slices
  const renderDonutChart = () => {
    if (!stats) return null;
    
    const { safe_count, needs_verification_count, suspicious_count, high_risk_count, total_analyses } = stats;
    
    if (total_analyses === 0) {
      return (
        <svg width="150" height="150" viewBox="0 0 100 100" className="mx-auto">
          <circle cx="50" cy="50" r="38" fill="transparent" stroke="#E2E8F0" strokeWidth="10" />
          <text x="50" y="54" textAnchor="middle" className="text-[12px] font-bold fill-slate-400">0 Checks</text>
        </svg>
      );
    }

    const circumference = 2 * Math.PI * 38; // ~238.76
    
    // Percentages
    const pSafe = safe_count / total_analyses;
    const pNeeds = needs_verification_count / total_analyses;
    const pSuspicious = suspicious_count / total_analyses;
    const pHigh = high_risk_count / total_analyses;

    // Dash lengths
    const dSafe = pSafe * circumference;
    const dNeeds = pNeeds * circumference;
    const dSuspicious = pSuspicious * circumference;
    const dHigh = pHigh * circumference;

    // Cumulative offsets
    const oHigh = 0;
    const oSuspicious = dHigh;
    const oNeeds = dHigh + dSuspicious;
    const oSafe = dHigh + dSuspicious + dNeeds;

    return (
      <div className="relative flex items-center justify-center">
        <svg width="160" height="160" viewBox="0 0 100 100" className="transform -rotate-90">
          {/* Base Track */}
          <circle cx="50" cy="50" r="38" fill="transparent" stroke="#F1F5F9" strokeWidth="8" />
          
          {/* High Risk slice (Red) */}
          {dHigh > 0 && (
            <circle
              cx="50"
              cy="50"
              r="38"
              fill="transparent"
              stroke="#EF4444"
              strokeWidth="8"
              strokeDasharray={`${dHigh} ${circumference}`}
              strokeDashoffset={-oHigh}
              className="transition-all duration-500"
            />
          )}
          {/* Suspicious slice (Orange) */}
          {dSuspicious > 0 && (
            <circle
              cx="50"
              cy="50"
              r="38"
              fill="transparent"
              stroke="#F97316"
              strokeWidth="8"
              strokeDasharray={`${dSuspicious} ${circumference}`}
              strokeDashoffset={-oSuspicious}
              className="transition-all duration-500"
            />
          )}
          {/* Needs Verification slice (Yellow) */}
          {dNeeds > 0 && (
            <circle
              cx="50"
              cy="50"
              r="38"
              fill="transparent"
              stroke="#EAB308"
              strokeWidth="8"
              strokeDasharray={`${dNeeds} ${circumference}`}
              strokeDashoffset={-oNeeds}
              className="transition-all duration-500"
            />
          )}
          {/* Safe slice (Green) */}
          {dSafe > 0 && (
            <circle
              cx="50"
              cy="50"
              r="38"
              fill="transparent"
              stroke="#10B981"
              strokeWidth="8"
              strokeDasharray={`${dSafe} ${circumference}`}
              strokeDashoffset={-oSafe}
              className="transition-all duration-500"
            />
          )}
        </svg>
        
        {/* Center label */}
        <div className="absolute text-center">
          <p className="text-3xl font-extrabold text-slate-800">{total_analyses}</p>
          <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Total Checks</p>
        </div>
      </div>
    );
  };

  return (
    <Layout>
      {loading ? (
        <div className="flex h-96 w-full items-center justify-center">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-brand-500 border-t-transparent"></div>
        </div>
      ) : error ? (
        <div className="flex h-96 w-full flex-col items-center justify-center gap-4 text-center">
          <AlertTriangle className="h-12 w-12 text-red-500" />
          <p className="text-slate-600 font-medium">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2 text-sm font-bold text-white transition-all hover:bg-brand-600 cursor-pointer"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Try Again</span>
          </button>
        </div>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className="space-y-8"
        >
          {/* Welcome Banner Card */}
          <div className="rounded-2xl bg-gradient-to-r from-brand-600 to-indigo-600 p-8 text-white shadow-xl shadow-brand-500/10 flex flex-col md:flex-row items-center justify-between gap-6 relative overflow-hidden">
            {/* Ambient design graphics */}
            <div className="absolute right-0 bottom-0 h-48 w-48 rounded-full bg-white/5 blur-2xl pointer-events-none"></div>
            
            <div className="space-y-2 text-center md:text-left">
              <h2 className="text-2xl font-bold">Secure Your Job Search</h2>
              <p className="text-sm text-indigo-100 max-w-lg leading-relaxed">
                RecruitSafe analyzes documents, links, and text description fields to detect identity theft or registration fee traps. Check new jobs before giving out sensitive details.
              </p>
            </div>
            
            <Link
              to="/analysis/new"
              className="flex items-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-bold text-brand-600 shadow-md transition-all hover:scale-[1.02] cursor-pointer shrink-0"
            >
              <Plus className="h-4.5 w-4.5 stroke-[2.5]" />
              <span>Start New Check</span>
            </Link>
          </div>

          {/* Core Content Grid */}
          <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start">
            
            {/* Left Col: Recent Checks Table */}
            <div className="xl:col-span-8 space-y-6">
              <div className="rounded-2xl bg-white p-6 shadow-sm border border-slate-200/80">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-bold text-slate-800">Recent Checks</h3>
                  <Link to="/history" className="text-xs font-bold text-brand-600 hover:text-brand-500 flex items-center gap-1">
                    <span>View History</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                </div>

                {stats?.recent_analyses.length === 0 ? (
                  <div className="py-12 text-center">
                    <p className="text-slate-400 font-medium">No job scam checks performed yet.</p>
                    <Link
                      to="/analysis/new"
                      className="inline-flex items-center gap-1.5 text-xs font-bold text-brand-600 hover:text-brand-500 mt-2"
                    >
                      <span>Analyze your first job now</span>
                      <ArrowRight className="h-3.5 w-3.5" />
                    </Link>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="border-b border-slate-100 text-slate-400 font-bold text-xs uppercase tracking-wider">
                          <th className="pb-3 pl-2">Job Preview</th>
                          <th className="pb-3">Type</th>
                          <th className="pb-3">Risk Level</th>
                          <th className="pb-3">Score</th>
                          <th className="pb-3 pr-2">Date Checked</th>
                        </tr>
                      </thead>
                      <tbody>
                        {stats?.recent_analyses.map((item) => (
                          <tr 
                            key={item.id} 
                            onClick={() => navigate(`/analysis/${item.id}`)}
                            className="border-b border-slate-50 last:border-0 hover:bg-slate-50/60 transition-colors cursor-pointer group"
                          >
                            <td className="py-4 pl-2 font-bold text-sm text-slate-700 max-w-xs truncate group-hover:text-brand-600 transition-colors">
                              {item.original_content || 'Extracted File Text'}
                            </td>
                            <td className="py-4 text-xs font-semibold text-slate-400 capitalize">
                              {item.input_type}
                            </td>
                            <td className="py-4">
                              <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${getRiskBadgeStyles(item.risk_category)}`}>
                                {item.risk_category}
                              </span>
                            </td>
                            <td className="py-4 font-bold text-sm text-slate-700">
                              {item.trust_score !== null ? `${item.trust_score}/100` : '—'}
                            </td>
                            <td className="py-4 pr-2 text-xs font-semibold text-slate-400">
                              {new Date(item.created_at).toLocaleDateString(undefined, {
                                month: 'short',
                                day: 'numeric',
                                year: 'numeric'
                              })}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>

            {/* Right Col: Stats Card list & Circular Chart */}
            <div className="xl:col-span-4 space-y-8">
              {/* Stats Numerical indicators */}
              <div className="grid grid-cols-2 gap-4">
                <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-200/80 flex flex-col justify-between">
                  <div className="h-8 w-8 flex items-center justify-center rounded-lg bg-slate-50 text-slate-500 border border-slate-100 mb-4">
                    <FileText className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-2xl font-black text-slate-800">{stats?.total_analyses}</p>
                    <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider mt-1">Total Checks</p>
                  </div>
                </div>

                <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-200/80 flex flex-col justify-between">
                  <div className="h-8 w-8 flex items-center justify-center rounded-lg bg-red-50 text-red-500 border border-red-100 mb-4">
                    <ShieldAlert className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-2xl font-black text-slate-800">{stats?.high_risk_count}</p>
                    <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider mt-1">High Risk</p>
                  </div>
                </div>

                <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-200/80 flex flex-col justify-between">
                  <div className="h-8 w-8 flex items-center justify-center rounded-lg bg-orange-50 text-orange-500 border border-orange-100 mb-4">
                    <AlertTriangle className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-2xl font-black text-slate-800">{stats?.suspicious_count}</p>
                    <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider mt-1">Suspicious</p>
                  </div>
                </div>

                <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-200/80 flex flex-col justify-between">
                  <div className="h-8 w-8 flex items-center justify-center rounded-lg bg-emerald-50 text-emerald-500 border border-emerald-100 mb-4">
                    <Shield className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-2xl font-black text-slate-800">{stats?.safe_count}</p>
                    <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider mt-1">Safe Jobs</p>
                  </div>
                </div>
              </div>

              {/* Circular Risk Distribution Donut Chart card */}
              <div className="rounded-2xl bg-white p-6 shadow-sm border border-slate-200/80">
                <h3 className="text-base font-bold text-slate-800 mb-6 text-center">Risk Distribution</h3>
                
                {renderDonutChart()}

                {/* Slices legend listing */}
                {stats?.total_analyses > 0 && (
                  <div className="mt-6 space-y-2 border-t border-slate-100 pt-4">
                    <div className="flex items-center justify-between text-xs font-semibold">
                      <div className="flex items-center gap-2 text-slate-500">
                        <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 shrink-0"></span>
                        <span>Safe</span>
                      </div>
                      <span className="text-slate-800">{stats?.risk_distribution['Safe']}%</span>
                    </div>

                    <div className="flex items-center justify-between text-xs font-semibold">
                      <div className="flex items-center gap-2 text-slate-500">
                        <span className="h-2.5 w-2.5 rounded-full bg-yellow-500 shrink-0"></span>
                        <span>Needs Verification</span>
                      </div>
                      <span className="text-slate-800">{stats?.risk_distribution['Needs Verification']}%</span>
                    </div>

                    <div className="flex items-center justify-between text-xs font-semibold">
                      <div className="flex items-center gap-2 text-slate-500">
                        <span className="h-2.5 w-2.5 rounded-full bg-orange-500 shrink-0"></span>
                        <span>Suspicious</span>
                      </div>
                      <span className="text-slate-800">{stats?.risk_distribution['Suspicious']}%</span>
                    </div>

                    <div className="flex items-center justify-between text-xs font-semibold">
                      <div className="flex items-center gap-2 text-slate-500">
                        <span className="h-2.5 w-2.5 rounded-full bg-red-500 shrink-0"></span>
                        <span>High Risk</span>
                      </div>
                      <span className="text-slate-800">{stats?.risk_distribution['High Risk']}%</span>
                    </div>
                  </div>
                )}
              </div>
            </div>

          </div>
        </motion.div>
      )}
    </Layout>
  );
};

export default DashboardPage;
