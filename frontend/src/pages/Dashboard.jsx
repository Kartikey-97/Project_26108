import React, { useEffect, useState } from 'react';
import WelcomeBanner from '../components/dashboard/WelcomeBanner';
import StatCards from '../components/dashboard/StatCards';
import RecentAnalyses from '../components/dashboard/RecentAnalyses';
import QuickActions from '../components/dashboard/QuickActions';
import { listAnalyses } from '../services/api';

export default function Dashboard() {
  const [analyses, setAnalyses] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    listAnalyses().then(setAnalyses).catch((err) => setError(err.message));
  }, []);

  const completed = analyses.filter((item) => ['completed', 'partially_completed'].includes(item.status));
  const liveAnalyses = analyses.slice(0, 5).map((item) => ({
    id: item.analysis_id,
    title: item.tender_title || 'Procurement specification analysis',
    category: item.metadata?.category || 'BIS analysis',
    department: item.metadata?.department || 'Procurement review',
    date: new Date(item.created_at).toLocaleDateString(),
    standardsCount: 0,
    standards: [],
    completenessScore: Math.max(0, 100 - item.issues_found * 10),
    status: item.status === 'completed' ? 'COMPLETED' : item.issues_found ? 'WARNING_FLAGGED' : 'IN_REVIEW',
    qcoMandatory: false,
  }));
  const stats = [
    { id: 'analyses', title: 'Total Analyses Run', value: String(analyses.length), change: `${completed.length} completed`, trend: 'up', description: 'Persisted procurement analyses' },
    { id: 'requirements', title: 'Requirements Extracted', value: String(analyses.reduce((sum, item) => sum + item.total_requirements, 0)), change: 'Across saved analyses', trend: 'neutral', description: 'Technical requirements reviewed' },
    { id: 'issues', title: 'Issues Flagged', value: String(analyses.reduce((sum, item) => sum + item.issues_found, 0)), change: 'Requires officer review', trend: 'alert', description: 'Compliance and restriction findings' },
    { id: 'mode', title: 'Analysis Mode', value: completed.some((item) => item.analysis_mode === 'remote') ? 'AI' : 'BIS', change: 'Fallback-ready', trend: 'neutral', description: 'Remote AI or deterministic checks' },
  ];
  const actions = [
    { id: 'act-1', title: 'New Procurement Analysis', description: 'Paste text or upload a tender document for BIS review.', actionText: 'Start Analysis', link: '/analyze', badge: 'Analysis' },
    { id: 'act-2', title: 'Indian Standards Explorer', description: 'Search the live 1,015-record BIS catalog.', actionText: 'Explore Catalog', link: '/standards', badge: 'BIS' },
    { id: 'act-3', title: 'Compare Standards', description: 'Compare selected live BIS records side by side.', actionText: 'Compare', link: '/compare', badge: 'Compare' },
  ];
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Welcome Hero Banner */}
      <WelcomeBanner />

      {/* Statistics Cards */}
      {error && <p className="text-xs text-red-600">{error}</p>}
      <StatCards stats={stats} />

      {/* Quick Actions Shortcuts */}
      <QuickActions actions={actions} />

      {/* Recent Analyses Table */}
      <RecentAnalyses analyses={liveAnalyses} />
    </div>
  );
}
