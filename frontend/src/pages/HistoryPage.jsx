import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../services/api';
import Layout from '../components/common/Layout';
import { 
  Search, 
  Trash2, 
  Eye, 
  AlertTriangle, 
  Calendar,
  Layers,
  ChevronLeft,
  ChevronRight,
  Shield,
  Clock,
  Filter,
  Sparkles
} from 'lucide-react';

const HistoryPage = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Search & Filtering
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('');
  
  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const perPage = 8;

  const navigate = useNavigate();

  const fetchHistory = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get('/api/history', {
        params: {
          page,
          per_page: perPage,
          q: searchTerm,
          risk_category: filterCategory
        }
      });
      
      const { analyses, total } = response.data;
      setHistory(analyses);
      setTotalItems(total);
      setTotalPages(Math.ceil(total / perPage) || 1);
    } catch (err) {
      console.error('Failed to fetch history:', err);
      setError('Could not load analysis history. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchHistory();
  };

  const handleResetFilters = () => {
    setSearchTerm('');
    setFilterCategory('');
    setPage(1);
    setTimeout(() => fetchHistory(), 0);
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this scan from history?')) {
      return;
    }
    try {
      await api.delete(`/api/analyze/${id}`);
      fetchHistory();
    } catch (err) {
      console.error(err);
      alert('Failed to delete report. Please try again.');
    }
  };

  const getRiskBadgeStyles = (category) => {
    switch (category) {
      case 'Safe':
        return 'bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400 border-emerald-100 dark:border-emerald-900/40';
      case 'Needs Verification':
        return 'bg-amber-50 dark:bg-amber-955/20 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-900/40';
      case 'Suspicious':
        return 'bg-orange-50 dark:bg-orange-955/20 text-orange-605 dark:text-orange-400 border-orange-100 dark:border-orange-900/40';
      case 'High Risk':
        return 'bg-red-50 dark:bg-red-955/20 text-red-600 dark:text-red-400 border-red-105 dark:border-red-900/40';
      default:
        return 'bg-slate-50 dark:bg-slate-800/40 text-slate-500 dark:text-slate-400 border-slate-105 dark:border-slate-800/50';
    }
  };

  return (
    <Layout>
      <div className="space-y-6 max-w-5xl mx-auto">
        
        {/* Search & Filter Bar */}
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl bg-white dark:bg-slate-900 p-6 shadow-sm border border-slate-200/80 dark:border-slate-800/80 transition-colors duration-300"
        >
          <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row items-center gap-4">
            
            {/* Search Input */}
            <div className="relative flex-1 w-full">
              <input
                type="text"
                placeholder="Search scans (keywords, company, titles)..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full rounded-2xl border border-slate-200 dark:border-slate-800 py-3.5 pl-10 pr-4 text-xs text-slate-800 dark:text-slate-200 bg-white dark:bg-slate-900/60 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-600 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
              />
              <Search className="absolute left-3.5 top-3.5 h-4.5 w-4.5 text-slate-400 dark:text-slate-600" />
            </div>

            {/* Risk Category Filter */}
            <div className="relative w-full md:w-56">
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="w-full rounded-2xl border border-slate-200 dark:border-slate-800 py-3.5 pl-9 pr-8 text-xs text-slate-700 dark:text-slate-300 outline-none transition-all focus:border-indigo-505 bg-white dark:bg-slate-900/60 appearance-none cursor-pointer font-bold"
              >
                <option value="">All Risk Categories</option>
                <option value="Safe">Safe</option>
                <option value="Needs Verification">Needs Verification</option>
                <option value="Suspicious">Suspicious</option>
                <option value="High Risk">High Risk</option>
              </select>
              <Filter className="absolute left-3 top-3.5 h-4 w-4 text-slate-400 dark:text-slate-600 pointer-events-none" />
              <div className="absolute right-3.5 top-4.5 h-0 w-0 border-4 border-transparent border-t-slate-400 pointer-events-none" />
            </div>

            {/* Action buttons */}
            <div className="flex items-center gap-2.5 w-full md:w-auto">
              <motion.button
                type="submit"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="flex-1 md:flex-none flex items-center justify-center gap-1.5 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs px-5 py-3.5 shadow-md shadow-indigo-600/10 dark:shadow-none transition-colors cursor-pointer"
              >
                Apply
              </motion.button>
              <motion.button
                type="button"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleResetFilters}
                className="flex-1 md:flex-none flex items-center justify-center gap-1.5 rounded-2xl border border-slate-200 dark:border-slate-800 hover:border-slate-350 dark:hover:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-850 text-slate-600 dark:text-slate-400 font-bold text-xs px-4.5 py-3.5 transition-colors cursor-pointer"
              >
                Reset
              </motion.button>
            </div>

          </form>
        </motion.div>

        {/* History Results list */}
        {loading ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-48 rounded-2xl animate-shimmer"></div>
              ))}
            </div>
          </div>
        ) : error ? (
          <div className="py-12 text-center text-red-500 font-semibold">{error}</div>
        ) : history.length === 0 ? (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="rounded-2xl bg-white dark:bg-slate-900 p-12 text-center border border-slate-200/80 dark:border-slate-800/80 transition-colors duration-300"
          >
            <Layers className="h-10 w-10 text-slate-300 dark:text-slate-700 mx-auto mb-4 stroke-[1.5]" />
            <p className="text-slate-400 dark:text-slate-500 font-semibold text-sm">No analysis matching your search criteria found.</p>
            {(searchTerm || filterCategory) && (
              <button
                onClick={handleResetFilters}
                className="text-xs font-bold text-indigo-650 dark:text-indigo-400 hover:underline mt-2 cursor-pointer"
              >
                Clear all filters and search again
              </button>
            )}
          </motion.div>
        ) : (
          <div className="space-y-6">
            <motion.div 
              initial="hidden"
              animate="show"
              variants={{
                hidden: {},
                show: { transition: { staggerChildren: 0.05 } }
              }}
              className="grid grid-cols-1 md:grid-cols-2 gap-4"
            >
              {history.map((item) => (
                <motion.div
                  key={item.id}
                  onClick={() => navigate(`/analysis/${item.id}`)}
                  variants={{
                    hidden: { opacity: 0, y: 10 },
                    show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } }
                  }}
                  whileHover={{ y: -4, transition: { duration: 0.15 } }}
                  className="rounded-2xl bg-white dark:bg-slate-900 p-5 border border-slate-200/80 dark:border-slate-800/85 hover:border-slate-300 dark:hover:border-slate-705 hover:shadow-md hover:shadow-slate-100 dark:hover:shadow-none transition-all cursor-pointer flex flex-col justify-between h-48 relative group"
                >
                  {/* Top */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between gap-4">
                      <span className="text-[9px] text-slate-450 dark:text-slate-500 font-bold uppercase tracking-wider bg-slate-50 dark:bg-slate-850/50 border border-slate-100 dark:border-slate-800 rounded-lg px-2 py-0.5">
                        {item.input_type} Check
                      </span>
                      
                      {/* Delete Action button */}
                      <button
                        onClick={(e) => handleDelete(e, item.id)}
                        className="h-7 w-7 rounded-lg hover:bg-red-500/10 text-slate-400 hover:text-red-500 flex items-center justify-center transition-colors cursor-pointer md:opacity-0 group-hover:opacity-100"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>

                    <h4 className="text-sm font-extrabold text-slate-800 dark:text-slate-200 line-clamp-2 pr-6 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                      {item.original_content || "Text Input Block"}
                    </h4>
                  </div>

                  {/* Bottom */}
                  <div className="border-t border-slate-50 dark:border-slate-850 pt-3 flex items-center justify-between text-xs">
                    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[9px] font-bold ${getRiskBadgeStyles(item.risk_category)}`}>
                      {item.risk_category}
                    </span>
                    
                    <div className="flex items-center gap-1.5 text-slate-400 dark:text-slate-500 font-bold text-[9.5px]">
                      <Calendar className="h-3.5 w-3.5 text-slate-400" />
                      <span>
                        {new Date(item.created_at).toLocaleDateString(undefined, {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric'
                        })}
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between border-t border-slate-100 dark:border-slate-800 pt-6">
                <p className="text-xs text-slate-400 dark:text-slate-500 font-semibold">
                  Showing <span className="font-bold text-slate-600 dark:text-slate-400">{(page - 1) * perPage + 1}</span> to{' '}
                  <span className="font-bold text-slate-600 dark:text-slate-400">
                    {Math.min(page * perPage, totalItems)}
                  </span>{' '}
                  of <span className="font-bold text-slate-600 dark:text-slate-400">{totalItems}</span> scans
                </p>

                <div className="flex items-center gap-1.5">
                  <button
                    disabled={page === 1}
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    className="h-8 w-8 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-slate-350 dark:hover:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 flex items-center justify-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                  >
                    <ChevronLeft className="h-4.5 w-4.5" />
                  </button>
                  
                  <span className="text-xs font-bold text-slate-750 dark:text-slate-450 px-3">
                    Page {page} of {totalPages}
                  </span>

                  <button
                    disabled={page === totalPages}
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    className="h-8 w-8 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-slate-350 dark:hover:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 flex items-center justify-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                  >
                    <ChevronRight className="h-4.5 w-4.5" />
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

      </div>
    </Layout>
  );
};

export default HistoryPage;
