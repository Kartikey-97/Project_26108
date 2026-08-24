import { useState } from 'react';
import { ShieldAlert, FileCheck2, ArrowRight } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { getSpecificationRequirementsByAnalysisId } from '@/data/mockData';
import type { Analysis } from '@/data/types';

export function AnalysisGapsTab({ analysisId }: { analysisId: string }) {
  const reqs = getSpecificationRequirementsByAnalysisId(analysisId);
  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-2">
        {reqs.map((req) => (
          <Card key={req.id} padding="md">
            <Badge variant={req.status === 'covered' ? 'success' : req.status === 'missing' ? 'error' : 'warning'}>
              {req.status.toUpperCase()}
            </Badge>
            <h4 className="text-sm font-bold mt-2">{req.requirement}</h4>
            <p className="text-xs text-ink-600 mt-1 italic">"{req.tenderEvidence}"</p>
            <div className="mt-3 p-2 bg-ivory-50 rounded text-xs text-ink-700">
              <span className="font-semibold block">Recommendation:</span>
              {req.suggestedAction || req.whyMatters}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
