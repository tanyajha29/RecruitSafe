import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import Layout from '../components/common/Layout';
import { useAuth } from '../context/AuthContext';
import { Card, PrimaryButton, ScoreRing, Badge } from '../components/common/Primitives';
import { 
  FileText, 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  ArrowRight,
  TrendingUp,
  Globe
} from 'lucide-react';

const DashboardPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

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

  const calculateSafetyScore = () => {
    if (!stats || stats.total_analyses === 0) return 85;
    const safeW = (stats.safe_count || 0) * 98;
    const reviewW = (stats.needs_verification_count || 0) * 75;
    const suspW = (stats.suspicious_count || 0) * 35;
    const highW = (stats.high_risk_count || 0) * 10;
    const sum = safeW + reviewW + suspW + highW;
    return Math.round(sum / stats.total_analyses);
  };

  const getEntityTitle = (item) => {
    if (!item.original_content) return 'Verification Outreach';
    return item.original_content.split('\n')?.[0]?.replace('Company: ', '') || 'Company Outreach';
  };

  const getSubtext = (item) => {
    const timeStr = new Date(item.created_at).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric'
    });
    if (item.risk_category === 'Safe') {
      return `Verified Outreach • ${timeStr}`;
    } else if (item.risk_category === 'Needs Verification' || item.risk_category === 'Needs Review') {
      return `Needs Audit • ${timeStr}`;
    }
    return `Suspected Phishing • ${timeStr}`;
  };

  const getClassificationBadge = (category) => {
    switch (category) {
      case 'Safe':
        return <Badge variant="success">Verified</Badge>;
      case 'Needs Verification':
      case 'Needs Review':
        return <Badge variant="warning">Needs review</Badge>;
      default:
        return <Badge variant="danger">Suspicious</Badge>;
    }
  };

  const safetyScore = calculateSafetyScore();

  if (loading) {
    return (
      <Layout>
        <div className="space-y-8 max-w-[1280px] mx-auto py-12 animate-pulse select-none">
          <div className="h-16 bg-card rounded-xl w-1/3 border border-border"></div>
          <div className="grid grid-cols-12 gap-6">
            <div className="col-span-12 md:col-span-7 h-64 bg-card rounded-xl border border-border"></div>
            <div className="col-span-12 md:col-span-5 h-64 bg-card rounded-xl border border-border"></div>
            <div className="col-span-12 h-80 bg-card rounded-xl border border-border"></div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-8 select-none max-w-[1280px] mx-auto">
        
        {/* Welcome Section */}
        <section className="text-left animate-in fade-in duration-500">
          <h1 className="font-sans text-2xl font-bold text-text-primary tracking-tight">
            Welcome back, {user?.full_name?.split(' ')?.[0] || 'Alex'}.
          </h1>
          <p className="text-text-secondary text-sm">
            Your security ecosystem is stable. {stats?.high_risk_count > 0 ? `${stats.high_risk_count} threat signals require inspection.` : 'No urgent threats detected.'}
          </p>
        </section>

        {/* Bento Grid Content */}
        <div className="grid grid-cols-12 gap-6">
          
          {/* Quick Action Card */}
          <Card className="col-span-12 md:col-span-7 flex flex-col justify-between text-left">
            <div className="space-y-3">
              <span className="font-mono text-[10px] font-bold text-text-secondary uppercase tracking-widest block">
                Immediate Actions
              </span>
              <h2 className="font-sans text-xl font-bold text-text-primary tracking-tight">
                Threat Intelligence & Recruiter Analysis
              </h2>
              <p className="text-text-secondary text-sm leading-relaxed max-w-md">
                Verify unsolicited outreach from potential recruiters using our neural fraud detection engine.
              </p>
            </div>
            
            <div className="pt-8">
              <PrimaryButton 
                onClick={() => navigate('/analysis/new')}
                className="w-full md:w-auto"
              >
                <span>Start New Analysis</span>
                <ArrowRight className="h-4 w-4" />
              </PrimaryButton>
            </div>
          </Card>

          {/* Safety Score Card */}
          <Card className="col-span-12 md:col-span-5 flex flex-col items-center justify-center text-center">
            <span className="font-mono text-[10px] font-bold text-text-secondary uppercase tracking-widest mb-6 block">
              Personal Safety Score
            </span>
            <ScoreRing 
              score={safetyScore} 
              label={safetyScore >= 80 ? 'SAFE' : safetyScore >= 50 ? 'CAUTION' : 'AT RISK'} 
            />
            <div className="mt-6 inline-flex items-center gap-2 px-3 py-1 bg-brand-light rounded-full border border-brand/20">
              <ShieldCheck className="h-4 w-4 text-brand" />
              <span className="font-mono text-[11px] font-bold text-brand uppercase tracking-wider">
                Optimal Protection Active
              </span>
            </div>
          </Card>

          {/* Stats quick overview cards */}
          <Card className="col-span-6 md:col-span-3 text-left flex items-center gap-4">
            <div className="h-10 w-10 rounded-lg bg-bg border border-border flex items-center justify-center text-text-secondary">
              <FileText className="h-5 w-5" />
            </div>
            <div>
              <p className="text-2xl font-bold text-text-primary">{stats?.total_analyses}</p>
              <p className="text-[10px] text-text-secondary font-mono font-bold uppercase tracking-wider mt-0.5">Total Checks</p>
            </div>
          </Card>

          <Card className="col-span-6 md:col-span-3 text-left flex items-center gap-4">
            <div className="h-10 w-10 rounded-lg bg-danger/5 border border-danger/20 flex items-center justify-center text-danger">
              <ShieldAlert className="h-5 w-5" />
            </div>
            <div>
              <p className="text-2xl font-bold text-danger">{stats?.high_risk_count}</p>
              <p className="text-[10px] text-text-secondary font-mono font-bold uppercase tracking-wider mt-0.5">High Risk</p>
            </div>
          </Card>

          <Card className="col-span-6 md:col-span-3 text-left flex items-center gap-4">
            <div className="h-10 w-10 rounded-lg bg-warning/5 border border-warning/20 flex items-center justify-center text-warning">
              <AlertTriangle className="h-5 w-5" />
            </div>
            <div>
              <p className="text-2xl font-bold text-warning">{stats?.suspicious_count}</p>
              <p className="text-[10px] text-text-secondary font-mono font-bold uppercase tracking-wider mt-0.5">Suspicious</p>
            </div>
          </Card>

          <Card className="col-span-6 md:col-span-3 text-left flex items-center gap-4">
            <div className="h-10 w-10 rounded-lg bg-success/5 border border-success/20 flex items-center justify-center text-success">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <p className="text-2xl font-bold text-success">{stats?.safe_count}</p>
              <p className="text-[10px] text-text-secondary font-mono font-bold uppercase tracking-wider mt-0.5">Safe Outreach</p>
            </div>
          </Card>

          {/* Recent Verifications Table */}
          <Card className="col-span-12 p-0 overflow-hidden text-left">
            <div className="px-8 py-6 border-b border-border flex justify-between items-center bg-card">
              <h3 className="font-mono text-[11px] font-bold text-text-secondary uppercase tracking-widest">
                Recent Verifications
              </h3>
              <button 
                onClick={() => navigate('/history')}
                className="text-brand font-mono text-[11px] font-bold hover:underline cursor-pointer"
              >
                VIEW ALL HISTORY
              </button>
            </div>
            
            <div className="overflow-x-auto">
              {stats?.recent_analyses?.length === 0 ? (
                <div className="py-16 text-center border-t border-border bg-card">
                  <p className="text-text-secondary text-sm font-semibold">No recent scans found.</p>
                  <button 
                    onClick={() => navigate('/analysis/new')}
                    className="text-brand text-xs font-bold font-mono mt-2 underline cursor-pointer"
                  >
                    Perform your first recruiter scan
                  </button>
                </div>
              ) : (
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-bg border-b border-border select-none">
                      <th className="px-8 py-4 font-mono text-[10px] font-bold text-text-secondary uppercase tracking-wider">Entity</th>
                      <th className="px-8 py-4 font-mono text-[10px] font-bold text-text-secondary uppercase tracking-wider">Classification</th>
                      <th className="px-8 py-4 font-mono text-[10px] font-bold text-text-secondary uppercase tracking-wider text-right">Confidence</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {stats?.recent_analyses?.slice(0, 3).map((item) => (
                      <tr 
                        key={item.id}
                        onClick={() => navigate(`/analysis/${item.id}`)}
                        className="hover:bg-bg/50 transition-colors group cursor-pointer"
                      >
                        <td className="px-8 py-5">
                          <div className="flex items-center gap-4">
                            <div className="w-9 h-9 flex items-center justify-center bg-bg border border-border rounded-lg shrink-0 text-text-secondary">
                              <span className="material-symbols-outlined text-[20px]">
                                {item.input_type === 'email' ? 'alternate_email' : item.input_type === 'url' ? 'globe' : 'work'}
                              </span>
                            </div>
                            <div>
                              <p className="font-sans text-sm font-semibold text-text-primary truncate max-w-xs group-hover:text-brand transition-colors">{getEntityTitle(item)}</p>
                              <p className="font-mono text-[10px] text-text-secondary mt-0.5">{getSubtext(item)}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-8 py-5">
                          {getClassificationBadge(item.risk_category)}
                        </td>
                        <td className="px-8 py-5 text-right font-mono text-xs text-text-secondary">
                          {item.trust_score !== null ? `${item.trust_score}%` : '--%'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </Card>

          {/* Network Insights */}
          <Card className="col-span-12 md:col-span-6 text-left space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="font-mono text-[11px] font-bold text-text-secondary uppercase tracking-widest">
                Global Network Health
              </h3>
              <Globe className="h-4.5 w-4.5 text-brand" />
            </div>
            
            <div className="space-y-6">
              <div className="space-y-2">
                <div className="flex justify-between font-mono text-[10px] font-bold uppercase">
                  <span>Phishing Activity</span>
                  <span className="text-brand">Low</span>
                </div>
                <div className="h-1 bg-bg border border-border overflow-hidden rounded-full">
                  <div className="h-full bg-brand w-[20%]"></div>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between font-mono text-[10px] font-bold uppercase">
                  <span>Identity Spoofing</span>
                  <span className="text-brand">Moderate</span>
                </div>
                <div className="h-1 bg-bg border border-border overflow-hidden rounded-full">
                  <div className="h-full bg-brand w-[45%]"></div>
                </div>
              </div>
            </div>
          </Card>

          {/* Security Tip */}
          <Card className="col-span-12 md:col-span-6 bg-brand-light/30 border-brand/20 text-left flex gap-5">
            <div className="flex-shrink-0 w-11 h-11 bg-brand text-white flex items-center justify-center rounded-lg">
              <span className="material-symbols-outlined text-[20px]">lightbulb</span>
            </div>
            <div>
              <h4 className="font-sans text-[15px] font-bold text-text-primary mb-1">Pro-Tip: Domain Check</h4>
              <p className="text-text-secondary text-xs leading-relaxed">
                Recruiters from major firms will never contact you from personal Gmail or Outlook accounts. Always check the MX records of the sender's domain.
              </p>
            </div>
          </Card>

        </div>

      </div>
    </Layout>
  );
};

export default DashboardPage;
