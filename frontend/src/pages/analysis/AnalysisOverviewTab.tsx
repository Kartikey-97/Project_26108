import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { useRouter } from '@/router';
import type { Analysis, MatchedRequirementItem, Standard } from '@/data/types';

interface Props {
  analysis: Analysis;
  standards: Standard[];
  matchedRequirements: MatchedRequirementItem[];
  primaryStandard: Standard | null;
}

export function AnalysisOverviewTab({ analysis, matchedRequirements, primaryStandard }: Props) {
  const { navigate } = useRouter();

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Card padding="md" interactive onClick={() => navigate({ name: 'analysis', analysisId: analysis.id, tab: 'standards' })}>
          <h4 className="text-xs font-semibold uppercase text-ink-500">Applicable Standards</h4>
          <p className="mt-2 text-2xl font-bold">{analysis.standardsIdentified}</p>
        </Card>
        <Card padding="md" interactive onClick={() => navigate({ name: 'analysis', analysisId: analysis.id, tab: 'gaps' })}>
          <h4 className="text-xs font-semibold uppercase text-ink-500">Issues Detected</h4>
          <p className="mt-2 text-2xl font-bold text-warning-600">{analysis.gapsFound}</p>
        </Card>
        <Card padding="md" interactive onClick={() => navigate({ name: 'analysis', analysisId: analysis.id, tab: 'certification' })}>
          <h4 className="text-xs font-semibold uppercase text-ink-500">Certifications</h4>
          <p className="mt-2 text-2xl font-bold text-blue-600">{analysis.certificationsRequired}</p>
        </Card>
        <Card padding="md">
          <h4 className="text-xs font-semibold uppercase text-ink-500">Avg. Confidence</h4>
          <p className="mt-2 text-2xl font-bold text-teal-600">{analysis.confidence}%</p>
        </Card>
      </div>

      {primaryStandard && (
        <Card padding="lg" className="border-teal-200 shadow-card">
          <Badge variant="teal">Primary Applicable Standard</Badge>
          <h2 className="mt-2 text-lg font-bold">{primaryStandard.number} — {primaryStandard.title}</h2>
          <p className="mt-2 text-sm text-ink-600">{primaryStandard.whyApplies || primaryStandard.summary}</p>
        </Card>
      )}

      <Card padding="lg">
        <h3 className="mb-4 text-sm font-semibold">Matched Procurement Requirements</h3>
        {matchedRequirements.length === 0 ? (
          <p className="text-xs text-ink-500">No requirements were extracted for this analysis.</p>
        ) : (
          <div className="space-y-2">
            {matchedRequirements.slice(0, 6).map((req) => (
              <div key={req.id} className="flex items-center justify-between gap-3 rounded-lg border border-ink-100 bg-ivory-50 p-3">
                <span className="text-xs font-semibold">{req.requirement}</span>
                <Badge variant={req.status === 'covered' ? 'success' : req.status === 'not-found' ? 'error' : 'warning'}>{req.status}</Badge>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
