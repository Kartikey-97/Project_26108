import { useState } from 'react';
import { ShieldCheck, ExternalLink } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { getRegulatoryRequirementsByAnalysisId } from '@/data/mockData';
import type { Analysis } from '@/data/types';

export function AnalysisCertificationTab({ analysis }: { analysis: Analysis }) {
  const reqs = getRegulatoryRequirementsByAnalysisId(analysis.id);
  return (
    <div className="space-y-4">
      <div className="grid gap-3">
        {reqs.map((req) => (
          <Card key={req.id} padding="md">
            <div className="flex justify-between">
              <h4 className="text-sm font-bold">{req.requirement}</h4>
              <Badge variant="blue">{req.status.toUpperCase()}</Badge>
            </div>
            <p className="text-xs mt-1 text-ink-500">Authority: {req.issuingAuthority}</p>
            <p className="text-xs mt-3">{req.whyAppliesText}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}
