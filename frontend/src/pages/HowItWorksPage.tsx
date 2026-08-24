import { motion } from 'motion/react';
import {
  FileText,
  FileSearch,
  Layers,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';
import { TopNav } from '@/components/TopNav';
import { Footer } from '@/components/Footer';
import { Card } from '@/components/ui/Card';
import { useRouter } from '@/router';

export function HowItWorksPage() {
  const { navigate } = useRouter();

  return (
    <div className="min-h-screen bg-ivory-50 text-ink-900 selection:bg-teal-500/20 dark:bg-[#090D16] dark:text-slate-100">
      <TopNav variant="public" />
      <section className="py-14 sm:py-20">
        <div className="container-page mx-auto max-w-4xl space-y-6">
          <Card>
            <h2 className="text-xl font-bold">1. Procurement Input</h2>
            <p className="mt-2 text-ink-600">Upload tender documents, NITs, RFPs, BOQs.</p>
          </Card>
          <Card>
            <h2 className="text-xl font-bold">2. Requirement Understanding</h2>
            <p className="mt-2 text-ink-600">Extract scope, operating parameters, and technical thresholds.</p>
          </Card>
        </div>
      </section>
      <Footer />
    </div>
  );
}
