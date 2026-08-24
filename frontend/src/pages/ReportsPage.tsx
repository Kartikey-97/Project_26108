import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Download, Eye, FileText, Filter, Printer, Search, X } from 'lucide-react';
import { TopNav } from '@/components/TopNav';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { useRouter } from '@/router';
import { reports, getAnalysisById } from '@/data/mockData';
import { formatDate } from '@/utils/format';
import type { Report, ReportType } from '@/data/types';

export function ReportsPage() {
  const { navigate } = useRouter();
  const [search, setSearch] = useState('');
  
  return (
    <div className="min-h-screen bg-ivory-50 text-ink-900 dark:bg-[#090D16] dark:text-slate-100">
      <TopNav variant="app" />
      <div className="container-app py-8">
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-ink-900 dark:text-white">Defensible Reports</h1>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {reports.map((report, i) => {
            const analysis = getAnalysisById(report.analysisId);
            return (
              <Card key={report.id} padding="lg" interactive className="flex h-full flex-col">
                <div className="mt-4 flex-1">
                  <h3 className="text-sm font-semibold text-ink-900 dark:text-slate-100">{report.title}</h3>
                </div>
                <div className="mt-4 grid grid-cols-2 gap-2">
                  <Button variant="secondary" size="sm" leftIcon={<Eye size={13} />}>
                    View Brief
                  </Button>
                  <Button variant="secondary" size="sm" leftIcon={<Download size={13} />}>
                    Download
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
