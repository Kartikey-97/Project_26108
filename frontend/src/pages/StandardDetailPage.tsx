import { useState } from 'react';
import { ArrowLeft, BookOpen, Columns, ExternalLink, History, Layers } from 'lucide-react';
import { TopNav } from '@/components/TopNav';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { useRouter } from '@/router';
import { getStandardById } from '@/data/mockData';
import { StandardComparisonModal } from '@/components/standards/StandardComparisonModal';

interface Props { standardId: string; }

export function StandardDetailPage({ standardId }: Props) {
  const { navigate } = useRouter();
  const standard = getStandardById(standardId);
  const [isCompareOpen, setIsCompareOpen] = useState(false);

  if (!standard) return <div>Not found</div>;

  return (
    <div className="min-h-screen bg-ivory-50 text-ink-900 pb-16 dark:bg-[#090D16] dark:text-slate-100">
      <TopNav variant="app" />
      <div className="container-app py-6 space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <button onClick={() => navigate({ name: 'standards' })} className="flex items-center gap-1 hover:text-ink-900 text-xs">
            <ArrowLeft size={14} /> Back
          </button>
          <Button variant="secondary" size="sm" onClick={() => setIsCompareOpen(true)}>Compare</Button>
        </div>
        
        <Card padding="lg">
          <h1 className="text-xl font-bold tracking-tight text-ink-900 sm:text-2xl font-mono">{standard.number}</h1>
          <h2 className="mt-1.5 text-base font-semibold text-ink-800">{standard.title}</h2>
          <p className="mt-2 text-sm text-ink-600">{standard.summary}</p>
        </Card>

        <StandardComparisonModal
          standardAId={standard.id}
          standardBId="std-1944"
          isOpen={isCompareOpen}
          onClose={() => setIsCompareOpen(false)}
        />
      </div>
    </div>
  );
}
