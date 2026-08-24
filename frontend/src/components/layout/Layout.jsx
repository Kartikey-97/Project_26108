import React from 'react';
import { Outlet } from 'react-router-dom';
import TopNavigation from './TopNavigation';

export default function Layout() {
  return (
    <div
      className="min-h-screen flex flex-col font-sans transition-colors duration-150"
      style={{
        backgroundColor: 'var(--bg-primary)',
        color: 'var(--text-main)'
      }}
    >
      
      {/* 2-Tier Spacious Top Navigation (Replaces Left Sidebar) */}
      <TopNavigation />

      {/* Main Full-Width Content Container with Generous Whitespace */}
      <main className="flex-1 w-full max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-10 py-8">
        <Outlet />
      </main>

      {/* Minimal Enterprise / Government Footer */}
      <footer
        className="border-t py-5 px-6 lg:px-10 text-xs transition-colors duration-150"
        style={{
          backgroundColor: 'var(--header-bg)',
          borderColor: 'var(--border-subtle)',
          color: 'var(--text-secondary)'
        }}
      >
        <div className="max-w-[1440px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-bold" style={{ color: 'var(--text-main)' }}>StandIQ / ProcureIntel</span>
            <span>· Bureau of Indian Standards (BIS) &amp; DPIIT QCO Recommendation Engine</span>
          </div>
          <div
            className="flex items-center gap-4 text-[11px] font-mono"
            style={{ color: 'var(--text-muted)' }}
          >
            <span>BIS Act 2016</span>
            <span>·</span>
            <span>SIH 2026 Smart Procurement</span>
          </div>
        </div>
      </footer>

    </div>
  );
}
