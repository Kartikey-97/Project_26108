import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldCheck,
  ArrowRight,
  CheckCircle2,
  FileText,
  BookOpen,
  Zap,
  BarChart3,
  Menu,
  X,
  ExternalLink,
  ShieldAlert,
  Search,
  Sparkles,
  Layers,
  Award,
  Moon,
  Sun
} from 'lucide-react';
import { useTheme } from '../utils/ThemeContext';

export default function LandingPage() {
  const navigate = useNavigate();
  const { isDark, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
    setMobileMenuOpen(false);
  };

  const howSteps = [
    {
      step: '01',
      title: 'Submit Specification',
      desc: 'Paste tender technical clauses or upload specification documents (PDF, DOCX, TXT) directly.',
      icon: FileText
    },
    {
      step: '02',
      title: 'AI Parameter Extraction',
      desc: 'The engine parses electrical ratings, mechanical tolerances, environmental ratings, and testing clauses.',
      icon: Zap
    },
    {
      step: '03',
      title: 'BIS & QCO Mapping',
      desc: 'Matches parameters against 384+ Indian Standards and flags mandatory DPIIT Quality Control Orders.',
      icon: BookOpen
    },
    {
      step: '04',
      title: 'Defensible Audit Dossier',
      desc: 'Generates evidence-backed recommendations, completeness scores, and clause-level compliance proof.',
      icon: Award
    }
  ];

  const features = [
    {
      title: 'Automated Standard Identification',
      desc: 'Instantly identifies primary governing Indian Standards (IS) and allied normative references for tender products.',
      badge: 'BIS Act 2016',
      icon: BookOpen
    },
    {
      title: 'DPIIT QCO Mandate Compliance',
      desc: 'Audits mandatory Quality Control Orders (QCO) to prevent illegal procurement of non-BIS certified goods.',
      badge: 'Legal Shield',
      icon: ShieldAlert
    },
    {
      title: 'Proprietary Bias & Vendor Lock-in Detection',
      desc: 'Highlights overly narrow or restrictive clauses and recommends relaxation based on official BIS tolerance ranges.',
      badge: 'Fair Competition',
      icon: ShieldCheck
    },
    {
      title: 'Tender Completeness Scorecard',
      desc: 'Evaluates if critical safety, testing, warranty, and environmental parameters are missing from tender drafts.',
      badge: 'Pre-Bid Audit',
      icon: BarChart3
    },
    {
      title: 'Clause-by-Clause Evidence Trail',
      desc: 'Provides exact clause numbers, tables, and verbatim quotes from official BIS catalog records.',
      badge: 'Auditable Proof',
      icon: Layers
    },
    {
      title: 'Side-by-Side Standard Comparison',
      desc: 'Compare superseded vs current standards or evaluate international equivalent adoptions (e.g., IEC, ISO).',
      badge: 'Multi-Standard',
      icon: Search
    }
  ];

  return (
    <div
      className="min-h-screen font-sans selection:bg-[#087F73]/20 transition-colors duration-150"
      style={{
        backgroundColor: 'var(--bg-primary)',
        color: 'var(--text-main)'
      }}
    >
      
      {/* ─── Top Navbar (Matching StandIQ reference header) ─── */}
      <header
        className="sticky top-0 z-50 backdrop-blur-md border-b px-6 lg:px-16 h-16 flex items-center justify-between transition-colors duration-150"
        style={{
          backgroundColor: 'var(--header-bg)',
          borderColor: 'var(--border-subtle)'
        }}
      >
        
        {/* Left: Brand Logo & Links */}
        <div className="flex items-center gap-8">
          <div 
            onClick={() => navigate('/')}
            className="flex items-center gap-2.5 cursor-pointer"
          >
            {/* Black shield logo box from screenshot */}
            <div
              className="w-8 h-8 rounded-lg text-white flex items-center justify-center shadow-xs"
              style={{
                backgroundColor: isDark ? 'var(--brand-primary)' : '#11151C'
              }}
            >
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <span
              className="text-base font-bold tracking-tight"
              style={{ color: 'var(--text-main)' }}
            >
              StandIQ
            </span>
          </div>

          <nav className="hidden md:flex items-center gap-6 text-xs font-semibold">
            <button 
              onClick={() => scrollTo('how-it-works')}
              className="hover:opacity-80 transition-opacity cursor-pointer"
              style={{ color: 'var(--text-secondary)' }}
            >
              How It Works
            </button>
            <button 
              onClick={() => scrollTo('features')}
              className="hover:opacity-80 transition-opacity cursor-pointer"
              style={{ color: 'var(--text-secondary)' }}
            >
              Capabilities
            </button>
            <button 
              onClick={() => scrollTo('standards-catalog')}
              className="hover:opacity-80 transition-opacity cursor-pointer"
              style={{ color: 'var(--text-secondary)' }}
            >
              Standards Catalog
            </button>
          </nav>
        </div>

        {/* Right: Theme Toggle & Sign In & Launch App CTA */}
        <div className="flex items-center gap-3 sm:gap-4">
          <button
            type="button"
            onClick={toggleTheme}
            className="p-2 rounded-lg transition-colors cursor-pointer flex items-center justify-center"
            style={{ color: 'var(--text-secondary)' }}
            title={isDark ? "Switch to light mode" : "Switch to dark mode"}
            aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
          >
            {isDark ? (
              <Sun className="w-4 h-4 text-amber-400 hover:text-amber-300 transition-colors" />
            ) : (
              <Moon className="w-4 h-4 text-[#667085] hover:text-[#17202A] transition-colors" />
            )}
          </button>

          <button
            onClick={() => navigate('/app')}
            className="text-xs font-semibold hover:opacity-80 transition-opacity hidden sm:block cursor-pointer"
            style={{ color: 'var(--text-secondary)' }}
          >
            Sign In
          </button>

          <button
            onClick={() => navigate('/app')}
            className="btn-primary text-xs font-semibold px-4 py-2 rounded-lg transition-colors cursor-pointer shadow-sm flex items-center gap-1.5"
          >
            <span>Launch App</span>
          </button>

          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-1.5 cursor-pointer"
            style={{ color: 'var(--text-secondary)' }}
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

      </header>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div
          className="md:hidden border-b px-6 py-4 space-y-3 animate-fade-in text-xs font-semibold shadow-md"
          style={{
            backgroundColor: 'var(--bg-surface)',
            borderColor: 'var(--border-subtle)',
            color: 'var(--text-secondary)'
          }}
        >
          <button onClick={() => scrollTo('how-it-works')} className="block w-full text-left py-1 hover:opacity-80">How It Works</button>
          <button onClick={() => scrollTo('features')} className="block w-full text-left py-1 hover:opacity-80">Capabilities</button>
          <button onClick={() => scrollTo('standards-catalog')} className="block w-full text-left py-1 hover:opacity-80">Standards Catalog</button>
          <button
            onClick={() => {
              toggleTheme();
              setMobileMenuOpen(false);
            }}
            className="w-full flex items-center justify-between py-1.5 cursor-pointer border-t"
            style={{ borderColor: 'var(--border-subtle)' }}
          >
            <span>Theme</span>
            <span className="text-[10px] font-mono uppercase">{isDark ? 'Dark Mode' : 'Light Mode'}</span>
          </button>
          <div className="pt-2 border-t" style={{ borderColor: 'var(--border-subtle)' }}>
            <button onClick={() => navigate('/app')} className="w-full btn-primary py-2.5 rounded-lg text-center font-bold justify-center">Launch App</button>
          </div>
        </div>
      )}

      {/* ─── Hero Section (Exact Pixel-Precision Match to StandIQ Screenshot) ─── */}
      <section
        className="bg-grid-subtle relative pt-20 pb-24 md:pt-28 md:pb-32 px-6 lg:px-16 text-center border-b overflow-hidden transition-colors duration-150"
        style={{ borderColor: 'var(--border-subtle)' }}
      >
        
        <div className="max-w-4xl mx-auto space-y-8 relative z-10">
          
          {/* Eyebrow Pill Badge */}
          <div
            className="inline-flex items-center gap-1.5 text-[11px] font-bold px-3.5 py-1 rounded-full shadow-xs animate-fade-in border"
            style={{
              backgroundColor: 'var(--brand-tint)',
              borderColor: 'var(--brand-tint-border)',
              color: 'var(--brand-primary)'
            }}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Procurement Intelligence Platform</span>
          </div>

          {/* Main Hero Headline */}
          <h1
            className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight leading-[1.12]"
            style={{ color: 'var(--text-main)' }}
          >
            Identify every applicable <br className="hidden sm:inline" />
            <span
              className="font-serif-italic font-normal inline-block px-1"
              style={{ color: 'var(--brand-primary)' }}
            >
              Indian Standard
            </span>{' '}
            in your <br className="hidden sm:inline" />
            procurement documents
          </h1>

          {/* Subtitle Description */}
          <p
            className="text-xs sm:text-sm md:text-base max-w-2xl mx-auto leading-relaxed font-normal"
            style={{ color: 'var(--text-secondary)' }}
          >
            StandIQ analyzes tender documents and technical specifications to surface applicable standards, detect specification gaps, and map certification requirements — before your bid goes out.
          </p>

          {/* Dual Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3.5 pt-2">
            <button
              type="button"
              onClick={() => navigate('/analyze')}
              className="w-full sm:w-auto btn-primary text-xs sm:text-sm font-semibold px-6 py-3 rounded-lg shadow-sm flex items-center justify-center gap-2 cursor-pointer transition-all hover:scale-[1.01]"
            >
              <span>Start an Analysis</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              type="button"
              onClick={() => scrollTo('how-it-works')}
              className="w-full sm:w-auto btn-secondary text-xs sm:text-sm font-semibold px-6 py-3 rounded-lg cursor-pointer transition-colors"
            >
              <span>See How It Works</span>
            </button>
          </div>

          {/* Trust Caption */}
          <p className="text-[11px] font-medium pt-1" style={{ color: 'var(--text-muted)' }}>
            No credit card required · Government &amp; enterprise ready
          </p>

        </div>

      </section>

      {/* ─── Interactive Live Preview Card ─── */}
      <section className="px-6 lg:px-16 -mt-10 relative z-20 max-w-5xl mx-auto">
        <div className="surface-card rounded-xl p-6 shadow-lg space-y-5">
          
          <div
            className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b gap-2"
            style={{ borderColor: 'var(--border-subtle)' }}
          >
            <div className="flex items-center gap-2.5">
              <span
                className="w-3 h-3 rounded-full animate-pulse"
                style={{ backgroundColor: 'var(--brand-primary)' }}
              />
              <h3 className="text-xs font-bold uppercase tracking-wider" style={{ color: 'var(--text-main)' }}>
                Live System Demonstration · Tender Spec Audit
              </h3>
            </div>
            <span
              className="text-[11px] font-mono px-2.5 py-0.5 rounded border"
              style={{
                backgroundColor: 'var(--brand-tint)',
                borderColor: 'var(--brand-tint-border)',
                color: 'var(--brand-primary)'
              }}
            >
              BIS Act 2016 &amp; DPIIT QCO Compliant
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            
            {/* Box 1 */}
            <div
              className="p-4 rounded-lg border space-y-2"
              style={{
                backgroundColor: 'var(--bg-surface-secondary)',
                borderColor: 'var(--border-subtle)'
              }}
            >
              <span className="text-[10px] font-bold uppercase" style={{ color: 'var(--text-secondary)' }}>Input Specification</span>
              <p className="font-mono font-semibold text-[11px] line-clamp-2" style={{ color: 'var(--text-main)' }}>
                "120W LED Street Luminaire, IP66, 10kV SPD, CCT 5700K..."
              </p>
              <div className="text-[10px] flex items-center gap-1 font-semibold" style={{ color: 'var(--status-success-text)' }}>
                <CheckCircle2 className="w-3 h-3" /> 7 Parameters Extracted
              </div>
            </div>

            {/* Box 2 */}
            <div
              className="p-4 rounded-lg border space-y-2"
              style={{
                backgroundColor: 'var(--brand-tint)',
                borderColor: 'var(--brand-tint-border)'
              }}
            >
              <span className="text-[10px] font-bold uppercase" style={{ color: 'var(--brand-primary)' }}>Primary Identified Standard</span>
              <p className="font-mono font-bold text-xs" style={{ color: 'var(--text-main)' }}>
                IS 10322 (Part 5/Sec 3): 2012
              </p>
              <div className="text-[10px] flex items-center gap-1 font-semibold" style={{ color: 'var(--brand-primary)' }}>
                <ShieldAlert className="w-3 h-3" /> QCO Mandatory Registration
              </div>
            </div>

            {/* Box 3 */}
            <div
              className="p-4 rounded-lg border space-y-2"
              style={{
                backgroundColor: 'var(--bg-surface-secondary)',
                borderColor: 'var(--border-subtle)'
              }}
            >
              <span className="text-[10px] font-bold uppercase" style={{ color: 'var(--text-secondary)' }}>Tender Health &amp; Defensibility</span>
              <div className="flex items-baseline gap-2">
                <span className="text-xl font-extrabold" style={{ color: 'var(--status-success-text)' }}>94%</span>
                <span className="text-[11px]" style={{ color: 'var(--text-secondary)' }}>Audit Score</span>
              </div>
              <p className="text-[10px] font-medium" style={{ color: 'var(--status-warning-text)' }}>
                1 Restrictive CCT clause flagged
              </p>
            </div>

          </div>

          <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
            <span style={{ color: 'var(--text-secondary)' }}>
              Ready to audit your tender document or specification clauses?
            </span>
            <button
              onClick={() => navigate('/analyze')}
              className="font-bold flex items-center gap-1 cursor-pointer hover:opacity-80 transition-opacity"
              style={{ color: 'var(--brand-primary)' }}
            >
              <span>Open Specification Workspace</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

        </div>
      </section>

      {/* ─── How It Works Section ─── */}
      <section id="how-it-works" className="py-24 px-6 lg:px-16 max-w-6xl mx-auto">
        
        <div className="text-center space-y-3 mb-14">
          <span
            className="text-[11px] font-bold uppercase tracking-wider px-3 py-1 rounded-full border"
            style={{
              backgroundColor: 'var(--brand-tint)',
              borderColor: 'var(--brand-tint-border)',
              color: 'var(--brand-primary)'
            }}
          >
            Methodology &amp; Workflow
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight" style={{ color: 'var(--text-main)' }}>
            How StandIQ Identifies Standards in Seconds
          </h2>
          <p className="text-xs sm:text-sm max-w-xl mx-auto" style={{ color: 'var(--text-secondary)' }}>
            From raw procurement draft to an audit-ready compliance dossier in four automated steps.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {howSteps.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div
                key={idx}
                className="surface-card p-6 rounded-xl flex flex-col justify-between space-y-4 hover:border-[var(--brand-primary)] transition-colors"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div
                      className="p-2.5 rounded-lg border"
                      style={{
                        backgroundColor: 'var(--brand-tint)',
                        borderColor: 'var(--brand-tint-border)',
                        color: 'var(--brand-primary)'
                      }}
                    >
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="text-xs font-mono font-bold" style={{ color: 'var(--text-muted)' }}>{item.step}</span>
                  </div>
                  <h3 className="text-sm font-bold" style={{ color: 'var(--text-main)' }}>{item.title}</h3>
                  <p className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{item.desc}</p>
                </div>
              </div>
            );
          })}
        </div>

      </section>

      {/* ─── Key Platform Capabilities (Features Grid) ─── */}
      <section
        id="features"
        className="py-20 px-6 lg:px-16 border-y transition-colors duration-150"
        style={{
          backgroundColor: 'var(--bg-surface-secondary)',
          borderColor: 'var(--border-subtle)'
        }}
      >
        
        <div className="max-w-6xl mx-auto space-y-12">
          
          <div className="text-center space-y-3">
            <span
              className="text-[11px] font-bold uppercase tracking-wider px-3 py-1 rounded-full border"
              style={{
                backgroundColor: 'var(--bg-surface)',
                borderColor: 'var(--border-subtle)',
                color: 'var(--brand-primary)'
              }}
            >
              Enterprise &amp; PSU Capabilities
            </span>
            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight" style={{ color: 'var(--text-main)' }}>
              Engineered for Indian Public Procurement Integrity
            </h2>
            <p className="text-xs sm:text-sm max-w-xl mx-auto" style={{ color: 'var(--text-secondary)' }}>
              Eliminate technical ambiguity, audit risk, and single-vendor lock-in before issuing tenders.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feat, idx) => {
              const Icon = feat.icon;
              return (
                <div
                  key={idx}
                  className="surface-card p-6 rounded-xl space-y-3 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center justify-between">
                    <div
                      className="p-2.5 rounded-lg border"
                      style={{
                        backgroundColor: 'var(--brand-tint)',
                        borderColor: 'var(--brand-tint-border)',
                        color: 'var(--brand-primary)'
                      }}
                    >
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="badge badge-current text-[10px]">{feat.badge}</span>
                  </div>

                  <h3 className="text-sm font-bold" style={{ color: 'var(--text-main)' }}>{feat.title}</h3>
                  <p className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{feat.desc}</p>
                </div>
              );
            })}
          </div>

        </div>

      </section>

      {/* ─── Standards Catalog Fast Navigation ─── */}
      <section id="standards-catalog" className="py-20 px-6 lg:px-16 max-w-6xl mx-auto">
        
        <div className="surface-card p-8 rounded-xl flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-2 max-w-xl">
            <span className="badge badge-qco text-[10px]">Indexed Repository</span>
            <h3 className="text-xl font-bold" style={{ color: 'var(--text-main)' }}>
              Search 384+ Governing Indian Standards
            </h3>
            <p className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
              Explore active specifications for Electrical, Electronics, Solar Energy, Smart Lighting, Infrastructure, and Mechanical products.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 shrink-0">
            <button
              onClick={() => navigate('/standards')}
              className="btn-primary text-xs py-2.5 px-4 flex items-center gap-2 cursor-pointer"
            >
              <Search className="w-4 h-4" />
              <span>Open Standards Explorer</span>
            </button>

            <button
              onClick={() => navigate('/compare')}
              className="btn-secondary text-xs py-2.5 px-4 flex items-center gap-2 cursor-pointer"
            >
              <span>Compare Standards</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

      </section>

      {/* ─── Bottom CTA Banner ─── */}
      <section
        className="py-16 px-6 lg:px-16 border-t text-center transition-colors duration-150"
        style={{
          backgroundColor: 'var(--bg-surface)',
          borderColor: 'var(--border-subtle)'
        }}
      >
        <div className="max-w-2xl mx-auto space-y-5">
          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight" style={{ color: 'var(--text-main)' }}>
            Ready to audit your procurement specifications?
          </h2>
          <p className="text-xs sm:text-sm" style={{ color: 'var(--text-secondary)' }}>
            Paste your tender clauses or load a pre-configured Smart LED street lighting tender preset.
          </p>
          <div className="pt-2">
            <button
              onClick={() => navigate('/analyze')}
              className="btn-accent text-sm py-3 px-6 inline-flex items-center gap-2 cursor-pointer shadow-sm hover:scale-[1.01] transition-all"
            >
              <span>Launch Specification Analysis</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </section>

      {/* ─── Footer ─── */}
      <footer
        className="py-8 px-6 lg:px-16 border-t text-xs flex flex-col sm:flex-row items-center justify-between gap-4 transition-colors duration-150"
        style={{
          backgroundColor: 'var(--header-bg)',
          borderColor: 'var(--border-subtle)',
          color: 'var(--text-secondary)'
        }}
      >
        <div className="flex items-center gap-2">
          <div
            className="w-5 h-5 rounded text-white flex items-center justify-center"
            style={{ backgroundColor: isDark ? 'var(--brand-primary)' : '#11151C' }}
          >
            <ShieldCheck className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="font-bold" style={{ color: 'var(--text-main)' }}>StandIQ / ProcureIntel AI</span>
          <span>· Smart India Hackathon (SIH 2026)</span>
        </div>

        <p className="text-[11px]" style={{ color: 'var(--text-muted)' }}>
          Bureau of Indian Standards (BIS Act 2016) &amp; DPIIT Quality Control Orders Reference System
        </p>
      </footer>

    </div>
  );
}
