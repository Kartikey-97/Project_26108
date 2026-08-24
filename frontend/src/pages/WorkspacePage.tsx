import { motion } from 'motion/react';
import {
  Activity as ActivityIcon,
  ArrowRight,
  CheckCircle2,
  Clock,
  FileStack,
  FileText,
  Filter,
  Plus,
  Search,
  ShieldCheck,
  TrendingUp,
  Users,
} from 'lucide-react';
import { TopNav } from '@/components/TopNav';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Avatar } from '@/components/ui/Avatar';
import { useRouter } from '@/router';
import {
  analyses,
  analysisStatusConfig,
  getMemberById,
  recentActivity,
  workspaceMembers,
} from '@/data/mockData';
import { formatDate, timeAgo } from '@/utils/format';

export function WorkspacePage() {
  const { navigate } = useRouter();
  const completedAnalyses = analyses.filter((a) => a.status === 'completed');

  return (
    <div className="min-h-screen bg-ivory-50 text-ink-900 dark:bg-[#090D16] dark:text-slate-100">
      <TopNav variant="app" />
      <div className="container-app py-8">
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-ink-900 dark:text-white">Workspace</h1>
            <p className="mt-1 text-sm text-ink-500 dark:text-slate-400">
              {analyses.length} analyses · {workspaceMembers.length} team members
            </p>
          </div>
          <Button onClick={() => navigate({ name: 'new-analysis' })} leftIcon={<Plus size={16} />}>
            New Analysis
          </Button>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <Card padding="none">
              <div className="flex items-center justify-between border-b border-ink-100 px-5 py-4">
                <h2 className="text-sm font-semibold text-ink-900">Recent Analyses</h2>
              </div>
              <div className="divide-y divide-ink-100">
                {analyses.map((analysis) => {
                  const status = analysisStatusConfig[analysis.status];
                  return (
                    <button
                      key={analysis.id}
                      onClick={() => navigate({ name: 'analysis', analysisId: analysis.id, tab: 'overview' })}
                      className="flex w-full items-center gap-4 px-5 py-4 text-left transition-colors hover:bg-ivory-50"
                    >
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-ivory-100 text-ink-500">
                        {analysis.status === 'completed' ? <CheckCircle2 size={18} className="text-success-500" /> : <Clock size={18} className="text-blue-500" />}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <p className="truncate text-sm font-medium text-ink-900">{analysis.title}</p>
                        </div>
                      </div>
                      <Badge variant={status.variant}>{status.label}</Badge>
                      <ArrowRight size={15} className="shrink-0 text-ink-300" />
                    </button>
                  );
                })}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
