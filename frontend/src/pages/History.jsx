import React from 'react';
import AnalysisHistoryTable from '../components/history/AnalysisHistoryTable';

export default function History() {
  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Workspace Header Banner */}
      <div className="surface-card p-6 border-[#E5E3DC] bg-white">
        <h1 className="text-xl font-bold text-[#11151C] tracking-tight">
          Procurement Analysis History Repository
        </h1>
        <p className="text-xs text-[#5F6368] mt-1 max-w-2xl">
          Centralized log of all audited tender specifications, mapped Indian Standards (BIS), completeness scores, and exported compliance certificates.
        </p>
      </div>

      <AnalysisHistoryTable />

    </div>
  );
}
