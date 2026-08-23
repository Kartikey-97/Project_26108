import React, { useState } from 'react';
import { AlertTriangle, Sliders, CheckCircle2, TrendingUp, DollarSign, Users, ShieldCheck, ArrowRight } from 'lucide-react';

export default function RequirementQualityView({ restrictivenessData }) {
  const [isRelaxed, setIsRelaxed] = useState(false);

  if (!restrictivenessData) return null;
  const cf = restrictivenessData.counterfactuals[0];

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Header Banner */}
      <div className="surface-card p-5 border-l-4 border-l-[#A8752B]">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="badge badge-restrictive">Innovation 4</span>
              <h2 className="text-base font-bold text-[#17202A]">Requirement Quality & Restrictiveness Inspector</h2>
            </div>
            <p className="text-xs text-[#667085]">
              Evidence-based detection of proprietary, overly narrow, or single-vendor biased technical clauses with interactive Counterfactual Relaxation Simulation.
            </p>
          </div>
        </div>
      </div>

      {/* Flagged Clause Overview Card */}
      <div className="surface-card p-6 space-y-5">
        
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-[#E5E2D9] pb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-[#FDF7ED] border border-[#F6E2C3] text-[#A8752B]">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xs text-[#A8752B] font-semibold uppercase">Flagged Specification</span>
              <h3 className="text-base font-bold text-[#17202A]">{cf.parameter}</h3>
            </div>
          </div>
          
          <div className="inline-flex items-center gap-2 bg-[#FDF7ED] border border-[#F6E2C3] text-[#A8752B] text-xs px-3.5 py-1.5 rounded font-semibold">
            Single-Vendor Bias Risk Identified
          </div>
        </div>

        {/* Comparison Box */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-[#F7F6F1] border border-[#E5E2D9] space-y-1">
            <span className="text-xs text-[#667085] font-semibold uppercase block">Draft Tender Clause:</span>
            <p className="text-sm font-mono text-[#A8752B] font-semibold">{cf.current_clause}</p>
            <p className="text-xs text-[#667085] mt-2">{cf.why_flagged}</p>
          </div>

          <div className="p-4 rounded-lg bg-[#EDF6F5] border border-[#C0E3DF] space-y-1">
            <span className="text-xs text-[#087F73] font-semibold uppercase block">BIS Standard Alignment Proposal:</span>
            <p className="text-sm font-mono text-[#2E6B5B] font-semibold">{cf.proposed_relaxation}</p>
            <p className="text-xs text-[#667085] mt-2">Fully aligns with IS 16102 (Part 2) 7-step MacAdam ellipse tolerance.</p>
          </div>
        </div>

        {/* Counterfactual Impact Interactive Simulator */}
        <div className="mt-2 p-5 rounded-lg bg-[#F7F6F1] border border-[#E5E2D9] space-y-5">
          
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-[#E5E2D9] pb-4">
            <div className="flex items-center gap-2.5">
              <Sliders className="w-5 h-5 text-[#087F73]" />
              <div>
                <h4 className="text-sm font-bold text-[#17202A]">Interactive Counterfactual Simulator</h4>
                <p className="text-xs text-[#667085]">Toggle clause relaxation to observe predicted impact on vendor competition & cost.</p>
              </div>
            </div>

            {/* Toggle Switch */}
            <div className="flex items-center gap-1 bg-white p-1 rounded border border-[#E5E2D9]">
              <span
                className={`text-xs font-semibold px-3 py-1.5 rounded cursor-pointer transition-all ${
                  !isRelaxed ? 'bg-[#FDF7ED] text-[#A8752B] border border-[#F6E2C3]' : 'text-[#667085] hover:text-[#17202A]'
                }`}
                onClick={() => setIsRelaxed(false)}
              >
                Current Spec (±50K)
              </span>
              <span
                className={`text-xs font-semibold px-3 py-1.5 rounded cursor-pointer transition-all ${
                  isRelaxed ? 'bg-[#EBF4F1] text-[#2E6B5B] border border-[#C4E2DA]' : 'text-[#667085] hover:text-[#17202A]'
                }`}
                onClick={() => setIsRelaxed(true)}
              >
                Relaxed Spec (IS Standard)
              </span>
            </div>
          </div>

          {/* Impact Results Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            
            {/* Metric A: Vendor Competition */}
            <div className={`p-4 rounded-lg border transition-all ${
              isRelaxed ? 'bg-[#EBF4F1] border-[#C4E2DA]' : 'bg-white border-[#E5E2D9]'
            }`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-[#667085] font-semibold">Vendor Pool</span>
                <Users className={`w-4 h-4 ${isRelaxed ? 'text-[#2E6B5B]' : 'text-[#9BA3AF]'}`} />
              </div>
              <div className="text-base font-bold text-[#17202A] leading-tight">
                {isRelaxed ? cf.impact_analysis.vendor_pool_expansion : 'Restricted (2-3 Bidders)'}
              </div>
              <p className="text-xs text-[#667085] mt-1">
                {isRelaxed ? 'Allows Havells, Wipro, Bajaj, Surya, Philips' : 'High risk of single-vendor collusion'}
              </p>
            </div>

            {/* Metric B: Cost Savings */}
            <div className={`p-4 rounded-lg border transition-all ${
              isRelaxed ? 'bg-[#EBF4F1] border-[#C4E2DA]' : 'bg-white border-[#E5E2D9]'
            }`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-[#667085] font-semibold">Cost Impact</span>
                <DollarSign className={`w-4 h-4 ${isRelaxed ? 'text-[#2E6B5B]' : 'text-[#9BA3AF]'}`} />
              </div>
              <div className="text-base font-bold text-[#17202A] leading-tight">
                {isRelaxed ? cf.impact_analysis.cost_saving_estimate : 'Baseline Premium Price'}
              </div>
              <p className="text-xs text-[#667085] mt-1">
                {isRelaxed ? 'Competitive bulk pricing' : 'Custom binning surcharge applies'}
              </p>
            </div>

            {/* Metric C: Standards Compliance */}
            <div className="p-4 rounded-lg bg-white border border-[#E5E2D9]">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-[#667085] font-semibold">Standards Integrity</span>
                <ShieldCheck className="text-[#087F73] w-4 h-4" />
              </div>
              <div className="text-base font-bold text-[#2E6B5B]">100% Compliant</div>
              <p className="text-xs text-[#667085] mt-1">Fully meets IS 10322 (Part 5/Sec 3)</p>
            </div>

            {/* Metric D: QCO Legal Compliance */}
            <div className="p-4 rounded-lg bg-white border border-[#E5E2D9]">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-[#667085] font-semibold">QCO Legal Status</span>
                <CheckCircle2 className="text-[#087F73] w-4 h-4" />
              </div>
              <div className="text-base font-bold text-[#087F73]">Unaffected</div>
              <p className="text-xs text-[#667085] mt-1">Mandatory BIS CRS Registration preserved</p>
            </div>

          </div>

        </div>

      </div>
    </div>
  );
}
