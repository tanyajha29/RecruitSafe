import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, PieChart, Pie, Cell } from 'recharts';
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
  Clock,
  Sparkles,
  Zap,
  TrendingUp,
  Activity
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
        return 'bg-emerald-50 dark:bg-emerald-950/30 text-emerald-600 dark:text-emerald-400 border-emerald-100 dark:border-emerald-900/50';
      case 'Needs Verification':
        return 'bg-amber-50 dark:bg-amber-950/30 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-900/50';
      case 'Suspicious':
        return 'bg-orange-50 dark:bg-orange-950/30 text-orange-600 dark:text-orange-400 border-orange-100 dark:border-orange-900/50';
      case 'High Risk':
        return 'bg-red-50 dark:bg-red-950/30 text-red-600 dark:text-red-400 border-red-100 dark:border-red-900/50';
      default:
        return 'bg-slate-50 dark:bg-slate-800/40 text-slate-500 dark:text-slate-400 border-slate-100 dark:border-slate-800/50';
    }
  };

  // Compile trend data from recent analyses
  const getTrendData = () => {
    if (!stats || !stats.recent_analyses || stats.recent_analyses.length === 0) {
      return [
        { name: 'Jan', score: 90 },
        { name: 'Feb', score: 85 },
        { name: 'Mar', score: 92 },
        { name: 'Apr', score: 88 },
      ];
    }

    const items = [...stats.recent_analyses].reverse();
    return items.map((item, idx) => {
      const dateStr = new Date(item.created_at).toLocaleDateString(undefined, { 
        month: 'short', 
        day: 'numeric' 
      });
      return {
        name: dateStr,
        score: item.trust_score !== null ? item.trust_score : 70,
      };
    });
  };

  // Compile donut/pie data
  const getPieData = () => {
    if (!stats) return [];
    return [
      { name: 'Safe', value: stats.safe_count, color: '#2E7D32' },
      { name: 'Verification', value: stats.needs_verification_count, color: '#C6A27E' },
      { name: 'Suspicious', value: stats.suspicious_count, color: '#8B5E3C' },
      { name: 'High Risk', value: stats.high_risk_count, color: '#C53030' }
    ].filter(item => item.value > 0);
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.08 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 15 },
    show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } }
  };

  return (
    <Layout>
      <AnimatePresence mode="wait">
        {loading ? (
          <motion.div 
            key="skeleton"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-8"
          >
            {/* Banner Skeleton */}
            <div className="h-44 w-full rounded-2xl animate-shimmer"></div>
            {/* Stats Grid Skeleton */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-32 rounded-xl animate-shimmer"></div>
              ))}
            </div>
            {/* Content Split Skeleton */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              <div className="lg:col-span-8 h-80 rounded-2xl animate-shimmer"></div>
              <div className="lg:col-span-4 h-80 rounded-2xl animate-shimmer"></div>
            </div>
          </motion.div>
        ) : error ? (
          <motion.div 
            key="error"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex h-96 w-full flex-col items-center justify-center gap-4 text-center"
          >
            <AlertTriangle className="h-12 w-12 text-red-500" />
            <p className="text-slate-655 dark:text-slate-400 font-medium">{error}</p>
            <button
              onClick={fetchDashboardData}
              className="flex items-center gap-2 rounded-xl bg-indigo-650 hover:bg-indigo-700 text-white px-5 py-2.5 text-sm font-bold shadow-md shadow-indigo-600/10 transition-colors cursor-pointer"
            >
              <RefreshCw className="h-4 w-4 animate-spin-slow" />
              <span>Try Again</span>
            </button>
          </motion.div>
        ) : (
          <motion.div
            key="dashboard"
            variants={containerVariants}
            initial="hidden"
            animate="show"
            className="space-y-8"
          >
            {/* Welcome Banner Card */}
            <motion.div 
              variants={itemVariants}
              className="rounded-2xl bg-gradient-to-r from-indigo-600 via-indigo-750 to-violet-700 p-8 text-white shadow-xl shadow-indigo-600/10 flex flex-col lg:flex-row items-center justify-between gap-6 relative overflow-hidden"
            >
              <div className="absolute right-0 bottom-0 h-48 w-48 rounded-full bg-white/5 blur-3xl pointer-events-none"></div>
              <div className="absolute left-1/3 top-0 h-32 w-32 rounded-full bg-indigo-500/10 blur-2xl pointer-events-none"></div>
              
              <div className="space-y-2.5 text-center lg:text-left relative z-10">
                <div className="inline-flex items-center gap-1.5 rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-indigo-100 backdrop-blur-md">
                  <Sparkles className="h-3 w-3 text-indigo-300" />
                  <span>Next-Gen Scam Analysis v2.1</span>
                </div>
                <h2 className="text-2xl lg:text-3xl font-extrabold tracking-tight">Secure Your Job Search</h2>
                <p className="text-sm text-indigo-100 max-w-xl leading-relaxed">
                  Analyze description files, recruiter email domains, and company websites to expose fraud, identity theft, or payment traps in real time.
                </p>
              </div>
              
              <motion.div
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                className="shrink-0 z-10"
              >
                <Link
                  to="/analysis/new"
                  className="flex items-center gap-2 rounded-xl bg-white text-indigo-600 px-6 py-3.5 text-xs font-black shadow-lg shadow-indigo-900/10 hover:shadow-indigo-900/20 transition-all cursor-pointer"
                >
                  <Plus className="h-4 w-4 stroke-[3]" />
                  <span>START NEW CHECK</span>
                </Link>
              </motion.div>
            </motion.div>

            {/* Statistics Row */}
            <motion.div 
              variants={itemVariants}
              className="grid grid-cols-2 lg:grid-cols-4 gap-6"
            >
              <motion.div 
                whileHover={{ y: -6, transition: { duration: 0.2 } }}
                className="rounded-2xl bg-white dark:bg-slate-900 p-5 shadow-sm border border-slate-200/80 dark:border-slate-800/80 flex items-center gap-4 transition-colors duration-300"
              >
                <div className="h-12 w-12 flex items-center justify-center rounded-xl bg-slate-50 dark:bg-slate-800/40 text-slate-500 border border-slate-100 dark:border-slate-800/50">
                  <FileText className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-2xl font-black text-slate-850 dark:text-slate-100">{stats?.total_analyses}</p>
                  <p className="text-[10px] text-slate-400 dark:text-slate-500 font-bold uppercase tracking-wider mt-0.5">Total Checks</p>
                </div>
              </motion.div>

              <motion.div 
                whileHover={{ y: -6, transition: { duration: 0.2 } }}
                className="rounded-2xl bg-white dark:bg-slate-900 p-5 shadow-sm border border-slate-200/80 dark:border-slate-800/80 flex items-center gap-4 transition-colors duration-300"
              >
                <div className="h-12 w-12 flex items-center justify-center rounded-xl bg-red-50 dark:bg-red-950/20 text-red-500 border border-red-100 dark:border-red-900/40">
                  <ShieldAlert className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-2xl font-black text-slate-850 dark:text-slate-100">{stats?.high_risk_count}</p>
                  <p className="text-[10px] text-slate-400 dark:text-slate-500 font-bold uppercase tracking-wider mt-0.5">High Risk</p>
                </div>
              </motion.div>

              <motion.div 
                whileHover={{ y: -6, transition: { duration: 0.2 } }}
                className="rounded-2xl bg-white dark:bg-slate-900 p-5 shadow-sm border border-slate-200/80 dark:border-slate-800/80 flex items-center gap-4 transition-colors duration-300"
              >
                <div className="h-12 w-12 flex items-center justify-center rounded-xl bg-orange-50 dark:bg-orange-950/20 text-orange-500 border border-orange-100 dark:border-orange-900/40">
                  <AlertTriangle className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-2xl font-black text-slate-850 dark:text-slate-100">{stats?.suspicious_count}</p>
                  <p className="text-[10px] text-slate-400 dark:text-slate-500 font-bold uppercase tracking-wider mt-0.5">Suspicious</p>
                </div>
              </motion.div>

              <motion.div 
                whileHover={{ y: -6, transition: { duration: 0.2 } }}
                className="rounded-2xl bg-white dark:bg-slate-900 p-5 shadow-sm border border-slate-200/80 dark:border-slate-800/80 flex items-center gap-4 transition-colors duration-300"
              >
                <div className="h-12 w-12 flex items-center justify-center rounded-xl bg-emerald-50 dark:bg-emerald-950/20 text-emerald-500 border border-emerald-100 dark:border-emerald-900/40">
                  <Shield className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-2xl font-black text-slate-850 dark:text-slate-100">{stats?.safe_count}</p>
                  <p className="text-[10px] text-slate-400 dark:text-slate-500 font-bold uppercase tracking-wider mt-0.5">Safe Jobs</p>
                </div>
              </motion.div>
            </motion.div>

            {/* Content & Charts Split Grid */}
            <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start">
              
              {/* Left Side: Recent Checks list & Trend Analysis */}
              <div className="xl:col-span-8 space-y-8">
                


                {/* Table: Recent Checks */}
                <motion.div 
                  variants={itemVariants}
                  className="rounded-2xl bg-white dark:bg-slate-900 p-6 shadow-sm border border-slate-200/80 dark:border-slate-800/80 transition-colors duration-300"
                >
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-2">
                      <Activity className="h-5 w-5 text-indigo-650 dark:text-indigo-400" />
                      <h3 className="text-base font-bold text-slate-800 dark:text-slate-100">Recent Analyses</h3>
                    </div>
                    <Link to="/history" className="text-xs font-bold text-indigo-600 dark:text-indigo-455 hover:underline flex items-center gap-1">
                      <span>View History</span>
                      <ArrowRight className="h-3.5 w-3.5" />
                    </Link>
                  </div>

                  {stats?.recent_analyses.length === 0 ? (
                    <div className="py-12 text-center border border-dashed border-slate-200 dark:border-slate-800 rounded-2xl">
                      <p className="text-slate-400 dark:text-slate-500 text-sm font-medium">No job scam checks performed yet.</p>
                      <Link
                        to="/analysis/new"
                        className="inline-flex items-center gap-1.5 text-xs font-bold text-indigo-600 dark:text-indigo-400 mt-2 hover:underline"
                      >
                        <span>Analyze your first job now</span>
                        <ArrowRight className="h-3.5 w-3.5" />
                      </Link>
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full text-left border-collapse">
                        <thead>
                          <tr className="border-b border-slate-100 dark:border-slate-800 text-slate-400 dark:text-slate-500 font-bold text-xs uppercase tracking-wider">
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
                              className="border-b border-slate-50 dark:border-slate-850 last:border-0 hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors cursor-pointer group"
                            >
                              <td className="py-4 pl-2 font-bold text-xs text-slate-700 dark:text-slate-205 max-w-[200px] truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                                {item.original_content || 'Extracted File Text'}
                              </td>
                              <td className="py-4 text-xs font-semibold text-slate-400 dark:text-slate-500 capitalize">
                                {item.input_type}
                              </td>
                              <td className="py-4">
                                <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[10px] font-bold ${getRiskBadgeStyles(item.risk_category)}`}>
                                  {item.risk_category}
                                </span>
                              </td>
                              <td className="py-4 font-bold text-xs text-slate-700 dark:text-slate-200">
                                {item.trust_score !== null ? `${item.trust_score}/100` : '—'}
                              </td>
                              <td className="py-4 pr-2 text-xs font-semibold text-slate-400 dark:text-slate-500">
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
                </motion.div>
              </div>

              {/* Right Side: Circular Donut Chart Card */}
              <motion.div 
                variants={itemVariants}
                className="xl:col-span-4 rounded-2xl bg-white dark:bg-slate-900 p-6 shadow-sm border border-slate-200/80 dark:border-slate-800/80 transition-colors duration-300"
              >
                <h3 className="text-base font-bold text-slate-850 dark:text-slate-100 mb-6 text-center">Risk Distribution</h3>
                
                {stats?.total_analyses === 0 ? (
                  <div className="h-48 flex items-center justify-center border border-dashed border-slate-200 dark:border-slate-800 rounded-2xl">
                    <p className="text-slate-400 dark:text-slate-500 text-xs font-bold uppercase tracking-wider">No Checks Yet</p>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center">
                    <div className="h-48 w-full relative flex items-center justify-center">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={getPieData()}
                            cx="50%"
                            cy="50%"
                            innerRadius={55}
                            outerRadius={75}
                            paddingAngle={4}
                            dataKey="value"
                          >
                            {getPieData().map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                        </PieChart>
                      </ResponsiveContainer>
                      <div className="absolute text-center">
                        <p className="text-3xl font-black text-slate-800 dark:text-white leading-none">{stats?.total_analyses}</p>
                        <p className="text-[9px] text-slate-400 dark:text-slate-500 font-black uppercase tracking-wider mt-1.5">Total Checks</p>
                      </div>
                    </div>

                    {/* Slices legend listing */}
                    <div className="w-full mt-6 space-y-2 border-t border-slate-100 dark:border-slate-800 pt-4">
                      {Object.keys(stats?.risk_distribution || {}).map((key) => {
                        let color = '#E2E8F0';
                        if (key === 'Safe') color = '#2E7D32';
                        if (key === 'Needs Verification') color = '#C6A27E';
                        if (key === 'Suspicious') color = '#8B5E3C';
                        if (key === 'High Risk') color = '#C53030';
                        
                        return (
                          <div key={key} className="flex items-center justify-between text-xs font-semibold">
                            <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
                              <span className="h-2.5 w-2.5 rounded-full shrink-0" style={{ backgroundColor: color }}></span>
                              <span>{key}</span>
                            </div>
                            <span className="text-slate-800 dark:text-slate-205">{stats.risk_distribution[key]}%</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </Layout>
  );
};

export default DashboardPage;
