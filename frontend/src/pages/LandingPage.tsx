import { useState } from 'react';
import { motion, type Variants } from 'motion/react';
import {
  ArrowRight,
  CheckCircle2,
  FileCheck2,
  FileSearch,
  FileText,
  GitBranch,
  Layers,
  Search,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import { TopNav } from '@/components/TopNav';
import { Footer } from '@/components/Footer';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { useRouter } from '@/router';

const heroContainerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.04,
    },
  },
};

const heroItemVariants: Variants = {
  hidden: { opacity: 0, y: 10 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: [0.16, 1, 0.3, 1],
    },
  },
};

export function LandingPage() {
  const { navigate } = useRouter();
  const [heroActiveTab, setHeroActiveTab] = useState<'standards' | 'issues' | 'profile' | 'evidence'>('standards');

  return (
    <div className="min-h-screen bg-ivory-50 text-ink-900 selection:bg-teal-500/20 dark:bg-[#090D16] dark:text-slate-100">
      <TopNav variant="public" />

      <section className="relative overflow-hidden border-b border-ink-200 bg-ivory-50/60">
        <div className="absolute inset-0 grid-bg opacity-35 pointer-events-none" />
        <div className="absolute inset-0 gradient-mesh pointer-events-none" />

        <div className="container-page relative pt-16 pb-20 sm:pt-20 sm:pb-28">
          <motion.div
            variants={heroContainerVariants}
            initial="hidden"
            animate="visible"
            className="mx-auto max-w-4xl text-center"
          >
            <motion.div variants={heroItemVariants} className="mb-6 inline-flex items-center gap-2 rounded-full border border-ink-200/90 bg-white/90 px-3.5 py-1 text-xs font-medium text-ink-700 shadow-soft backdrop-blur-sm">
              <span className="flex h-2 w-2 rounded-full bg-teal-500" />
              <span className="font-semibold text-ink-900">StandIQ</span>
              <span className="text-ink-300">|</span>
              <span>Procurement Intelligence Workspace</span>
            </motion.div>

            <motion.h1
              variants={heroItemVariants}
              className="text-balance text-4xl font-semibold tracking-tight text-ink-900 sm:text-5xl md:text-[3.4rem] md:leading-[1.14]"
            >
              From procurement requirements to{' '}
              <span className="font-serif italic font-normal text-teal-800">
                defensible standards intelligence
              </span>
              .
            </motion.h1>

            <motion.p
              variants={heroItemVariants}
              className="mx-auto mt-6 max-w-2xl text-balance text-base leading-relaxed text-ink-600 sm:text-lg"
            >
              Analyze tenders and technical specifications to identify applicable standards, related references,
              current versions, regulatory requirements, specification gaps and evidence.
            </motion.p>

            <motion.div
              variants={heroItemVariants}
              className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row"
            >
              <Button
                size="lg"
                onClick={() => navigate({ name: 'new-analysis' })}
                rightIcon={<ArrowRight size={17} />}
                className="shadow-card active:scale-[0.98] transition-transform"
              >
                Analyze a tender
              </Button>
              <Button
                size="lg"
                variant="secondary"
                onClick={() => navigate({ name: 'how-it-works' })}
                className="active:scale-[0.98] transition-transform"
              >
                See how it works
              </Button>
            </motion.div>

            <motion.p variants={heroItemVariants} className="mt-4 text-xs text-ink-400 font-mono">
              Engineered for Technical Evaluation Committees, Procurement Officers & Specification Authors
            </motion.p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.22, ease: [0.16, 1, 0.3, 1] }}
            className="mt-12 sm:mt-16"
          >
            <div className="mx-auto max-w-5xl rounded-xl border border-ink-200 bg-white shadow-pop overflow-hidden transition-all duration-300 hover:border-ink-300/80">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-ink-200 bg-ivory-100/80 px-4 py-3 sm:px-6">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1.5">
                    <span className="h-2.5 w-2.5 rounded-full bg-error-400/80" />
                    <span className="h-2.5 w-2.5 rounded-full bg-warning-400/80" />
                    <span className="h-2.5 w-2.5 rounded-full bg-success-400/80" />
                  </div>
                  <span className="text-ink-300">|</span>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-semibold text-ink-800">
                      Tender Analysis: NIT #MCD-2024-LT-09
                    </span>
                    <span className="badge-teal text-[11px] font-medium">LED Street Lighting Luminaire</span>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-xs">
                  <span className="flex items-center gap-1.5 text-success-700 font-medium bg-success-50 px-2.5 py-0.5 rounded border border-success-200/60 shadow-soft">
                    <span className="h-1.5 w-1.5 rounded-full bg-success-500" />
                    Analysis Complete
                  </span>
                  <span className="text-ink-400 hidden sm:inline font-mono text-[11px]">
                    ID: an-led-90w · 4.1s
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 divide-x divide-ink-100 border-b border-ink-200 bg-white sm:grid-cols-4">
                <div className="p-3.5 sm:px-5">
                  <p className="text-[11px] font-medium text-ink-400 uppercase tracking-wider">Applicable Standards</p>
                  <div className="mt-1 flex items-baseline gap-1.5">
                    <span className="text-xl font-semibold text-ink-900 tabular-nums">7</span>
                    <span className="text-xs text-teal-700 font-medium">Mapped to IS codes</span>
                  </div>
                </div>
                <div className="p-3.5 sm:px-5">
                  <p className="text-[11px] font-medium text-ink-400 uppercase tracking-wider">Related References</p>
                  <div className="mt-1 flex items-baseline gap-1.5">
                    <span className="text-xl font-semibold text-ink-900 tabular-nums">4</span>
                    <span className="text-xs text-blue-700 font-medium">Normative links</span>
                  </div>
                </div>
                <div className="p-3.5 sm:px-5 border-t sm:border-t-0">
                  <p className="text-[11px] font-medium text-ink-400 uppercase tracking-wider">Issues Detected</p>
                  <div className="mt-1 flex items-baseline gap-1.5">
                    <span className="text-xl font-semibold text-warning-700 tabular-nums">3</span>
                    <span className="text-xs text-ink-500">1 obsolete, 2 gaps</span>
                  </div>
                </div>
                <div className="p-3.5 sm:px-5 border-t sm:border-t-0">
                  <p className="text-[11px] font-medium text-ink-400 uppercase tracking-wider">Evidence Status</p>
                  <div className="mt-1 flex items-baseline gap-1.5">
                    <span className="text-sm font-semibold text-success-700">Verified</span>
                    <span className="text-xs text-success-700 font-medium">Clause-cited</span>
                  </div>
                </div>
              </div>

              <div className="flex border-b border-ink-200 bg-ivory-50/50 px-4 sm:px-6 gap-1 pt-2">
                {[
                  { id: 'standards', label: 'Applicable Standards (7)' },
                  { id: 'issues', label: 'Issues & Gaps (3)' },
                  { id: 'profile', label: 'Procurement Profile' },
                  { id: 'evidence', label: 'Traceable Evidence' },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setHeroActiveTab(tab.id as any)}
                    className={`relative px-3 py-2 text-xs font-medium transition-colors ${
                      heroActiveTab === tab.id
                        ? 'text-ink-900 font-semibold'
                        : 'text-ink-500 hover:text-ink-800'
                    }`}
                  >
                    {heroActiveTab === tab.id && (
                      <motion.div
                        layoutId="heroTabIndicator"
                        className="absolute bottom-0 left-0 right-0 h-0.5 bg-ink-900"
                        transition={{ type: 'spring', bounce: 0.15, duration: 0.35 }}
                      />
                    )}
                    <span>{tab.label}</span>
                  </button>
                ))}
              </div>

              <div className="p-4 sm:p-6 bg-white min-h-[290px]">
                <motion.div
                  key={heroActiveTab}
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.25, ease: 'easeOut' }}
                >
                  {heroActiveTab === 'standards' && (
                    <div className="space-y-2.5">
                      <div className="flex items-center justify-between text-xs text-ink-400 px-2 pb-1 border-b border-ink-100 font-mono">
                        <span>Standard & Designation</span>
                        <span>Version & Status</span>
                      </div>

                      {[
                        {
                          code: 'IS 10322 (Part 5/Sec 3):2012',
                          title: 'Luminaires: Particular Requirements - Road and Street Lighting',
                          status: 'Current · Reaffirmed 2022',
                          badge: 'Mandatory',
                          badgeVariant: 'teal' as const,
                          detail: 'Includes Amendment 1 & 2 · Replaces IS 2149:1970',
                        },
                        {
                          code: 'IS 15885 (Part 2/Sec 13):2012',
                          title: 'Lamp Controlgear: AC/DC Supplied Electronic Controlgear for LED Modules',
                          status: 'Current · Compulsory Registration',
                          badge: 'CRS Mandatory',
                          badgeVariant: 'blue' as const,
                          detail: 'Thermal protection, safety isolation & voltage tolerance',
                        },
                        {
                          code: 'IS 16107 (Part 2/Sec 1):2012',
                          title: 'Luminaires Performance: LED Luminaire Performance Requirements',
                          status: 'Current · Reaffirmed 2022',
                          badge: 'Performance',
                          badgeVariant: 'neutral' as const,
                          detail: 'Lumen maintenance, CRI ≥ 70, efficacy ≥ 135 lm/W',
                        },
                      ].map((std, i) => (
                        <div
                          key={i}
                          className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 rounded-lg border border-ink-200/70 p-3 transition-colors hover:bg-ivory-50/80"
                        >
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center gap-2">
                              <span className="font-mono text-xs font-semibold text-ink-900">{std.code}</span>
                              <Badge variant={std.badgeVariant} className="text-[10px] py-0 px-1.5">
                                {std.badge}
                              </Badge>
                            </div>
                            <p className="mt-0.5 text-xs text-ink-600 truncate">{std.title}</p>
                            <p className="text-[11px] text-ink-400">{std.detail}</p>
                          </div>
                          <div className="shrink-0 text-left sm:text-right">
                            <span className="inline-block rounded bg-ink-100/70 px-2 py-0.5 text-[11px] font-medium text-ink-700">
                              {std.status}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {heroActiveTab === 'issues' && (
                    <div className="space-y-3">
                      <div className="rounded-lg border border-error-200 bg-error-50/50 p-3.5">
                        <div className="flex items-start gap-3">
                          <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-error-100 text-error-700">
                            <ShieldAlert size={13} />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center justify-between gap-2">
                              <h2 className="text-xs font-semibold text-error-900">
                                Obsolete Standard Reference Detected
                              </h2>
                              <Badge variant="error" className="text-[10px]">High Severity</Badge>
                            </div>
                            <p className="mt-1 text-xs text-ink-700 leading-relaxed">
                              <strong>Tender Section 4.2</strong> cites withdrawn standard <code className="rounded bg-error-100 px-1 font-mono text-[11px] text-error-900">IS 1944:1981</code>.
                            </p>
                            <p className="mt-1.5 text-xs text-ink-500">
                              <strong>Defensible Recommendation:</strong> Update clause to cite current <code className="font-mono text-[11px]">IS 10322 (Part 5/Sec 3):2012</code> read with the National Lighting Code (SP 72:2010).
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  {heroActiveTab === 'profile' && (
                    <div className="grid gap-4 sm:grid-cols-2">
                      <div className="rounded-lg border border-ink-200 p-4 bg-ivory-50/40">
                        <p className="text-xs font-semibold uppercase tracking-wider text-ink-400 mb-3">Procurement Entity & Context</p>
                        <dl className="space-y-2 text-xs">
                          <div className="flex justify-between border-b border-ink-100 pb-1.5">
                            <dt className="text-ink-500">Product</dt>
                            <dd className="font-medium text-ink-900 text-right">Commercial LED Street Lighting Luminaire</dd>
                          </div>
                        </dl>
                      </div>
                    </div>
                  )}
                  {heroActiveTab === 'evidence' && (
                    <div className="space-y-3">
                      <div className="rounded-lg border border-ink-200 bg-white p-4">
                        <div className="flex items-center justify-between border-b border-ink-100 pb-2 mb-2">
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-xs font-semibold text-teal-700">NIT Clause 3.2.1 Citation</span>
                            <Badge variant="teal" className="text-[10px]">Verified 96% Match</Badge>
                          </div>
                        </div>
                        <blockquote className="border-l-2 border-teal-500 pl-3 text-xs italic text-ink-700 bg-ivory-50/70 py-1.5 rounded-r">
                          "The luminaire shall use high-power SMD LEDs with an integrated electronic driver operating at nominal 230V AC. Driver must offer thermal auto-cutoff and voltage cutoff."
                        </blockquote>
                      </div>
                    </div>
                  )}
                </motion.div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
