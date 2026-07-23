import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import Layout from '../components/common/Layout';
import { Card, SecondaryButton, Badge } from '../components/common/Primitives';
import { 
  Bell, 
  CheckCheck, 
  AlertCircle, 
  CheckCircle2, 
  Info, 
  FileCheck
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
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch (err) {
      console.error(err);
      alert('Failed to mark all notifications as read.');
    }
  };

  const handleNotificationClick = async (item) => {
    if (!item.is_read) {
      try {
        await api.put(`/api/notifications/${item.id}/read`);
        setNotifications((prev) => 
          prev.map((n) => (n.id === item.id ? { ...n, is_read: true } : n))
        );
      } catch (err) {
        console.error('Failed to mark single notification as read:', err);
      }
    }

    if (item.analysis_id) {
      navigate(`/analysis/${item.analysis_id}`);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'analysis_complete':
        return <CheckCircle2 className="h-5 w-5 text-success" />;
      case 'upload_error':
        return <AlertCircle className="h-5 w-5 text-danger" />;
      case 'pdf_ready':
        return <FileCheck className="h-5 w-5 text-brand" />;
      default:
        return <Info className="h-5 w-5 text-text-secondary" />;
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
      <div className="max-w-3xl mx-auto space-y-6 select-none">
        
        {/* Header summary info */}
        <div className="flex items-center justify-between pb-4 border-b border-border text-left">
          <div>
            <h2 className="text-xl font-bold text-text-primary tracking-tight">Notifications</h2>
            <p className="text-xs text-text-secondary font-semibold mt-1">
              You have <span className="text-brand font-bold">{unreadCount}</span> unread alert notifications
            </p>
          </div>

          {unreadCount > 0 && (
            <SecondaryButton
              onClick={handleMarkAllRead}
              className="text-xs px-3.5 py-2.5"
            >
              <CheckCheck className="h-4 w-4 text-text-secondary" />
              <span>Mark all as read</span>
            </SecondaryButton>
          )}
        </div>

        {/* List of alerts */}
        {loading ? (
          <div className="flex h-64 w-full items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand border-t-transparent"></div>
          </div>
        ) : error ? (
          <div className="py-12 text-center text-danger font-medium">{error}</div>
        ) : notifications.length === 0 ? (
          <Card className="p-12 text-center">
            <Bell className="h-10 w-10 text-text-secondary/40 mx-auto mb-4 stroke-[1.5]" />
            <p className="text-text-secondary font-bold text-sm">No notifications found.</p>
          </Card>
        ) : (
          <div className="space-y-3">
            {notifications.map((item) => (
              <div
                key={item.id}
                onClick={() => handleNotificationClick(item)}
                className={`rounded-xl border p-4 transition-all duration-200 flex items-start gap-4 cursor-pointer relative overflow-hidden text-left ${
                  item.is_read 
                    ? 'bg-card border-border hover:bg-bg/40' 
                    : 'bg-brand-light border-brand/35 hover:bg-brand-light/70'
                }`}
              >
                {/* Unread indicator bar */}
                {!item.is_read && (
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-brand"></div>
                )}

                {/* Icon */}
                <div className="h-9 w-9 rounded-lg bg-bg border border-border flex items-center justify-center shrink-0">
                  {getNotificationIcon(item.type)}
                </div>

                {/* Content details */}
                <div className="flex-1 min-w-0 space-y-1">
                  <div className="flex items-center justify-between gap-4">
                    <h4 className={`text-sm leading-tight truncate font-bold text-text-primary`}>
                      {item.title}
                    </h4>
                    <span className="text-[10px] text-text-secondary font-mono font-bold uppercase tracking-wider shrink-0">
                      {formatNotificationTime(item.created_at)}
                    </span>
                  </div>
                  <p className={`text-xs leading-relaxed text-text-secondary`}>
                    {item.message}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </Layout>
  );
};

export default NotificationsPage;
