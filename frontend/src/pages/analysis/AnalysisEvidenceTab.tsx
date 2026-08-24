import { useState } from 'react';
import { ScrollText, FileSearch } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { getEvidenceChainsByAnalysisId } from '@/data/mockData';
import type { Analysis } from '@/data/types';

export function AnalysisEvidenceTab({ analysis }: { analysis: Analysis }) {
  const evs = getEvidenceChainsByAnalysisId(analysis.id);
  return (
    <div className="space-y-4">
      {evs.map((ev) => (
        <Card key={ev.id} padding="md">
          <div className="flex justify-between mb-2">
            <span className="text-xs font-bold font-mono text-teal-800">{ev.standard}</span>
            <span className="text-xs text-ink-400">{ev.sourceLocation}</span>
          </div>
          <h4 className="text-sm font-bold mb-2">{ev.requirement}</h4>
          <blockquote className="border-l-2 border-teal-500 pl-3 py-1 bg-ivory-50 text-xs italic">
            "{ev.evidence}"
          </blockquote>
          <div className="mt-3 text-xs bg-white border border-ink-100 p-2 rounded">
            <span className="font-semibold block">Conclusion:</span>
            {ev.conclusion}
          </div>
        </Card>
      ))}
    </div>
  );
}
