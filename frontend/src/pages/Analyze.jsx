import React, { useState } from 'react';
import SpecInputForm from '../components/analysis/SpecInputForm';
import FileUploadZone from '../components/analysis/FileUploadZone';
import AiProcessingScreen from '../components/analysis/AiProcessingScreen';
import ExtractedRequirements from '../components/analysis/ExtractedRequirements';
import { MOCK_EXTRACTED_SUMMARY, MOCK_EXTRACTED_REQUIREMENTS } from '../data/mockData';
import { FileText, Upload } from 'lucide-react';

export default function Analyze() {
  const [activeInputTab, setActiveInputTab] = useState('text'); // 'text' | 'file'
  const [analysisState, setAnalysisState] = useState('INPUT'); // 'INPUT' | 'PROCESSING' | 'EXTRACTED'
  const [extractedSummary, setExtractedSummary] = useState(MOCK_EXTRACTED_SUMMARY);
  const [extractedReqs, setExtractedReqs] = useState(MOCK_EXTRACTED_REQUIREMENTS);

  const handleStartProcessing = () => {
    setAnalysisState('PROCESSING');
  };

  const handleProcessingComplete = () => {
    setAnalysisState('EXTRACTED');
  };

  const handleResetAnalysis = () => {
    setAnalysisState('INPUT');
  };

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Workspace Header Banner */}
      <div className="surface-card p-6 border-[#E5E3DC] bg-white flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-1 max-w-2xl">
          <span className="text-[10px] font-bold text-[#176B63] bg-[#EDF6F5] px-2.5 py-0.5 rounded border border-[#C0E3DF] font-mono">
            Specification Audit Workspace
          </span>

          <h1 className="text-xl font-bold text-[#11151C] tracking-tight">
            New Specification Analysis & BIS Mapping
          </h1>

          <p className="text-xs text-[#5F6368] leading-relaxed">
            Input procurement tender specifications or upload PDF/DOCX tender documents to automatically extract technical parameters, evaluate completeness, and map mandatory Indian Standards (BIS).
          </p>
        </div>

        {/* Input Mode Switcher (Visible during INPUT state) */}
        {analysisState === 'INPUT' && (
          <div className="flex items-center gap-1 bg-[#F2F1EC] p-1 rounded border border-[#E5E3DC] shrink-0">
            <button
              onClick={() => setActiveInputTab('text')}
              className={`px-3.5 py-1.5 rounded text-xs font-medium transition-colors flex items-center gap-2 cursor-pointer ${
                activeInputTab === 'text'
                  ? 'bg-white text-[#11151C] font-semibold border border-[#E5E3DC]'
                  : 'text-[#5F6368] hover:text-[#11151C]'
              }`}
            >
              <FileText className="w-4 h-4 text-[#176B63]" />
              <span>Text Input</span>
            </button>
            <button
              onClick={() => setActiveInputTab('file')}
              className={`px-3.5 py-1.5 rounded text-xs font-medium transition-colors flex items-center gap-2 cursor-pointer ${
                activeInputTab === 'file'
                  ? 'bg-white text-[#11151C] font-semibold border border-[#E5E3DC]'
                  : 'text-[#5F6368] hover:text-[#11151C]'
              }`}
            >
              <Upload className="w-4 h-4 text-[#176B63]" />
              <span>Document Upload</span>
            </button>
          </div>
        )}
      </div>

      {/* State View 1: Input Forms */}
      {analysisState === 'INPUT' && (
        <>
          {activeInputTab === 'text' ? (
            <SpecInputForm onSubmitSpec={handleStartProcessing} />
          ) : (
            <FileUploadZone onStartFileAnalysis={handleStartProcessing} />
          )}
        </>
      )}

      {/* State View 2: Technical Execution Pipeline */}
      {analysisState === 'PROCESSING' && (
        <AiProcessingScreen onCompleteProcessing={handleProcessingComplete} />
      )}

      {/* State View 3: Extracted Technical Requirements Editor */}
      {analysisState === 'EXTRACTED' && (
        <ExtractedRequirements
          summary={extractedSummary}
          requirements={extractedReqs}
          onReAnalyze={handleResetAnalysis}
        />
      )}

    </div>
  );
}
