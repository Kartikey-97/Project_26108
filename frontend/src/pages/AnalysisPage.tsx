import { useEffect, useState } from 'react';
import { ArrowLeft, Loader2, AlertTriangle } from 'lucide-react';
import { TopNav } from '@/components/TopNav';
import { useRouter, type AnalysisTab } from '@/router';
import { getAnalysis } from '@/services/api';
import { adaptAnalysis, type AdaptedAnalysis } from '@/services/adapter';
import { AnalysisOverviewTab } from './analysis/AnalysisOverviewTab';
import { AnalysisStandardsTab } from './analysis/AnalysisStandardsTab';
import { AnalysisRelationshipsTab } from './analysis/AnalysisRelationshipsTab';
import { AnalysisGapsTab } from './analysis/AnalysisGapsTab';
import { AnalysisCertificationTab } from './analysis/AnalysisCertificationTab';
import { AnalysisEvidenceTab } from './analysis/AnalysisEvidenceTab';

interface Props { analysisId: string; tab: AnalysisTab; }

const TABS: AnalysisTab[] = ['overview', 'standards', 'relationships', 'gaps', 'certification', 'evidence'];

export function AnalysisPage({ analysisId, tab }: Props) {
  const { navigate } = useRouter();
  const activeTab = tab || 'overview';

  const [data, setData] = useState<AdaptedAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    getAnalysis(analysisId)
      .then((raw: unknown) => {
        if (cancelled) return;
        setData(adaptAnalysis(raw));
      })
      .catch((err: Error) => {
        if (cancelled) return;
        setError(err.message || 'Failed to load analysis.');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [analysisId]);

  const renderTab = () => {
    if (!data) return null;
    switch (activeTab) {
      case 'overview':
        return <AnalysisOverviewTab analysis={data.analysis} standards={data.standards} matchedRequirements={data.matchedRequirements} primaryStandard={data.primaryStandard} />;
      case 'standards':
        return <AnalysisStandardsTab standards={data.standards} />;
      case 'relationships':
        return <AnalysisRelationshipsTab relationships={data.relationships} />;
      case 'gaps':
        return <AnalysisGapsTab specRequirements={data.specRequirements} />;
      case 'certification':
        return <AnalysisCertificationTab regulatory={data.regulatory} />;
      case 'evidence':
        return <AnalysisEvidenceTab evidence={data.evidence} />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-ivory-50 text-ink-900 dark:bg-[#090D16] dark:text-slate-100">
      <TopNav variant="app" />
      <div className="container-app py-6">
        <button onClick={() => navigate({ name: 'workspace' })} className="mb-4 flex items-center gap-1.5 text-sm text-ink-500 hover:text-ink-900 dark:text-slate-400 dark:hover:text-white">
          <ArrowLeft size={15} /> Workspace
        </button>

        {loading && (
          <div className="flex flex-col items-center justify-center gap-3 py-24 text-ink-500 dark:text-slate-400">
            <Loader2 size={26} className="animate-spin text-teal-600" />
            <p className="text-sm">Loading analysis…</p>
          </div>
        )}

        {!loading && error && (
          <div className="mx-auto max-w-lg rounded-lg border border-error-200 bg-error-50 p-6 text-center">
            <AlertTriangle size={26} className="mx-auto mb-2 text-error-600" />
            <h2 className="text-sm font-semibold text-error-800">Could not load this analysis</h2>
            <p className="mt-1 text-xs text-error-700">{error}</p>
            <button onClick={() => navigate({ name: 'new-analysis' })} className="btn-secondary mt-4 text-xs">
              Start a new analysis
            </button>
          </div>
        )}

        {!loading && !error && data && (
          <>
            <div className="mb-1 flex flex-wrap items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-ink-900 dark:text-white">{data.analysis.title}</h1>
            </div>
            <p className="mb-6 text-xs text-ink-500 dark:text-slate-400">
              {data.analysis.standardsIdentified} standards · {data.analysis.gapsFound} issues · {data.analysis.certificationsRequired} certifications
              {data.analysisMode ? ` · ${data.analysisMode === 'remote' ? 'AI analysis' : 'deterministic analysis'}` : ''}
            </p>

            {data.degradedReason && (
              <div className="mb-6 rounded-lg border border-warning-200 bg-warning-50 px-4 py-2 text-xs text-warning-800">
                {data.degradedReason}
              </div>
            )}

            <div className="mb-6 flex gap-2 overflow-x-auto border-b border-ink-200 dark:border-slate-800">
              {TABS.map((t) => (
                <button
                  key={t}
                  onClick={() => navigate({ name: 'analysis', analysisId: data.analysis.id, tab: t })}
                  className={`whitespace-nowrap px-4 py-2 text-sm capitalize transition-colors ${activeTab === t ? 'border-b-2 border-ink-900 font-bold text-ink-900 dark:border-teal-400 dark:text-white' : 'text-ink-500 hover:text-ink-800 dark:text-slate-400'}`}
                >
                  {t}
                </button>
              ))}
            </div>

            {renderTab()}
          </>
        )}
      </div>
    </div>
  );
}
