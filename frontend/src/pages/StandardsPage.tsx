import { useEffect, useState } from 'react';
import { ExternalLink, Loader2, Search } from 'lucide-react';
import { TopNav } from '@/components/TopNav';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { useRouter } from '@/router';
import { listStandards, searchStandards } from '@/services/api';
import { adaptStandard } from '@/services/adapter';
import type { Standard } from '@/data/types';

// The backend returns either a bare array or a wrapped object depending on the route.
function toRows(data: any): any[] {
  if (Array.isArray(data)) return data;
  return data?.items || data?.results || data?.standards || [];
}

export function StandardsPage() {
  const { navigate } = useRouter();
  const [query, setQuery] = useState('');
  const [items, setItems] = useState<Standard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const q = query.trim();
    setLoading(true);
    setError(null);
    const timer = setTimeout(async () => {
      try {
        const data = q.length >= 2 ? await searchStandards(q) : await listStandards(0, 24);
        if (!cancelled) setItems(toRows(data).map(adaptStandard));
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load standards.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }, q ? 300 : 0);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [query]);

  return (
    <div className="min-h-screen bg-ivory-50 text-ink-900 dark:bg-[#090D16] dark:text-slate-100">
      <TopNav variant="app" />
      <div className="container-app space-y-6 py-8">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-ink-900 dark:text-white">Standards intelligence</h1>
          <p className="mt-1 text-sm text-ink-500 dark:text-slate-400">
            Search the live BIS catalog. QCO-notified standards require mandatory certification.
          </p>
        </div>

        <div className="relative max-w-xl">
          <Search size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by designation, title or keyword (min 2 characters)…"
            className="input pl-9 text-sm"
          />
        </div>

        {error && (
          <div className="rounded-lg border border-error-200 bg-error-50 px-4 py-3 text-sm text-error-700 dark:border-error-900/50 dark:bg-error-900/20 dark:text-error-300">
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center gap-2 py-16 text-sm text-ink-500 dark:text-slate-400">
            <Loader2 size={16} className="animate-spin" /> Loading standards…
          </div>
        ) : items.length === 0 ? (
          <div className="py-16 text-center text-sm text-ink-500 dark:text-slate-400">
            {query.trim().length >= 2 ? `No standards match “${query.trim()}”.` : 'No standards available.'}
          </div>
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            {items.map((std) => (
              <Card key={std.id} padding="md" interactive className="flex flex-col bg-white dark:bg-[#111827]">
                <div className="mb-1.5 flex items-start justify-between gap-2">
                  <h4 className="font-mono text-xs font-semibold text-ink-900 dark:text-slate-100">{std.number}</h4>
                  {std.regulatory && <Badge variant="warning">QCO</Badge>}
                </div>
                <p className="mb-3 line-clamp-2 text-[13px] text-ink-700 dark:text-slate-300">{std.title}</p>
                <div className="mt-auto flex items-center justify-between">
                  <Badge variant={std.status === 'current' ? 'success' : std.status === 'withdrawn' || std.status === 'superseded' ? 'error' : 'neutral'}>
                    {std.revision}
                  </Badge>
                  <Button size="sm" variant="ghost" onClick={() => navigate({ name: 'standard', standardId: std.id })}>
                    View detail <ExternalLink size={12} className="ml-1" />
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
