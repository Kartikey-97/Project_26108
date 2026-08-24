import { GitBranch } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import type { StandardRelationship } from '@/data/types';

export function AnalysisRelationshipsTab({ relationships }: { relationships: StandardRelationship[] }) {
  return (
    <div className="space-y-4">
      <Card padding="md">
        <h3 className="mb-4 flex items-center gap-2 font-bold"><GitBranch size={16} /> Standard Relationships</h3>
        {relationships.length === 0 ? (
          <p className="text-xs text-ink-500">No normative references were reported for the matched standards.</p>
        ) : (
          <div className="space-y-3">
            {relationships.map((r) => (
              <div key={r.id} className="rounded border border-ink-100 bg-ivory-50 p-3 text-xs">
                <span className="font-mono font-bold text-teal-800">{r.label}</span>
                <p className="mt-1 text-ink-700">{r.description}</p>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
