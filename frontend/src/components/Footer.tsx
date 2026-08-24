import { Logo } from './Logo';
import { useRouter, type Route } from '@/router';

export function Footer() {
  const { navigate } = useRouter();

  const productLinks: { label: string; route?: Route }[] = [
    { label: 'Workspace', route: { name: 'workspace' } },
    { label: 'Standards', route: { name: 'standards' } },
    { label: 'Reports', route: { name: 'reports' } },
  ];

  const resourceLinks: { label: string; route?: Route; href?: string }[] = [
    { label: 'How It Works', route: { name: 'how-it-works' } },
    { label: 'Problem Statement 26108', href: 'https://smartindiahackathon.gov.in' },
  ];

  const legalLinks = [
    { label: 'Privacy', href: '#' },
    { label: 'Terms', href: '#' },
  ];

  return (
    <footer className="border-t border-ink-200 bg-ivory-100/70 text-ink-600 dark:border-slate-800 dark:bg-[#090D16] dark:text-slate-400">
      <div className="container-page py-12 lg:py-16">
        <div className="grid gap-10 lg:grid-cols-12">
          {/* Brand Column */}
          <div className="lg:col-span-6">
            <button
              onClick={() => navigate({ name: 'landing' })}
              className="text-left transition-opacity hover:opacity-85"
            >
              <Logo size="md" />
            </button>
            <p className="mt-3 text-xs leading-relaxed text-ink-500 max-w-sm dark:text-slate-400">
              StandIQ is a unified procurement intelligence workspace. We help technical evaluation committees
              and procurement officers analyze tender specifications, discover applicable Indian Standards,
              detect version gaps, and verify evidence.
            </p>
            <div className="mt-5 inline-flex items-center gap-2 rounded-md border border-ink-200/80 bg-white px-2.5 py-1 text-[11px] font-mono text-ink-600 dark:border-slate-800 dark:bg-[#111827] dark:text-slate-300">
              <span className="h-1.5 w-1.5 rounded-full bg-teal-500" />
              <span>Requirement → Standard → Evidence → Audit</span>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="grid grid-cols-3 gap-6 lg:col-span-6">
            <div>
              <p className="mb-3 text-[11px] font-semibold uppercase tracking-wider text-ink-400 font-mono">Product</p>
              <ul className="space-y-2">
                {productLinks.map((item) => (
                  <li key={item.label}>
                    <button
                      onClick={() => item.route && navigate(item.route)}
                      className="text-xs text-ink-600 transition-colors hover:text-ink-900 text-left dark:text-slate-400 dark:hover:text-white"
                    >
                      {item.label}
                    </button>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <p className="mb-3 text-[11px] font-semibold uppercase tracking-wider text-ink-400 font-mono">Resources</p>
              <ul className="space-y-2">
                {resourceLinks.map((item) => (
                  <li key={item.label}>
                    {item.route ? (
                      <button
                        onClick={() => navigate(item.route!)}
                        className="text-xs text-ink-600 transition-colors hover:text-ink-900 text-left dark:text-slate-400 dark:hover:text-white"
                      >
                        {item.label}
                      </button>
                    ) : (
                      <a
                        href={item.href}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-ink-600 transition-colors hover:text-ink-900 dark:text-slate-400 dark:hover:text-white"
                      >
                        {item.label}
                      </a>
                    )}
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <p className="mb-3 text-[11px] font-semibold uppercase tracking-wider text-ink-400 font-mono">Legal</p>
              <ul className="space-y-2">
                {legalLinks.map((item) => (
                  <li key={item.label}>
                    <a
                      href={item.href}
                      onClick={(e) => {
                        e.preventDefault();
                        alert(`${item.label} Policy — StandIQ SIH 26108 Evaluation.`);
                      }}
                      className="text-xs text-ink-600 transition-colors hover:text-ink-900 dark:text-slate-400 dark:hover:text-white"
                    >
                      {item.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-ink-200/80 pt-6 sm:flex-row text-[11px] text-ink-400 dark:border-slate-800 dark:text-slate-500">
          <p>
            © {new Date().getFullYear()} StandIQ. Built for SIH Problem Statement 26108 · Indian Standards references derived from indexed standards catalog.
          </p>
          <div className="flex items-center gap-4">
            <button onClick={() => navigate({ name: 'how-it-works' })} className="hover:text-ink-700 dark:hover:text-slate-300">How It Works</button>
            <span className="text-ink-300 dark:text-slate-700">|</span>
            <button onClick={() => navigate({ name: 'workspace' })} className="hover:text-ink-700 dark:hover:text-slate-300">Workspace</button>
            <span className="text-ink-300 dark:text-slate-700">|</span>
            <button onClick={() => navigate({ name: 'standards' })} className="hover:text-ink-700 dark:hover:text-slate-300">Standards</button>
          </div>
        </div>
      </div>
    </footer>
  );
}

