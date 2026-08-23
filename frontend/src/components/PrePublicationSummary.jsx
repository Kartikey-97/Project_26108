import React from 'react';
import { ShieldCheck, CheckCircle2, AlertCircle, Printer } from 'lucide-react';

export default function PrePublicationSummary({ summaryData }) {
  if (!summaryData) return null;
  const { scorecard, missing_recommendations, defensibility_statement } = summaryData;

  const handleExport = () => {
    window.print();
  };

  return (
    <div className="space-y-6 animate-fade-in print:p-0">
      
      {/* Header Banner */}
      <div className="surface-card p-5 border-l-4 border-l-[#087F73] flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="badge badge-qco">Innovation 2</span>
            <h2 className="text-base font-bold text-[#17202A]">Pre-Publication Buyer-Side Intelligence</h2>
          </div>
          <p className="text-xs text-[#667085]">
            Audit-ready procurement defense dossier enabling procurement officers to validate technical requirements before releasing public tenders.
          </p>
        </div>

        <button
          type="button"
          onClick={handleExport}
          className="btn-accent print:hidden cursor-pointer text-xs py-2 px-3 shrink-0"
        >
          <Printer className="w-4 h-4" />
          Export Compliance Dossier
        </button>
      </div>

      {/* Scorecard Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="surface-card p-5 text-center">
          <span className="text-xs text-[#667085] font-semibold uppercase block mb-1">Completeness</span>
          <span className="text-3xl font-bold text-[#087F73]">{scorecard.completeness_score}%</span>
          <div className="w-full bg-[#E5E2D9] h-1.5 rounded-full mt-3 overflow-hidden">
            <div className="bg-[#087F73] h-full rounded-full" style={{ width: `${scorecard.completeness_score}%` }}></div>
          </div>
        </div>

        <div className="surface-card p-5 text-center">
          <span className="text-xs text-[#667085] font-semibold uppercase block mb-1">Legal Defensibility</span>
          <span className="text-3xl font-bold text-[#2E6B5B]">{scorecard.defensibility_score}%</span>
          <div className="w-full bg-[#E5E2D9] h-1.5 rounded-full mt-3 overflow-hidden">
            <div className="bg-[#2E6B5B] h-full rounded-full" style={{ width: `${scorecard.defensibility_score}%` }}></div>
          </div>
        </div>

        <div className="surface-card p-5 text-center">
          <span className="text-xs text-[#667085] font-semibold uppercase block mb-1">QCO Compliance</span>
          <span className="text-3xl font-bold text-[#087F73]">{scorecard.regulatory_compliance_score}%</span>
          <div className="w-full bg-[#E5E2D9] h-1.5 rounded-full mt-3 overflow-hidden">
            <div className="bg-[#087F73] h-full rounded-full" style={{ width: `${scorecard.regulatory_compliance_score}%` }}></div>
          </div>
        </div>

        <div className="surface-card p-5 text-center">
          <span className="text-xs text-[#667085] font-semibold uppercase block mb-1">Vendor Neutrality</span>
          <span className="text-3xl font-bold text-[#A8752B]">{scorecard.vendor_neutrality_score}%</span>
          <div className="w-full bg-[#E5E2D9] h-1.5 rounded-full mt-3 overflow-hidden">
            <div className="bg-[#A8752B] h-full rounded-full" style={{ width: `${scorecard.vendor_neutrality_score}%` }}></div>
          </div>
        </div>

      </div>

      {/* Missing Citation Recommendations */}
      <div className="surface-card p-6 space-y-4">
        <h3 className="text-sm font-bold text-[#17202A] flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-[#A8752B]" />
          Recommended Technical Standard Additions ({missing_recommendations.length})
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {missing_recommendations.map((rec, idx) => (
            <div key={idx} className="p-4 rounded-lg bg-[#F7F6F1] border border-[#E5E2D9] space-y-1">
              <h4 className="text-xs font-bold text-[#087F73] flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#087F73]" />
                {rec.title}
              </h4>
              <p className="text-xs text-[#667085]">{rec.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Defensibility Statement for Procurement Audit */}
      <div className="surface-card p-6 border-l-4 border-l-[#2E6B5B] space-y-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-[#2E6B5B]" />
          <h3 className="text-sm font-bold text-[#17202A]">Pre-Publication Audit Defensibility Statement</h3>
        </div>
        
        <div className="p-4 rounded-lg bg-[#EDF6F5] border border-[#C0E3DF] text-xs text-[#2E6B5B] font-mono leading-relaxed">
          "{defensibility_statement}"
        </div>
        <p className="text-[11px] text-[#667085]">
          This statement can be appended to the official tender committee approval note.
        </p>
      </div>

    </div>
  );
}
