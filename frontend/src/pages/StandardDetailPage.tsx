import { useEffect, useState } from 'react';
import { AlertTriangle, ArrowLeft, Loader2, ShieldCheck } from 'lucide-react';
import { TopNav } from '@/components/TopNav';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { useRouter } from '@/router';
import { getStandard } from '@/services/api';
import { adaptStandard } from '@/services/adapter';
import type { Standard } from '@/data/types';

interface Props {
  standardId: string;
}

export function StandardDetailPage({ standardId }: Props) {
  const { navigate } = useRouter();
  const [standard, setStandard] = useState<Standard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    (async () => {
      try {
        const data = await getStandard(standardId);
        if (!cancelled) setStandard(adaptStandard(data));
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load this standard.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [standardId]);

  return (
    <div className="min-h-screen bg-ivory-50 pb-16 text-ink-900 dark:bg-[#090D16] dark:text-slate-100">
      <TopNav variant="app" />
      <div className="container-app space-y-6 py-6">
        <button
          onClick={() => navigate({ name: 'standards' })}
          className="flex items-center gap-1 text-xs text-ink-500 hover:text-ink-900 dark:text-slate-400 dark:hover:text-white"
        >
          <ArrowLeft size={14} /> Back to standards
        </button>

        {loading ? (
          <div className="flex items-center gap-2 py-16 text-sm text-ink-500 dark:text-slate-400">
            <Loader2 size={16} className="animate-spin" /> Loading standard…
          </div>
        ) : error ? (
          <div className="rounded-lg border border-error-200 bg-error-50 px-4 py-3 text-sm text-error-700 dark:border-error-900/50 dark:bg-error-900/20 dark:text-error-300">
            {error}
          </div>
        ) : !standard ? (
          <div className="py-16 text-center text-sm text-ink-500 dark:text-slate-400">Standard not found.</div>
        ) : (
          <>
            <Card padding="lg" className="dark:bg-[#111827]">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h1 className="font-mono text-xl font-bold tracking-tight text-ink-900 sm:text-2xl dark:text-white">
                    {standard.number}
                  </h1>
                  <h2 className="mt-1.5 text-base font-semibold text-ink-800 dark:text-slate-200">{standard.title}</h2>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <Badge variant={standard.status === 'current' ? 'success' : standard.status === 'withdrawn' || standard.status === 'superseded' ? 'error' : 'neutral'}>
                    {standard.revision}
                  </Badge>
                  {standard.regulatory && (
                    <Badge variant="warning" icon={<ShieldCheck size={12} className="mr-1" />}>
                      QCO mandatory
                    </Badge>
                  )}
                </div>
              </div>
              <p className="mt-3 text-sm leading-relaxed text-ink-600 dark:text-slate-400">{standard.summary}</p>
            </Card>

            {standard.regulatory && standard.regulatoryNote && (
              <Card padding="md" className="border-warning-200 bg-warning-50 dark:border-warning-900/50 dark:bg-warning-900/20">
                <div className="flex gap-2.5">
                  <AlertTriangle size={16} className="mt-0.5 shrink-0 text-warning-600" />
                  <div>
                    <p className="text-sm font-semibold text-warning-800 dark:text-warning-300">Regulatory requirement</p>
                    <p className="mt-1 text-[13px] text-warning-700 dark:text-warning-200/80">{standard.regulatoryNote}</p>
                    {standard.certificationBody && (
                      <p className="mt-1 text-xs text-warning-700/80 dark:text-warning-200/60">
                        Certification body: {standard.certificationBody}
                      </p>
                    )}
                  </div>
                </div>
              </Card>
            )}

            <div className="grid gap-4 sm:grid-cols-2">
              <Card padding="md" className="dark:bg-[#111827]">
                <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-ink-500 dark:text-slate-400">Details</h3>
                <dl className="space-y-2 text-sm">
                  <Row label="Division / Council" value={standard.category || '—'} />
                  <Row label="Edition" value={standard.edition} />
                  <Row label="Year" value={standard.yearPublished ? String(standard.yearPublished) : '—'} />
                  <Row label="ICS / Section" value={standard.section || '—'} />
                  <Row label="Superseded by" value={standard.supersededBy || '—'} />
                </dl>
              </Card>

              <Card padding="md" className="dark:bg-[#111827]">
                <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-ink-500 dark:text-slate-400">Amendments</h3>
                {standard.amendments && standard.amendments.length > 0 ? (
                  <ul className="space-y-1.5 text-[13px] text-ink-700 dark:text-slate-300">
                    {standard.amendments.map((a, i) => (
                      <li key={i} className="flex gap-2">
                        <span className="text-ink-300">•</span> {a}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-[13px] text-ink-500 dark:text-slate-400">No amendments recorded.</p>
                )}
              </Card>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-4">
      <dt className="shrink-0 text-ink-500 dark:text-slate-400">{label}</dt>
      <dd className="text-right font-medium text-ink-800 dark:text-slate-200">{value}</dd>
    </div>
  );
}
