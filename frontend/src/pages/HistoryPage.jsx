import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
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
  Filter
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
    // Trigger update immediately
    setTimeout(() => fetchHistory(), 0);
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation(); // Stop navigation click
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

  return (
    <Layout>
      <div className="space-y-6 max-w-5xl mx-auto">
        
        {/* Search & Filter Bar */}
        <div className="rounded-2xl bg-white p-6 shadow-sm border border-slate-200/80">
          <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row items-center gap-4">
            
            {/* Search Input */}
            <div className="relative flex-1 w-full">
              <input
                type="text"
                placeholder="Search scans (keywords, company, titles)..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full rounded-lg border border-slate-200 py-2.5 pl-10 pr-4 text-xs text-slate-800 outline-none transition-all placeholder:text-slate-400 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10"
              />
              <Search className="absolute left-3.5 top-3.5 h-4.5 w-4.5 text-slate-400" />
            </div>

            {/* Risk Category Filter */}
            <div className="relative w-full md:w-56">
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="w-full rounded-lg border border-slate-200 py-2.5 pl-9 pr-4 text-xs text-slate-700 outline-none transition-all focus:border-brand-500 bg-white appearance-none cursor-pointer font-semibold"
              >
                <option value="">All Risk Categories</option>
                <option value="Safe">Safe</option>
                <option value="Needs Verification">Needs Verification</option>
                <option value="Suspicious">Suspicious</option>
                <option value="High Risk">High Risk</option>
              </select>
              <Filter className="absolute left-3 top-3.5 h-4 w-4 text-slate-400 pointer-events-none" />
              <div className="absolute right-3.5 top-4 h-0 w-0 border-4 border-transparent border-t-slate-400 pointer-events-none" />
            </div>

            {/* Action buttons */}
            <div className="flex items-center gap-2 w-full md:w-auto">
              <button
                type="submit"
                className="flex-1 md:flex-none flex items-center justify-center gap-1.5 rounded-lg bg-brand-500 hover:bg-brand-600 text-white font-bold text-xs px-5 py-2.5 transition-colors cursor-pointer"
              >
                Apply
              </button>
              <button
                type="button"
                onClick={handleResetFilters}
                className="flex-1 md:flex-none flex items-center justify-center gap-1.5 rounded-lg border border-slate-200 hover:border-slate-350 hover:bg-slate-50 text-slate-600 font-bold text-xs px-4 py-2.5 transition-colors cursor-pointer"
              >
                Reset
              </button>
            </div>

          </form>
        </div>

        {/* History Results list */}
        {loading ? (
          <div className="flex h-64 w-full items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent"></div>
          </div>
        ) : error ? (
          <div className="py-12 text-center text-red-500 font-medium">{error}</div>
        ) : history.length === 0 ? (
          <div className="rounded-2xl bg-white p-12 text-center border border-slate-200/80">
            <Layers className="h-10 w-10 text-slate-300 mx-auto mb-4 stroke-[1.5]" />
            <p className="text-slate-400 font-medium text-sm">No analysis matching your search criteria found.</p>
            {(searchTerm || filterCategory) && (
              <button
                onClick={handleResetFilters}
                className="text-xs font-bold text-brand-600 hover:text-brand-500 mt-2 cursor-pointer"
              >
                Clear all filters and search again
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {history.map((item) => (
                <motion.div
                  key={item.id}
                  onClick={() => navigate(`/analysis/${item.id}`)}
                  whileHover={{ y: -2 }}
                  className="rounded-xl bg-white p-5 border border-slate-200/80 hover:border-slate-300 hover:shadow-md hover:shadow-slate-100 transition-all cursor-pointer flex flex-col justify-between h-48 relative group"
                >
                  {/* Top */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between gap-4">
                      <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider bg-slate-50 border border-slate-100 rounded px-1.5 py-0.5">
                        {item.input_type} Check
                      </span>
                      
                      {/* Delete Action button */}
                      <button
                        onClick={(e) => handleDelete(e, item.id)}
                        className="h-7 w-7 rounded hover:bg-red-500/10 text-slate-400 hover:text-red-500 flex items-center justify-center transition-colors cursor-pointer md:opacity-0 group-hover:opacity-100"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>

                    <h4 className="text-sm font-bold text-slate-800 line-clamp-2 pr-6 group-hover:text-brand-600 transition-colors">
                      {item.original_content || "Text Input Block"}
                    </h4>
                  </div>

                  {/* Bottom */}
                  <div className="border-t border-slate-50 pt-3 flex items-center justify-between text-xs">
                    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[10px] font-bold ${getRiskBadgeStyles(item.risk_category)}`}>
                      {item.risk_category}
                    </span>
                    
                    <div className="flex items-center gap-1.5 text-slate-400 font-semibold text-[10px]">
                      <Calendar className="h-3.5 w-3.5" />
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
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between border-t border-slate-100 pt-6">
                <p className="text-xs text-slate-400 font-medium">
                  Showing <span className="font-semibold text-slate-600">{(page - 1) * perPage + 1}</span> to{' '}
                  <span className="font-semibold text-slate-600">
                    {Math.min(page * perPage, totalItems)}
                  </span>{' '}
                  of <span className="font-semibold text-slate-600">{totalItems}</span> scans
                </p>

                <div className="flex items-center gap-1.5">
                  <button
                    disabled={page === 1}
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    className="h-8 w-8 rounded-lg border border-slate-200 bg-white hover:border-slate-350 hover:bg-slate-50 text-slate-600 flex items-center justify-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                  >
                    <ChevronLeft className="h-4.5 w-4.5" />
                  </button>
                  
                  <span className="text-xs font-bold text-slate-700 px-3">
                    Page {page} of {totalPages}
                  </span>

                  <button
                    disabled={page === totalPages}
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    className="h-8 w-8 rounded-lg border border-slate-200 bg-white hover:border-slate-350 hover:bg-slate-50 text-slate-600 flex items-center justify-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
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
