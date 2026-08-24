import { useState } from 'react';
import { ArrowRight, CheckCircle2, Clock, FileCheck2, ScrollText, ShieldAlert, ShieldCheck } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { useRouter } from '@/router';
import { getStandardById, getGapsByAnalysisId, getMatchedRequirementsByAnalysisId } from '@/data/mockData';
import type { Analysis, MatchedRequirementItem } from '@/data/types';

interface Props { analysis: Analysis; }

export function AnalysisOverviewTab({ analysis }: Props) {
  const { navigate } = useRouter();
  const primaryStandard = getStandardById('std-10322');
  const initialRequirements = getMatchedRequirementsByAnalysisId(analysis.id);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Card padding="md" interactive onClick={() => navigate({ name: 'analysis', analysisId: analysis.id, tab: 'standards' })}>
          <h4 className="font-semibold text-xs text-ink-500 uppercase">Applicable Standards</h4>
          <p className="text-2xl font-bold mt-2">7</p>
        </Card>
        <Card padding="md" interactive onClick={() => navigate({ name: 'analysis', analysisId: analysis.id, tab: 'gaps' })}>
          <h4 className="font-semibold text-xs text-ink-500 uppercase">Issues Detected</h4>
          <p className="text-2xl font-bold mt-2 text-warning-600">3</p>
        </Card>
      </div>
      
      {primaryStandard && (
        <Card padding="lg" className="border-teal-200 shadow-card">
          <Badge variant="teal">Primary Applicable Standard</Badge>
          <h2 className="mt-2 text-lg font-bold">{primaryStandard.number} — {primaryStandard.title}</h2>
          <p className="mt-2 text-sm text-ink-600">{primaryStandard.whyApplies}</p>
        </Card>
      )}

      <Card padding="lg">
        <h3 className="text-sm font-semibold mb-4">Matched Procurement Requirements</h3>
        <div className="space-y-2">
          {initialRequirements.slice(0, 3).map(req => (
            <div key={req.id} className="p-3 bg-ivory-50 rounded-lg border border-ink-100 flex justify-between">
              <span className="font-semibold text-xs">{req.requirement}</span>
              <Badge variant={req.status === 'covered' ? 'success' : 'warning'}>{req.status}</Badge>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
