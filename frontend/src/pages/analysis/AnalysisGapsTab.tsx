import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import type { SpecificationRequirement } from '@/data/types';

const STATUS_VARIANT: Record<SpecificationRequirement['status'], 'success' | 'error' | 'warning'> = {
  covered: 'success',
  missing: 'error',
  conflicting: 'error',
  restrictive: 'warning',
  review: 'warning',
};

export function AnalysisGapsTab({ specRequirements }: { specRequirements: SpecificationRequirement[] }) {
  if (specRequirements.length === 0) {
    return <Card padding="lg"><p className="text-sm text-ink-500">No specification requirements were assessed.</p></Card>;
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-2">
        {specRequirements.map((req) => (
          <Card key={req.id} padding="md">
            <Badge variant={STATUS_VARIANT[req.status] || 'warning'}>{req.status.toUpperCase()}</Badge>
            <h4 className="mt-2 text-sm font-bold">{req.requirement}</h4>
            {req.tenderEvidence && <p className="mt-1 text-xs italic text-ink-600">"{req.tenderEvidence}"</p>}
            <div className="mt-3 rounded bg-ivory-50 p-2 text-xs text-ink-700">
              <span className="block font-semibold">Recommendation:</span>
              {req.suggestedAction || req.whyMatters || 'No specific action recommended.'}
            </div>
            {req.applicableStandard && req.applicableStandard !== 'Not mapped' && (
              <p className="mt-2 font-mono text-[11px] text-teal-700">{req.applicableStandard}</p>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
