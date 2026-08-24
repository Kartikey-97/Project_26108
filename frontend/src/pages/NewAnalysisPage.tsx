import { useState } from 'react';
import { motion } from 'motion/react';
import { ArrowLeft, ArrowRight, FileUp, Sparkles, FileText, CheckCircle2 } from 'lucide-react';
import { TopNav } from '@/components/TopNav';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useRouter } from '@/router';

export function NewAnalysisPage() {
  const { navigate } = useRouter();
  const [analysisTitle, setAnalysisTitle] = useState('LED Street Lighting — Urban Smart Highway NIT');
  
  return (
    <div className="min-h-screen bg-ivory-50 text-ink-900 dark:bg-[#090D16] dark:text-slate-100">
      <TopNav variant="app" />
      <main className="container-app py-8 max-w-4xl">
        <div className="mb-6 flex items-center justify-between">
          <button onClick={() => navigate({ name: 'workspace' })} className="inline-flex items-center gap-1.5 text-xs font-medium text-ink-500 transition-colors hover:text-ink-900">
            <ArrowLeft size={14} /> Back to Workspace
          </button>
        </div>
        
        <div className="mb-8">
          <h1 className="text-2xl font-semibold tracking-tight text-ink-900 sm:text-3xl dark:text-white">Start a procurement analysis</h1>
        </div>

        <Card padding="md" className="mb-6 bg-white border-ink-200 shadow-soft">
          <label className="block text-xs font-semibold text-ink-700 uppercase tracking-wider mb-1.5">Analysis Reference Title</label>
          <input
            type="text"
            value={analysisTitle}
            onChange={(e) => setAnalysisTitle(e.target.value)}
            className="input text-sm font-medium"
          />
        </Card>

        <div className="flex gap-2">
          <Button
            onClick={() => navigate({ name: 'analysis', analysisId: 'an-001', tab: 'overview' })}
            rightIcon={<ArrowRight size={15} />}
            className="shadow-soft"
          >
            Extract Procurement Profile
          </Button>
        </div>
      </main>
    </div>
  );
}
