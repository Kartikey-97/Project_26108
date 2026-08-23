import React from 'react';
import WelcomeBanner from '../components/dashboard/WelcomeBanner';
import StatCards from '../components/dashboard/StatCards';
import RecentAnalyses from '../components/dashboard/RecentAnalyses';
import QuickActions from '../components/dashboard/QuickActions';
import { MOCK_STATS, MOCK_RECENT_ANALYSES, MOCK_QUICK_ACTIONS } from '../data/mockData';

export default function Dashboard() {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Welcome Hero Banner */}
      <WelcomeBanner />

      {/* Statistics Cards */}
      <StatCards stats={MOCK_STATS} />

      {/* Quick Actions Shortcuts */}
      <QuickActions actions={MOCK_QUICK_ACTIONS} />

      {/* Recent Analyses Table */}
      <RecentAnalyses analyses={MOCK_RECENT_ANALYSES} />
    </div>
  );
}
