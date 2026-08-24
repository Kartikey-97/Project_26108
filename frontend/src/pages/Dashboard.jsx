import React, { useEffect, useState } from 'react';
import WelcomeBanner from '../components/dashboard/WelcomeBanner';
import StatCards from '../components/dashboard/StatCards';
import RecentAnalyses from '../components/dashboard/RecentAnalyses';
import QuickActions from '../components/dashboard/QuickActions';
import { listAnalyses } from '../services/api';

// Import the excellent realistic mock data for SIH Demo Mode
import { MOCK_RECENT_ANALYSES, MOCK_STATS } from '../data/mockData';

export default function Dashboard() {
  const [analyses, setAnalyses] = useState([]);
  const [error, setError] = useState('');
  const [demoMode, setDemoMode] = useState(false);

  useEffect(() => {
    if (!demoMode) {
      listAnalyses().then(setAnalyses).catch((err) => setError(err.message));
    }
  }, [demoMode]);

  // If in Demo Mode, inject the MOCK data directly!
  const liveAnalyses = demoMode 
    ? MOCK_RECENT_ANALYSES 
    : analyses.slice(0, 5).map((item) => ({
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

  const completed = analyses.filter((item) => ['completed', 'partially_completed'].includes(item.status));
  
  const stats = demoMode 
    ? MOCK_STATS 
    : [
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
      <WelcomeBanner />

      {error && <p className="text-xs text-red-600">{error}</p>}
      
      {/* Demo Mode Activator */}
      {analyses.length === 0 && !demoMode && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">No Recent Analyses Found</h3>
          <p className="text-sm text-blue-700 mb-4">You haven't run any real analyses yet. Want to populate the dashboard for your presentation?</p>
          <button 
            onClick={() => setDemoMode(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded shadow transition-colors"
          >
            Load SIH Demo Data
          </button>
        </div>
      )}

      <StatCards stats={stats} />
      <QuickActions actions={actions} />
      <RecentAnalyses analyses={liveAnalyses} />
    </div>
  );
}
