import { useState } from 'react';
import { BookMarked, ExternalLink, Columns } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useRouter } from '@/router';
import { getStandardById, getMatchedRequirementsByAnalysisId } from '@/data/mockData';
import type { Analysis, Standard } from '@/data/types';

export function AnalysisStandardsTab({ analysis }: { analysis: Analysis }) {
  const { navigate } = useRouter();
  const matchedStandards = analysis.matchedStandardIds.map(id => getStandardById(id)).filter((s): s is Standard => !!s);

  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-2">
        {matchedStandards.map((std) => (
          <Card key={std.id} padding="md" className="h-full flex flex-col justify-between">
            <div>
              <h4 className="text-sm font-bold font-mono text-ink-900">{std.number}</h4>
              <p className="text-xs text-ink-600 mt-1">{std.title}</p>
            </div>
            <div className="mt-4 flex gap-2">
              <Button size="sm" variant="secondary" onClick={() => navigate({ name: 'standard', standardId: std.id })}>
                View Detail
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
