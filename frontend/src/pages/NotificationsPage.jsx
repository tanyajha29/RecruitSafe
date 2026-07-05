import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../services/api';
import Layout from '../components/common/Layout';
import { 
  Bell, 
  CheckCheck, 
  Trash2, 
  AlertCircle, 
  CheckCircle2, 
  Info, 
  FileCheck,
  Calendar,
  Layers
} from 'lucide-react';

const NotificationsPage = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();

  const fetchNotifications = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get('/api/notifications');
      setNotifications(response.data);
    } catch (err) {
      console.error(err);
      setError('Could not retrieve notifications. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const handleMarkAllRead = async () => {
    try {
      await api.post('/api/notifications/read-all');
      // Update local state to show all as read
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch (err) {
      console.error(err);
      alert('Failed to mark all notifications as read.');
    }
  };

  const handleNotificationClick = async (item) => {
    // 1. Mark as read on backend if unread
    if (!item.is_read) {
      try {
        await api.put(`/api/notifications/${item.id}/read`);
        // Update local state
        setNotifications((prev) => 
          prev.map((n) => (n.id === item.id ? { ...n, is_read: true } : n))
        );
      } catch (err) {
        console.error('Failed to mark single notification as read:', err);
      }
    }

    // 2. Redirect to analysis details if associated
    if (item.analysis_id) {
      navigate(`/analysis/${item.analysis_id}`);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'analysis_complete':
        return <CheckCircle2 className="h-5 w-5 text-emerald-500" />;
      case 'upload_error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'pdf_ready':
        return <FileCheck className="h-5 w-5 text-brand-500" />;
      default:
        return <Info className="h-5 w-5 text-slate-500" />;
    }
  };

  const formatNotificationTime = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    
    return date.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  return (
    <Layout>
      <div className="max-w-3xl mx-auto space-y-6">
        
        {/* Header summary info & Read all trigger */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-200">
          <div>
            <h2 className="text-xl font-bold text-slate-800">Notifications</h2>
            <p className="text-xs text-slate-400 font-semibold mt-1">
              You have <span className="text-brand-600 font-bold">{unreadCount}</span> unread alert notifications
            </p>
          </div>

          {unreadCount > 0 && (
            <button
              onClick={handleMarkAllRead}
              className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white hover:border-slate-350 hover:bg-slate-50 text-slate-700 font-bold text-xs px-3.5 py-2.5 transition-colors cursor-pointer"
            >
              <CheckCheck className="h-4 w-4 text-slate-500" />
              <span>Mark all as read</span>
            </button>
          )}
        </div>

        {/* List of alerts */}
        {loading ? (
          <div className="flex h-64 w-full items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent"></div>
          </div>
        ) : error ? (
          <div className="py-12 text-center text-red-500 font-medium">{error}</div>
        ) : notifications.length === 0 ? (
          <div className="rounded-2xl bg-white p-12 text-center border border-slate-200/80">
            <Bell className="h-10 w-10 text-slate-300 mx-auto mb-4 stroke-[1.5]" />
            <p className="text-slate-400 font-medium text-sm">No notifications found.</p>
          </div>
        ) : (
          <div className="space-y-3">
            <AnimatePresence>
              {notifications.map((item) => (
                <motion.div
                  key={item.id}
                  layout
                  onClick={() => handleNotificationClick(item)}
                  className={`rounded-xl border p-4 transition-all duration-200 flex items-start gap-4 cursor-pointer relative overflow-hidden ${
                    item.is_read 
                      ? 'bg-white border-slate-200/60 hover:bg-slate-50/20' 
                      : 'bg-brand-500/[0.02] border-brand-500/20 hover:bg-brand-500/[0.04]'
                  }`}
                >
                  {/* Unread indicator bar */}
                  {!item.is_read && (
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-brand-500"></div>
                  )}

                  {/* Icon */}
                  <div className="h-9 w-9 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-center shrink-0">
                    {getNotificationIcon(item.type)}
                  </div>

                  {/* Content details */}
                  <div className="flex-1 min-w-0 space-y-1">
                    <div className="flex items-center justify-between gap-4">
                      <h4 className={`text-sm leading-tight truncate ${item.is_read ? 'text-slate-700 font-bold' : 'text-slate-800 font-extrabold'}`}>
                        {item.title}
                      </h4>
                      <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider shrink-0">
                        {formatNotificationTime(item.created_at)}
                      </span>
                    </div>
                    <p className={`text-xs leading-relaxed ${item.is_read ? 'text-slate-500 font-semibold' : 'text-slate-655 font-bold'}`}>
                      {item.message}
                    </p>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}

      </div>
    </Layout>
  );
};

export default NotificationsPage;
