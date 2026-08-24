import { useState } from 'react';
import { Columns, ExternalLink, Search } from 'lucide-react';
import { TopNav } from '@/components/TopNav';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useRouter } from '@/router';
import { standards } from '@/data/mockData';

export function StandardsPage() {
  const { navigate } = useRouter();
  const [search, setSearch] = useState('');

  return (
    <div className="min-h-screen bg-ivory-50 text-ink-900 dark:bg-[#090D16] dark:text-slate-100">
      <TopNav variant="app" />
      <div className="container-app py-8 space-y-6">
        <h1 className="text-2xl font-bold tracking-tight text-ink-900 dark:text-white">Standards intelligence</h1>
        <div className="grid gap-3 md:grid-cols-2">
          {standards.map((std) => (
            <Card key={std.id} padding="md" className="bg-white">
              <h4 className="text-xs font-semibold text-ink-900 mb-1">{std.number}</h4>
              <p className="text-[11px] text-ink-600 line-clamp-2 mb-2">{std.title}</p>
              <Button size="sm" variant="ghost" onClick={() => navigate({ name: 'standard', standardId: std.id })}>
                View Detail <ExternalLink size={12} className="ml-1"/>
              </Button>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
