import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import Analyze from './pages/Analyze';
import Recommendations from './pages/Recommendations';
import History from './pages/History';
import StandardsExplorer from './pages/StandardsExplorer';
import Compare from './pages/Compare';
import StandardDetails from './pages/StandardDetails';
import Settings from './pages/Settings';

export default function App() {
  return (
    <Routes>
      {/* StandIQ Landing Page */}
      <Route path="/" element={<LandingPage />} />

      {/* Main Procurement Intelligence Application Workspace */}
      <Route element={<Layout />}>
        <Route path="app" element={<Dashboard />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="analyze" element={<Analyze />} />
        <Route path="recommendations" element={<Recommendations />} />
        <Route path="history" element={<History />} />
        <Route path="standards" element={<StandardsExplorer />} />
        <Route path="standards/:id" element={<StandardDetails />} />
        <Route path="compare" element={<Compare />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      {/* Fallback to Landing Page */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
