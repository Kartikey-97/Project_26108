import { Card } from '@/components/ui/Card';
import type { EvidenceChainItem } from '@/data/types';

export function AnalysisEvidenceTab({ evidence }: { evidence: EvidenceChainItem[] }) {
  if (evidence.length === 0) {
    return <Card padding="lg"><p className="text-sm text-ink-500">No evidence chains were produced for this analysis.</p></Card>;
  }

  return (
    <div className="space-y-4">
      {evidence.map((ev) => (
        <Card key={ev.id} padding="md">
          <div className="mb-2 flex items-center justify-between gap-3">
            <span className="font-mono text-xs font-bold text-teal-800">{ev.standard}</span>
            {ev.sourceLocation && <span className="text-xs text-ink-400">{ev.sourceLocation}</span>}
          </div>
          <h4 className="mb-2 text-sm font-bold">{ev.requirement}</h4>
          <blockquote className="border-l-2 border-teal-500 bg-ivory-50 py-1 pl-3 text-xs italic">
            "{ev.evidence}"
          </blockquote>
          <div className="mt-3 rounded border border-ink-100 bg-white p-2 text-xs">
            <span className="block font-semibold">Conclusion:</span>
            {ev.conclusion}
          </div>
        </Card>
      ))}
    </div>
  );
}
