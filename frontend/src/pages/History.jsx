import React, { useEffect, useState } from 'react';
import AnalysisHistoryTable from '../components/history/AnalysisHistoryTable';
import { listAnalyses } from '../services/api';

export default function History() {
  const [analyses, setAnalyses] = useState([]);
  useEffect(() => {
    listAnalyses()
      .then((items) => {
        setAnalyses(items.map((item) => ({
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
          flaggedIssues: item.issues_found,
        })));
      })
      .catch(() => setAnalyses([]));
  }, []);
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

      <AnalysisHistoryTable analyses={analyses} />

    </div>
  );
}
