import { useEffect, useState } from 'react';
import { Download, Eye, FileText, Loader2 } from 'lucide-react';
import { TopNav } from '@/components/TopNav';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { useRouter } from '@/router';
import { getReport, listAnalyses } from '@/services/api';
import { adaptAnalysisSummary, statusBadge } from '@/services/adapter';
import { formatDate } from '@/utils/format';
import type { Analysis } from '@/data/types';

function toRows(data: any): any[] {
  if (Array.isArray(data)) return data;
  return data?.items || data?.results || data?.analyses || [];
}

interface ReportRow {
  analysis: Analysis;
  rawStatus: string;
}

export function ReportsPage() {
  const { navigate } = useRouter();
  const [reports, setReports] = useState<ReportRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await listAnalyses();
        const rows = toRows(data)
          .map((raw) => ({ analysis: adaptAnalysisSummary(raw), rawStatus: raw?.status ?? '' }))
          // A report exists once the analysis reaches a terminal, successful state.
          .filter((r) => r.analysis.status === 'completed');
        if (!cancelled) setReports(rows);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load reports.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleDownload(id: string, title: string) {
    setDownloadingId(id);
    setError(null);
    try {
      const report = await getReport(id);
      const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${title.replace(/[^a-z0-9]+/gi, '_').slice(0, 60) || 'analysis'}_report.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Report download failed.');
    } finally {
      setDownloadingId(null);
    }
  }

  return (
    <div className="min-h-screen bg-ivory-50 text-ink-900 dark:bg-[#090D16] dark:text-slate-100">
      <TopNav variant="app" />
      <div className="container-app py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold tracking-tight text-ink-900 dark:text-white">Defensible Reports</h1>
          <p className="mt-1 text-sm text-ink-500 dark:text-slate-400">
            Every completed analysis produces an evidence-backed report you can view or export.
          </p>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-error-200 bg-error-50 px-4 py-3 text-sm text-error-700 dark:border-error-900/50 dark:bg-error-900/20 dark:text-error-300">
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center gap-2 py-16 text-sm text-ink-500 dark:text-slate-400">
            <Loader2 size={16} className="animate-spin" /> Loading reports…
          </div>
        ) : reports.length === 0 ? (
          <div className="py-16 text-center text-sm text-ink-500 dark:text-slate-400">
            No completed reports yet. Run an analysis to generate one.
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {reports.map(({ analysis, rawStatus }) => {
              const badge = statusBadge(rawStatus || analysis.status);
              return (
                <Card key={analysis.id} padding="lg" className="flex h-full flex-col dark:bg-[#111827]">
                  <div className="mb-3 flex items-start justify-between gap-2">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-teal-50 text-teal-600 dark:bg-teal-900/30 dark:text-teal-300">
                      <FileText size={16} />
                    </div>
                    <Badge variant={badge.variant}>{badge.label}</Badge>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-sm font-semibold text-ink-900 dark:text-slate-100">{analysis.title}</h3>
                    <p className="mt-1 text-xs text-ink-500 dark:text-slate-400">
                      {analysis.completedAt ? formatDate(analysis.completedAt) : analysis.createdAt ? formatDate(analysis.createdAt) : '—'}
                      {analysis.gapsFound > 0 ? ` · ${analysis.gapsFound} issue${analysis.gapsFound === 1 ? '' : 's'}` : ''}
                    </p>
                  </div>
                  <div className="mt-4 grid grid-cols-2 gap-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      leftIcon={<Eye size={13} />}
                      onClick={() => navigate({ name: 'analysis', analysisId: analysis.id, tab: 'evidence' })}
                    >
                      View
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      leftIcon={downloadingId === analysis.id ? <Loader2 size={13} className="animate-spin" /> : <Download size={13} />}
                      disabled={downloadingId === analysis.id}
                      onClick={() => handleDownload(analysis.id, analysis.title)}
                    >
                      {downloadingId === analysis.id ? 'Exporting' : 'Download'}
                    </Button>
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
