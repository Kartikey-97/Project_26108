import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { useRouter } from '@/router';
import type { Standard } from '@/data/types';

export function AnalysisStandardsTab({ standards }: { standards: Standard[] }) {
  const { navigate } = useRouter();

  if (standards.length === 0) {
    return <Card padding="lg"><p className="text-sm text-ink-500">No applicable standards were identified.</p></Card>;
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-2">
        {standards.map((std) => (
          <Card key={std.id} padding="md" className="flex h-full flex-col justify-between">
            <div>
              <div className="flex items-center justify-between gap-2">
                <h4 className="font-mono text-sm font-bold text-ink-900">{std.number}</h4>
                {std.regulatory && <Badge variant="blue">QCO</Badge>}
              </div>
              <p className="mt-1 text-xs text-ink-600">{std.title}</p>
            </div>
            <div className="mt-4 flex items-center gap-2">
              <Button size="sm" variant="secondary" onClick={() => navigate({ name: 'standard', standardId: std.id })}>
                View Detail
              </Button>
              {typeof std.applicabilityScore === 'number' && (
                <span className="text-xs font-medium text-teal-700">{std.applicabilityScore}% match</span>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
