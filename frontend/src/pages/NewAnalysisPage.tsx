import { useState } from 'react';
import { ArrowLeft, ArrowRight, FileUp, FileText, Loader2, Sparkles, X } from 'lucide-react';
import { TopNav } from '@/components/TopNav';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useRouter } from '@/router';
import { createAnalysis, getSampleDocument, waitForAnalysis } from '@/services/api';
import { statusBadge } from '@/services/adapter';

type Phase = 'idle' | 'submitting' | 'polling' | 'error';

export function NewAnalysisPage() {
  const { navigate } = useRouter();
  const [title, setTitle] = useState('');
  const [text, setText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [phase, setPhase] = useState<Phase>('idle');
  const [progress, setProgress] = useState('');
  const [error, setError] = useState<string | null>(null);

  const busy = phase === 'submitting' || phase === 'polling';
  const canSubmit = !busy && (text.trim().length > 0 || file !== null);

  async function handleUseSample() {
    setError(null);
    try {
      const sample = await getSampleDocument();
      setFile(sample);
      setText('');
      if (!title.trim()) setTitle('LED Street Lighting — Urban Smart Highway NIT');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not load the bundled sample document.');
    }
  }

  async function handleSubmit() {
    if (!canSubmit) return;
    setError(null);
    setPhase('submitting');
    setProgress('Uploading specification…');
    try {
      const res = await createAnalysis({
        text: file ? undefined : text.trim(),
        file: file ?? undefined,
        category: undefined,
        department: undefined,
        tenderTitle: title.trim() || undefined,
      });
      const id = res?.analysis_id;
      if (!id) throw new Error('The server did not return an analysis id.');

      setPhase('polling');
      const final = await waitForAnalysis(id, (a: { status?: string }) => {
        setProgress(statusBadge(a?.status ?? '').label);
      });

      if (final?.status === 'failed') {
        setPhase('error');
        setError(final?.degraded_reason || 'The analysis failed to complete. Please try again.');
        return;
      }
      navigate({ name: 'analysis', analysisId: String(id), tab: 'overview' });
    } catch (e) {
      setPhase('error');
      setError(e instanceof Error ? e.message : 'Something went wrong starting the analysis.');
    }
  }

  return (
    <div className="min-h-screen bg-ivory-50 text-ink-900 dark:bg-[#090D16] dark:text-slate-100">
      <TopNav variant="app" />
      <main className="container-app max-w-4xl py-8">
        <div className="mb-6 flex items-center justify-between">
          <button
            onClick={() => navigate({ name: 'workspace' })}
            className="inline-flex items-center gap-1.5 text-xs font-medium text-ink-500 transition-colors hover:text-ink-900 dark:text-slate-400 dark:hover:text-white"
          >
            <ArrowLeft size={14} /> Back to Workspace
          </button>
        </div>

        <div className="mb-8">
          <h1 className="text-2xl font-semibold tracking-tight text-ink-900 sm:text-3xl dark:text-white">
            Start a procurement analysis
          </h1>
          <p className="mt-1.5 text-sm text-ink-500 dark:text-slate-400">
            Paste the tender text or upload a document. StandIQ extracts the requirements, matches BIS
            standards, and builds a defensible evidence trail.
          </p>
        </div>

        <Card padding="md" className="mb-4 border-ink-200 bg-white shadow-soft dark:border-slate-800 dark:bg-[#111827]">
          <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-ink-700 dark:text-slate-300">
            Analysis reference title <span className="font-normal normal-case text-ink-400">(optional)</span>
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. LED Street Lighting — Urban Smart Highway NIT"
            disabled={busy}
            className="input text-sm font-medium"
          />
        </Card>

        <Card padding="md" className="mb-4 border-ink-200 bg-white shadow-soft dark:border-slate-800 dark:bg-[#111827]">
          <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-ink-700 dark:text-slate-300">
            Tender specification text
          </label>
          <textarea
            value={text}
            onChange={(e) => {
              setText(e.target.value);
              if (file) setFile(null);
            }}
            placeholder="Paste the technical specification / NIT clauses here…"
            rows={10}
            disabled={busy || file !== null}
            className="input min-h-[200px] resize-y text-sm leading-relaxed disabled:opacity-50"
          />

          <div className="mt-4 flex flex-wrap items-center gap-3 border-t border-ink-100 pt-4 dark:border-slate-800">
            <label className="inline-flex cursor-pointer items-center gap-2 rounded-lg border border-ink-200 bg-white px-3 py-1.5 text-xs font-medium text-ink-700 transition-colors hover:border-ink-300 hover:bg-ivory-50 dark:border-slate-700 dark:bg-[#161F30] dark:text-slate-200 dark:hover:border-slate-600">
              <FileUp size={14} />
              Upload document
              <input
                type="file"
                accept=".pdf,.doc,.docx,.txt"
                disabled={busy}
                className="hidden"
                onChange={(e) => {
                  const f = e.target.files?.[0] ?? null;
                  if (f) {
                    setFile(f);
                    setText('');
                  }
                }}
              />
            </label>

            <Button variant="ghost" size="sm" onClick={handleUseSample} disabled={busy} leftIcon={<Sparkles size={14} />}>
              Use LED sample tender
            </Button>

            {file && (
              <span className="inline-flex items-center gap-1.5 rounded-lg bg-teal-50 px-2.5 py-1 text-xs font-medium text-teal-700 dark:bg-teal-900/30 dark:text-teal-300">
                <FileText size={13} />
                {file.name}
                <button onClick={() => setFile(null)} disabled={busy} className="hover:text-teal-900 disabled:opacity-50">
                  <X size={13} />
                </button>
              </span>
            )}
          </div>
        </Card>

        {error && (
          <div className="mb-4 rounded-lg border border-error-200 bg-error-50 px-4 py-3 text-sm text-error-700 dark:border-error-900/50 dark:bg-error-900/20 dark:text-error-300">
            {error}
          </div>
        )}

        <div className="flex items-center gap-3">
          <Button onClick={handleSubmit} disabled={!canSubmit} rightIcon={busy ? undefined : <ArrowRight size={15} />} className="shadow-soft">
            {busy ? <Loader2 size={15} className="mr-1.5 animate-spin" /> : null}
            {busy ? (progress || 'Working…') : 'Extract & analyze'}
          </Button>
          {phase === 'polling' && (
            <span className="text-xs text-ink-500 dark:text-slate-400">This usually takes 10–40 seconds.</span>
          )}
        </div>
      </main>
    </div>
  );
}
