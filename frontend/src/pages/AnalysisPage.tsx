import { useState } from 'react';
import { ArrowLeft, CheckCircle2, Clock, FileText, GitBranch, ListChecks, ScrollText, ShieldCheck, Sparkles } from 'lucide-react';
import { TopNav } from '@/components/TopNav';
import { useRouter, type AnalysisTab } from '@/router';
import { getAnalysisById } from '@/data/mockData';
import { AnalysisOverviewTab } from './analysis/AnalysisOverviewTab';
import { AnalysisStandardsTab } from './analysis/AnalysisStandardsTab';
import { AnalysisRelationshipsTab } from './analysis/AnalysisRelationshipsTab';
import { AnalysisGapsTab } from './analysis/AnalysisGapsTab';
import { AnalysisCertificationTab } from './analysis/AnalysisCertificationTab';
import { AnalysisEvidenceTab } from './analysis/AnalysisEvidenceTab';

interface Props { analysisId: string; tab: AnalysisTab; }

export function AnalysisPage({ analysisId, tab }: Props) {
  const { navigate } = useRouter();
  const analysis = getAnalysisById(analysisId);
  const activeTab = tab || 'overview';

  if (!analysis) return <div>Analysis not found</div>;

  const renderTab = () => {
    switch (activeTab) {
      case 'overview': return <AnalysisOverviewTab analysis={analysis} />;
      case 'standards': return <AnalysisStandardsTab analysis={analysis} />;
      case 'relationships': return <AnalysisRelationshipsTab analysisId={analysis.id} />;
      case 'gaps': return <AnalysisGapsTab analysisId={analysis.id} />;
      case 'certification': return <AnalysisCertificationTab analysis={analysis} />;
      case 'evidence': return <AnalysisEvidenceTab analysis={analysis} />;
    }
  };

  return (
    <div className="min-h-screen bg-ivory-50 text-ink-900 dark:bg-[#090D16] dark:text-slate-100">
      <TopNav variant="app" />
      <div className="container-app py-6">
        <button onClick={() => navigate({ name: 'workspace' })} className="mb-4 flex items-center gap-1.5 text-sm text-ink-500">
          <ArrowLeft size={15} /> Workspace
        </button>
        <h1 className="text-xl font-bold mb-6">{analysis.title}</h1>
        
        <div className="mb-6 flex gap-2 overflow-x-auto border-b border-ink-200">
          {(['overview', 'standards', 'relationships', 'gaps', 'certification', 'evidence'] as AnalysisTab[]).map(t => (
            <button key={t} onClick={() => navigate({ name: 'analysis', analysisId: analysis.id, tab: t })} className={`px-4 py-2 text-sm ${activeTab === t ? 'border-b-2 border-ink-900 font-bold' : ''}`}>
              {t.toUpperCase()}
            </button>
          ))}
        </div>
        
        {renderTab()}
      </div>
    </div>
  );
}
