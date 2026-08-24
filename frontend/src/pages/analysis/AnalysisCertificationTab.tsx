import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import type { RegulatoryRequirement } from '@/data/types';

export function AnalysisCertificationTab({ regulatory }: { regulatory: RegulatoryRequirement[] }) {
  if (regulatory.length === 0) {
    return (
      <Card padding="lg">
        <p className="text-sm text-ink-500">No mandatory certification (QCO) requirements were identified for the matched standards.</p>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-3">
        {regulatory.map((req) => (
          <Card key={req.id} padding="md">
            <div className="flex items-start justify-between gap-3">
              <h4 className="text-sm font-bold">{req.requirement}</h4>
              <Badge variant="blue">{req.status.toUpperCase()}</Badge>
            </div>
            <p className="mt-1 text-xs text-ink-500">Authority: {req.issuingAuthority}</p>
            <p className="mt-3 text-xs text-ink-700">{req.whyAppliesText}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}
