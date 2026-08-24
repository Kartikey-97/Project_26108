import { useState } from 'react';
import { GitBranch } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { getRelationshipsByAnalysisId } from '@/data/mockData';

export function AnalysisRelationshipsTab({ analysisId }: { analysisId: string }) {
  const rels = getRelationshipsByAnalysisId(analysisId);
  return (
    <div className="space-y-4">
      <Card padding="md">
        <h3 className="font-bold mb-4 flex items-center gap-2"><GitBranch size={16}/> Relationship Graph Data</h3>
        <div className="space-y-3">
          {rels.map((r) => (
            <div key={r.id} className="p-3 bg-ivory-50 rounded border border-ink-100 text-xs">
              <span className="font-mono font-bold text-teal-800">{r.label}</span>
              <p className="mt-1 text-ink-700">{r.description}</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
