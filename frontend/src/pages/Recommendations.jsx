import React, { useState } from 'react';
import RecommendedStandards from '../components/recommendations/RecommendedStandards';
import WhyRecommended from '../components/recommendations/WhyRecommended';
import MissingRequirements from '../components/recommendations/MissingRequirements';
import SpecCompleteness from '../components/recommendations/SpecCompleteness';
import {
  MOCK_RECOMMENDED_STANDARDS,
  MOCK_EVIDENCE_MAP,
  MOCK_MISSING_REQUIREMENTS,
  MOCK_COMPLETENESS_DATA
} from '../data/mockData';
import {
  BookOpen,
  HelpCircle,
  AlertTriangle,
  BarChart3,
  GitCompare,
  Download
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Recommendations() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('recommended');
  const [selectedCompareIds, setSelectedCompareIds] = useState(['std-1', 'std-2']);

  const handleToggleCompare = (id) => {
    setSelectedCompareIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const tabs = [
    { id: 'recommended', label: 'Recommended Standards', icon: BookOpen, count: MOCK_RECOMMENDED_STANDARDS.length },
    { id: 'why', label: 'Why Recommended', icon: HelpCircle },
    { id: 'missing', label: 'Missing Requirements', icon: AlertTriangle, count: MOCK_MISSING_REQUIREMENTS.length },
    { id: 'completeness', label: 'Spec Completeness', icon: BarChart3 },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Workspace Header Banner */}
      <div className="surface-card p-6 bg-white flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-[#17202A] tracking-tight">
              BIS Standard Recommendations Report
            </h1>
            <span className="badge badge-current text-[10px]">Verified Audit</span>
          </div>
          <p className="text-xs text-[#667085] mt-1 max-w-2xl">
            Governing Indian Standards (BIS) mapped to draft procurement specification: <span className="font-semibold text-[#17202A]">LED Street Light Fixtures 120W (NH-44 Tender)</span>
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            type="button"
            onClick={() => navigate('/compare')}
            className="btn-secondary text-xs py-2 px-3.5 flex items-center gap-2 cursor-pointer"
          >
            <GitCompare className="w-4 h-4 text-[#087F73]" />
            <span>Compare Selected ({selectedCompareIds.length})</span>
          </button>

          <button
            type="button"
            onClick={() => window.print()}
            className="btn-accent text-xs py-2.5 px-4 flex items-center gap-2 cursor-pointer"
          >
            <Download className="w-4 h-4" />
            <span>Export Report (PDF)</span>
          </button>
        </div>
      </div>

      {/* Editorial Navigation Tabs Bar */}
      <div className="border-b border-[#E5E2D9] flex items-center gap-2 overflow-x-auto pb-0">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2.5 text-xs font-semibold flex items-center gap-2 border-b-2 transition-colors cursor-pointer whitespace-nowrap ${
                isActive
                  ? 'border-[#087F73] text-[#087F73] bg-white rounded-t'
                  : 'border-transparent text-[#667085] hover:text-[#17202A] hover:bg-[#F7F6F1]'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                  isActive ? 'bg-[#EDF6F5] text-[#087F73]' : 'bg-[#F2F1EC] text-[#667085]'
                }`}>
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Tab Content Panels */}
      <div>
        {activeTab === 'recommended' && (
          <RecommendedStandards
            standards={MOCK_RECOMMENDED_STANDARDS}
            onSelectForCompare={handleToggleCompare}
            selectedCompareIds={selectedCompareIds}
          />
        )}

        {activeTab === 'why' && (
          <WhyRecommended evidence={MOCK_EVIDENCE_MAP} />
        )}

        {activeTab === 'missing' && (
          <MissingRequirements missingList={MOCK_MISSING_REQUIREMENTS} />
        )}

        {activeTab === 'completeness' && (
          <SpecCompleteness completeness={MOCK_COMPLETENESS_DATA} />
        )}
      </div>

    </div>
  );
}
