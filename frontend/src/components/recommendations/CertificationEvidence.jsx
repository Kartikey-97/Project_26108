import React from 'react';
import { Shield, Link2, CheckSquare } from 'lucide-react';

const STEPS = [
  { id: 1, title: 'BIS ISI Mark Certification', std: 'IS 2:2022', desc: 'Products must bear BIS ISI mark. License No. format: CM/L-XXXXXXX. Applicable for: LED Luminaires, Control Gear.', status: 'MANDATORY', color: 'bg-red-500' },
  { id: 2, title: 'BIS CRS (Compulsory Registration Scheme)', std: 'Electronic equipment compulsory registration', desc: 'CRS portal registration required before import/sale. Portal: crsbis.in', status: 'MANDATORY', color: 'bg-red-500' },
  { id: 3, title: 'QCO Compliance Declaration', std: 'DPIIT Quality Control Order', desc: 'Self-declaration of conformity + NABL lab test report required with bid submission.', status: 'MANDATORY', color: 'bg-red-500' },
  { id: 4, title: 'NABL Accredited Lab Testing', std: 'IS 17 / IS 1248', desc: 'All performance tests must be conducted at NABL-accredited labs. Lab list: nabl.gov.in', status: 'REQUIRED FOR BID', color: 'bg-orange-500' },
  { id: 5, title: 'BEE Star Label', std: 'Energy Conservation Act 2001', desc: 'Minimum 3-Star BEE rating mandatory for LED street lights above 50W per circular dated March 2024.', status: 'RECOMMENDED', color: 'bg-blue-500' },
];

export default function CertificationEvidence({ standards = [], analysisId = '' }) {
  const primaryStd = standards[0]?.code || 'IS 10322 (Part 5/Sec 3)';
  const primaryTitle = standards[0]?.title || 'Luminaires for Road and Street Lighting';

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Left Column */}
      <div className="flex flex-col gap-4">
        <div className="flex items-center gap-2 mb-2">
          <Shield className="text-brand-primary" size={24} />
          <h2 className="text-xl font-bold text-main">Mandatory Certification Pathway</h2>
        </div>

        <div className="flex flex-col gap-4 relative">
          <div className="absolute left-[15px] top-4 bottom-4 w-0.5 bg-border-subtle z-0"></div>
          
          {STEPS.map((step) => (
            <div key={step.id} className="relative z-10 flex gap-4">
              <div className="mt-1 flex-shrink-0 w-8 h-8 rounded-full bg-surface border-2 border-brand-primary flex items-center justify-center text-brand-primary font-bold text-sm">
                {step.id}
              </div>
              <div className="surface-card p-4 rounded-lg border border-subtle flex-1 flex flex-col gap-2 border-l-4" style={{ borderLeftColor: 'var(--brand-primary)' }}>
                <div className="flex justify-between items-start gap-2">
                  <h3 className="font-bold text-main">{step.title}</h3>
                  <span className={`text-[10px] font-bold px-2 py-1 rounded text-white ${step.color}`}>
                    {step.status}
                  </span>
                </div>
                <div className="text-xs font-medium text-secondary">{step.std}</div>
                <p className="text-sm text-secondary">{step.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right Column */}
      <div className="flex flex-col gap-4">
        <div className="flex items-center gap-2 mb-2">
          <Link2 className="text-brand-primary" size={24} />
          <h2 className="text-xl font-bold text-main">Audit Evidence Trail</h2>
        </div>

        <div className="surface-card rounded-lg border border-subtle overflow-hidden">
          <div className="p-4 border-b border-subtle bg-surface-secondary">
            <h3 className="font-bold text-main">{primaryStd}</h3>
            <p className="text-xs text-secondary">{primaryTitle}</p>
          </div>
          <div className="p-4">
            <div className="flex flex-col gap-3 relative before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-border-subtle">
              <div className="flex gap-3 relative z-10">
                <div className="w-4 h-4 rounded-full bg-green-500 mt-0.5 border-2 border-surface"></div>
                <div>
                  <div className="text-sm font-bold text-main">{primaryStd}</div>
                  <div className="text-xs text-secondary">Direct Governing Mandate</div>
                </div>
              </div>
              <div className="flex gap-3 relative z-10">
                <div className="w-4 h-4 rounded-full bg-blue-500 mt-0.5 border-2 border-surface"></div>
                <div>
                  <div className="text-sm font-bold text-main">IS 16107 (Part 2/Sec 1)</div>
                  <div className="text-xs text-secondary">Normative Reference</div>
                </div>
              </div>
              <div className="flex gap-3 relative z-10">
                <div className="w-4 h-4 rounded-full bg-purple-500 mt-0.5 border-2 border-surface"></div>
                <div>
                  <div className="text-sm font-bold text-main">IS/IEC 60529</div>
                  <div className="text-xs text-secondary">Type Test Requirement</div>
                </div>
              </div>
              <div className="flex gap-3 relative z-10 opacity-60">
                <div className="w-4 h-4 rounded-full bg-gray-400 mt-0.5 border-2 border-surface"></div>
                <div>
                  <div className="text-sm font-bold text-main line-through">IS 1944:1981</div>
                  <div className="text-xs text-secondary">Withdrawn / Superseded</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="surface-card p-4 rounded-lg border border-subtle mt-auto">
          <h3 className="font-bold text-main mb-3 flex items-center gap-2">
            <CheckSquare size={18} className="text-brand-primary" />
            Compliance Readiness Checklist
          </h3>
          <div className="flex flex-col gap-2">
            <label className="flex items-start gap-2 text-sm text-secondary cursor-pointer">
              <input type="checkbox" defaultChecked className="mt-1 text-brand-primary rounded" />
              <span>BIS ISI Mark procurement clause included</span>
            </label>
            <label className="flex items-start gap-2 text-sm text-secondary cursor-pointer">
              <input type="checkbox" defaultChecked className="mt-1 text-brand-primary rounded" />
              <span>NABL lab test report requirement specified</span>
            </label>
            <label className="flex items-start gap-2 text-sm text-secondary cursor-pointer">
              <input type="checkbox" defaultChecked className="mt-1 text-brand-primary rounded" />
              <span>QCO gazette reference cited in tender</span>
            </label>
            <label className="flex items-start gap-2 text-sm text-secondary cursor-pointer">
              <input type="checkbox" defaultChecked className="mt-1 text-brand-primary rounded" />
              <span>BEE star rating minimum specified</span>
            </label>
          </div>
        </div>

      </div>
    </div>
  );
}
