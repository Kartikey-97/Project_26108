import { useEffect, useState, type ReactNode } from 'react';
import { AlertTriangle, ArrowRight, CheckCircle2, Clock, FileStack, Loader2, Plus } from 'lucide-react';
import { TopNav } from '@/components/TopNav';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { useRouter } from '@/router';
import { listAnalyses } from '@/services/api';
import { adaptAnalysisSummary, statusBadge } from '@/services/adapter';
import { timeAgo } from '@/utils/format';
import type { Analysis } from '@/data/types';

function toRows(data: any): any[] {
  if (Array.isArray(data)) return data;
  return data?.items || data?.results || data?.analyses || [];
}

export function WorkspacePage() {
  const { navigate } = useRouter();
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [rawRows, setRawRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await listAnalyses();
        const rows = toRows(data);
        if (!cancelled) {
          setRawRows(rows);
          setAnalyses(rows.map(adaptAnalysisSummary));
        }
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load analyses.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const completed = analyses.filter((a) => a.status === 'completed').length;
  const totalIssues = analyses.reduce((sum, a) => sum + (a.gapsFound || 0), 0);

  return (
    <div className="min-h-screen bg-ivory-50 text-ink-900 dark:bg-[#090D16] dark:text-slate-100">
      <TopNav variant="app" />
      <div className="container-app py-8">
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-ink-900 dark:text-white">Workspace</h1>
            <p className="mt-1 text-sm text-ink-500 dark:text-slate-400">
              {loading ? 'Loading…' : `${analyses.length} ${analyses.length === 1 ? 'analysis' : 'analyses'} · ${completed} completed`}
            </p>
          </div>
          <Button onClick={() => navigate({ name: 'new-analysis' })} leftIcon={<Plus size={16} />}>
            New Analysis
          </Button>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <Card padding="none" className="dark:bg-[#111827]">
              <div className="flex items-center justify-between border-b border-ink-100 px-5 py-4 dark:border-slate-800">
                <h2 className="text-sm font-semibold text-ink-900 dark:text-slate-100">Recent Analyses</h2>
              </div>

              {error ? (
                <div className="px-5 py-10 text-sm text-error-600 dark:text-error-400">{error}</div>
              ) : loading ? (
                <div className="flex items-center gap-2 px-5 py-10 text-sm text-ink-500 dark:text-slate-400">
                  <Loader2 size={16} className="animate-spin" /> Loading analyses…
                </div>
              ) : analyses.length === 0 ? (
                <div className="px-5 py-12 text-center text-sm text-ink-500 dark:text-slate-400">
                  No analyses yet. Start your first one.
                </div>
              ) : (
                <div className="divide-y divide-ink-100 dark:divide-slate-800">
                  {analyses.map((analysis, i) => {
                    const badge = statusBadge(rawRows[i]?.status ?? analysis.status);
                    const done = analysis.status === 'completed';
                    return (
                      <button
                        key={analysis.id}
                        onClick={() => navigate({ name: 'analysis', analysisId: analysis.id, tab: 'overview' })}
                        className="flex w-full items-center gap-4 px-5 py-4 text-left transition-colors hover:bg-ivory-50 dark:hover:bg-slate-800/50"
                      >
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-ivory-100 text-ink-500 dark:bg-slate-800">
                          {done ? (
                            <CheckCircle2 size={18} className="text-success-500" />
                          ) : analysis.status === 'failed' ? (
                            <AlertTriangle size={18} className="text-error-500" />
                          ) : (
                            <Clock size={18} className="text-blue-500" />
                          )}
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm font-medium text-ink-900 dark:text-slate-100">{analysis.title}</p>
                          <p className="mt-0.5 text-xs text-ink-500 dark:text-slate-400">
                            {analysis.createdAt ? timeAgo(analysis.createdAt) : '—'}
                            {done && analysis.gapsFound > 0 ? ` · ${analysis.gapsFound} issue${analysis.gapsFound === 1 ? '' : 's'} flagged` : ''}
                          </p>
                        </div>
                        <Badge variant={badge.variant}>{badge.label}</Badge>
                        <ArrowRight size={15} className="shrink-0 text-ink-300" />
                      </button>
                    );
                  })}
                </div>
              )}
            </Card>
          </div>

          <div className="space-y-4">
            <Card padding="md" className="dark:bg-[#111827]">
              <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-ink-500 dark:text-slate-400">At a glance</h3>
              <div className="space-y-3">
                <Stat icon={<FileStack size={16} className="text-blue-500" />} label="Total analyses" value={loading ? '—' : String(analyses.length)} />
                <Stat icon={<CheckCircle2 size={16} className="text-success-500" />} label="Completed" value={loading ? '—' : String(completed)} />
                <Stat icon={<AlertTriangle size={16} className="text-warning-500" />} label="Issues flagged" value={loading ? '—' : String(totalIssues)} />
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

function Stat({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-ivory-100 dark:bg-slate-800">{icon}</div>
      <div className="min-w-0 flex-1">
        <p className="text-xs text-ink-500 dark:text-slate-400">{label}</p>
      </div>
      <p className="text-lg font-semibold text-ink-900 dark:text-white">{value}</p>
    </div>
  );
}
