import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../services/api';
import Layout from '../components/common/Layout';
import { Card, PrimaryButton, SecondaryButton, Badge } from '../components/common/Primitives';
import { 
  Search, 
  Trash2, 
  Calendar,
  Layers,
  ChevronLeft,
  ChevronRight,
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

  const getRiskBadgeVariant = (category) => {
    switch (category) {
      case 'Safe':
        return 'success';
      case 'Needs Verification':
      case 'Needs Review':
        return 'warning';
      default:
        return 'danger';
    }
  };

  return (
    <Layout>
      <div className="space-y-6 max-w-5xl mx-auto select-none">
        
        {/* Search & Filter Bar */}
        <Card className="p-6">
          <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row items-center gap-4">
            
            {/* Search Input */}
            <div className="relative flex-1 w-full text-left">
              <input
                type="text"
                placeholder="Search scans (keywords, company, titles)..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full rounded-lg border border-border py-3 pl-10 pr-4 text-sm text-text-primary bg-bg outline-none transition-all placeholder:text-text-secondary/40 focus:ring-1 focus:ring-brand focus:border-brand"
              />
              <Search className="absolute left-3.5 top-3.5 h-4.5 w-4.5 text-text-secondary/45" />
            </div>

            {/* Risk Category Filter */}
            <div className="relative w-full md:w-56 text-left">
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="w-full rounded-lg border border-border py-3 pl-9 pr-8 text-sm text-text-primary bg-bg outline-none transition-all appearance-none cursor-pointer font-bold focus:ring-1 focus:ring-brand"
              >
                <option value="">All Risk Categories</option>
                <option value="Safe">Safe</option>
                <option value="Needs Verification">Needs Verification</option>
                <option value="Suspicious">Suspicious</option>
                <option value="High Risk">High Risk</option>
              </select>
              <Filter className="absolute left-3.5 top-3.5 h-4 w-4 text-text-secondary/45 pointer-events-none" />
              <div className="absolute right-3.5 top-4.5 h-0 w-0 border-4 border-transparent border-t-text-secondary pointer-events-none" />
            </div>

            {/* Action buttons */}
            <div className="flex items-center gap-2.5 w-full md:w-auto">
              <PrimaryButton type="submit" className="flex-1 md:flex-none">
                Apply
              </PrimaryButton>
              <SecondaryButton type="button" onClick={handleResetFilters} className="flex-1 md:flex-none">
                Reset
              </SecondaryButton>
            </div>

          </form>
        </Card>

        {/* History Results list */}
        {loading ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-48 rounded-xl bg-card border border-border animate-pulse"></div>
              ))}
            </div>
          </div>
        ) : error ? (
          <div className="py-12 text-center text-danger font-semibold">{error}</div>
        ) : history.length === 0 ? (
          <Card className="p-12 text-center">
            <Layers className="h-10 w-10 text-text-secondary/40 mx-auto mb-4 stroke-[1.5]" />
            <p className="text-text-secondary font-bold text-sm">No analysis matching your search criteria found.</p>
            {(searchTerm || filterCategory) && (
              <button
                onClick={handleResetFilters}
                className="text-xs font-mono font-bold text-brand hover:underline mt-2 cursor-pointer"
              >
                Clear all filters and search again
              </button>
            )}
          </Card>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {history.map((item) => (
                <Card
                  key={item.id}
                  onClick={() => navigate(`/analysis/${item.id}`)}
                  className="hover:border-brand hover:shadow-md transition-all cursor-pointer flex flex-col justify-between h-48 text-left relative group"
                >
                  {/* Top */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between gap-4">
                      <span className="text-[9px] text-text-secondary font-mono font-bold uppercase tracking-wider bg-bg border border-border rounded px-2 py-0.5">
                        {item.input_type} Check
                      </span>
                      
                      {/* Delete Action button */}
                      <button
                        onClick={(e) => handleDelete(e, item.id)}
                        className="h-7 w-7 rounded-lg hover:bg-danger/10 text-text-secondary/45 hover:text-danger flex items-center justify-center transition-colors cursor-pointer md:opacity-0 group-hover:opacity-100"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>

                    <h4 className="text-sm font-extrabold text-text-primary line-clamp-2 pr-6 group-hover:text-brand transition-colors">
                      {item.original_content || "Text Input Block"}
                    </h4>
                  </div>

                  {/* Bottom */}
                  <div className="border-t border-border pt-3 flex items-center justify-between text-xs">
                    <Badge variant={getRiskBadgeVariant(item.risk_category)}>
                      {item.risk_category}
                    </Badge>
                    
                    <div className="flex items-center gap-1.5 text-text-secondary font-mono font-bold text-[9.5px]">
                      <Calendar className="h-3.5 w-3.5 text-text-secondary/45" />
                      <span>
                        {new Date(item.created_at).toLocaleDateString(undefined, {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric'
                        })}
                      </span>
                    </div>
                  </div>
                </Card>
              ))}
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between border-t border-border pt-6">
                <p className="text-xs text-text-secondary font-semibold">
                  Showing <span className="font-bold text-text-primary">{(page - 1) * perPage + 1}</span> to{' '}
                  <span className="font-bold text-text-primary">
                    {Math.min(page * perPage, totalItems)}
                  </span>{' '}
                  of <span className="font-bold text-text-primary">{totalItems}</span> scans
                </p>

                <div className="flex items-center gap-1.5">
                  <button
                    disabled={page === 1}
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    className="h-8 w-8 rounded-lg border border-border bg-card hover:bg-bg text-text-secondary flex items-center justify-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                  >
                    <ChevronLeft className="h-4.5 w-4.5" />
                  </button>
                  
                  <span className="text-xs font-bold text-text-primary px-3">
                    Page {page} of {totalPages}
                  </span>

                  <button
                    disabled={page === totalPages}
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    className="h-8 w-8 rounded-lg border border-border bg-card hover:bg-bg text-text-secondary flex items-center justify-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
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
