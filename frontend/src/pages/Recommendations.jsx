import React, { useEffect, useState } from 'react';
import RecommendedStandards from '../components/recommendations/RecommendedStandards';
import WhyRecommended from '../components/recommendations/WhyRecommended';
import MissingRequirements from '../components/recommendations/MissingRequirements';
import SpecCompleteness from '../components/recommendations/SpecCompleteness';
import DataSources from '../components/recommendations/DataSources';
import StandardRelationships from '../components/recommendations/StandardRelationships';
import CertificationEvidence from '../components/recommendations/CertificationEvidence';
import {
  BookOpen,
  HelpCircle,
  AlertTriangle,
  BarChart3,
  GitCompare,
  Download,
  Globe,
  Network,
  ShieldCheck,
} from 'lucide-react';
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { getAnalysis, getReport, toUiAnalysis } from '../services/api';

export default function Recommendations() {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const [liveResult, setLiveResult] = useState(location.state?.result || null);
  const [error, setError] = useState('');

  useEffect(() => {
    const analysisId = searchParams.get('analysis');
    if (analysisId && !location.state?.result) {
      getAnalysis(analysisId).then((analysis) => setLiveResult(toUiAnalysis(analysis))).catch((err) => setError(err.message));
    }
  }, [searchParams, location.state]);
  
  const recommendedStandards = liveResult?.standards_intelligence || [];
  const missingRequirements = liveResult?.pre_publication_summary?.missing_recommendations || [];
  const completenessData = liveResult?.pre_publication_summary?.scorecard;

  const [activeTab, setActiveTab] = useState('recommended');
  const [selectedCompareIds, setSelectedCompareIds] = useState([]);

  const handleToggleCompare = (id) => {
    setSelectedCompareIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const tabs = [
    { id: 'recommended', label: 'Recommended Standards', icon: BookOpen, count: recommendedStandards.length },
    { id: 'why', label: 'Why Recommended', icon: HelpCircle },
    { id: 'missing', label: 'Missing Requirements', icon: AlertTriangle, count: missingRequirements.length },
    { id: 'completeness', label: 'Spec Completeness', icon: BarChart3 },
    { id: 'relationships', label: 'Standard Relationships', icon: Network },
    { id: 'certification', label: 'Certification & Evidence', icon: ShieldCheck },
    { id: 'sources', label: 'Data Sources', icon: Globe },
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
            Governing Indian Standards (BIS) mapped to draft procurement specification: <span className="font-semibold text-[#17202A]">{liveResult?.input_summary?.category || "Analyzed Document"}</span>
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            type="button"
            onClick={() => navigate(`/compare?ids=${selectedCompareIds.join(',')}`)}
            className="btn-secondary text-xs py-2 px-3.5 flex items-center gap-2 cursor-pointer"
          >
            <GitCompare className="w-4 h-4 text-[#087F73]" />
            <span>Compare Selected ({selectedCompareIds.length})</span>
          </button>

          <button
            type="button"
            onClick={async () => {
              if (!liveResult?.id) return window.print();
              const report = await getReport(liveResult.id);
              const url = URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' }));
              const link = document.createElement('a');
              link.href = url; link.download = `analysis-${liveResult.id}-report.json`; link.click();
              URL.revokeObjectURL(url);
            }}
            className="btn-accent text-xs py-2.5 px-4 flex items-center gap-2 cursor-pointer"
          >
            <Download className="w-4 h-4" />
            <span>Export Report (PDF)</span>
          </button>
        </div>
      </div>

      {error && <p className="text-xs text-red-600">{error}</p>}
      {!liveResult && !error && <p className="text-xs text-[#667085]">Open a completed analysis from History or run a new analysis to view live recommendations.</p>}

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
            standards={recommendedStandards}
            onSelectForCompare={handleToggleCompare}
            selectedCompareIds={selectedCompareIds}
          />
        )}

        {activeTab === 'why' && (
          <WhyRecommended evidence={liveResult?.evidence || []} />
        )}

        {activeTab === 'missing' && (
          <MissingRequirements missingList={missingRequirements} />
        )}

        {activeTab === 'completeness' && completenessData && (
          <SpecCompleteness completeness={completenessData} />
        )}
        {activeTab === 'completeness' && !completenessData && (
          <SpecCompleteness />
        )}

        {activeTab === 'relationships' && (
          <StandardRelationships
            standards={recommendedStandards}
            analysisTitle={liveResult?.input_summary?.title || ''}
          />
        )}

        {activeTab === 'certification' && (
          <CertificationEvidence
            standards={recommendedStandards}
            analysisId={liveResult?.id || ''}
          />
        )}

        {activeTab === 'sources' && (
          <DataSources analysisId={liveResult?.id || ''} />
        )}
      </div>

    </div>
  );
}
