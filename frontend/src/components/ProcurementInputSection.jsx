import React, { useState, useEffect } from 'react';
import { FileText, Upload, Sparkles, AlertCircle, ArrowRight, CheckCircle2, Zap, Layers, BookOpen, ShieldAlert, FileCheck, Check } from 'lucide-react';

const PRESET_LED_PROMPT = `Procurement of 120W Smart LED Street Lighting Luminaires for NH-44 Highway Expansion Project.
Requirements:
1. System wattage: 120W ± 5%. Operating voltage: 140V-270V AC.
2. Minimum luminous efficacy: 130 lm/W.
3. Ingress Protection: IP 66 for optical and driver compartment.
4. Surge protection: External 10 kV SPD included.
5. Correlated Color Temperature (CCT): Strictly 5700K ± 50K Only.
6. Total Harmonic Distortion (THD): ≤ 10%.
7. Compliance: Mandatory BIS CRS Registration & QCO certification mark on housing. Housing die-cast ADC12 powder coated.`;

const STAGES = [
  { id: 1, label: 'Document & Requirement Extraction', icon: Layers },
  { id: 2, label: 'BIS Standard Identification', icon: BookOpen },
  { id: 3, label: 'QCO & Compliance Analysis', icon: ShieldAlert },
  { id: 4, label: 'Evidence & Provenance Generation', icon: FileCheck },
  { id: 5, label: 'Unified Procurement Analysis', icon: CheckCircle2 }
];

export default function ProcurementInputSection({ onAnalyze, isAnalyzing }) {
  const [activeTab, setActiveTab] = useState('text'); // 'text' | 'upload'
  const [inputText, setInputText] = useState(PRESET_LED_PROMPT);
  const [selectedFile, setSelectedFile] = useState(null);
  const [currentStage, setCurrentStage] = useState(1);

  useEffect(() => {
    let interval;
    if (isAnalyzing) {
      setCurrentStage(1);
      interval = setInterval(() => {
        setCurrentStage((prev) => (prev < 5 ? prev + 1 : prev));
      }, 250);
    } else {
      setCurrentStage(5);
    }
    return () => clearInterval(interval);
  }, [isAnalyzing]);

  const handlePresetClick = () => {
    setInputText(PRESET_LED_PROMPT);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onAnalyze({
      text: inputText,
      file: selectedFile,
      inputType: activeTab
    });
  };

  return (
    <div className="surface-card p-6 mb-8 space-y-6">
      
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between pb-4 border-b border-[#E5E2D9] gap-4">
        <div>
          <h2 className="text-base font-semibold text-[#17202A] flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-[#087F73]" />
            1. Start Procurement Analysis
          </h2>
          <p className="text-xs text-[#667085] mt-0.5">
            Submit a procurement requirement description or upload a tender draft to run buyer-side standards intelligence.
          </p>
        </div>

        {/* Input Mode Tabs */}
        <div className="flex items-center gap-1 bg-[#F7F6F1] p-1 rounded border border-[#E5E2D9]">
          <button
            type="button"
            onClick={() => setActiveTab('text')}
            className={`px-3 py-1.5 rounded text-xs font-medium transition-all flex items-center gap-1.5 cursor-pointer ${
              activeTab === 'text'
                ? 'bg-white text-[#17202A] border border-[#E5E2D9] font-semibold'
                : 'text-[#667085] hover:text-[#17202A]'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            Natural Language Description
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('upload')}
            className={`px-3 py-1.5 rounded text-xs font-medium transition-all flex items-center gap-1.5 cursor-pointer ${
              activeTab === 'upload'
                ? 'bg-white text-[#17202A] border border-[#E5E2D9] font-semibold'
                : 'text-[#667085] hover:text-[#17202A]'
            }`}
          >
            <Upload className="w-3.5 h-3.5" />
            Upload Tender PDF / DOCX
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {activeTab === 'text' ? (
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-medium text-[#17202A] flex items-center gap-1.5">
                Technical Procurement Description:
              </label>
              <button
                type="button"
                onClick={handlePresetClick}
                className="text-xs text-[#087F73] hover:text-[#066560] font-medium flex items-center gap-1 bg-[#EDF6F5] px-2.5 py-1 rounded border border-[#C0E3DF] cursor-pointer"
              >
                <Zap className="w-3 h-3 text-[#A8752B]" />
                Load LED Street Lighting Preset (PoC)
              </button>
            </div>
            <textarea
              rows={4}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="e.g. Procurement of LED road lighting luminaires with IP66 protection, 120W rating, surge protection..."
              className="w-full bg-white border border-[#D5D3C8] rounded-lg p-3.5 text-sm text-[#17202A] placeholder-[#9BA3AF] focus:outline-none focus:border-[#087F73] focus:ring-1 focus:ring-[#087F73] transition-all font-mono"
            />
          </div>
        ) : (
          <div className="border-2 border-dashed border-[#D5D3C8] rounded-lg p-6 text-center bg-[#F7F6F1] hover:bg-[#F0EFEA] transition-all">
            <input
              type="file"
              id="tender-file"
              accept=".pdf,.docx,.txt"
              onChange={handleFileUpload}
              className="hidden"
            />
            <label htmlFor="tender-file" className="cursor-pointer flex flex-col items-center justify-center">
              <div className="p-3 rounded-full bg-[#EDF6F5] border border-[#C0E3DF] text-[#087F73] mb-2">
                <Upload className="w-5 h-5" />
              </div>
              <p className="text-sm font-medium text-[#17202A] mb-1">
                {selectedFile ? selectedFile.name : 'Click to upload tender document or drag and drop'}
              </p>
              <p className="text-xs text-[#667085]">PDF, DOCX or TXT (up to 25MB)</p>
              {selectedFile && (
                <div className="mt-3 inline-flex items-center gap-2 bg-[#EBF4F1] border border-[#C4E2DA] text-[#2E6B5B] text-xs px-3 py-1 rounded">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  File uploaded & ready for analysis
                </div>
              )}
            </label>
          </div>
        )}

        {/* Multi-Stage Analysis Progress Tracker */}
        {isAnalyzing && (
          <div className="p-4 rounded-lg bg-[#EDF6F5] border border-[#C0E3DF] space-y-3 animate-fade-in">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-[#087F73] flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-[#087F73] animate-ping"></div>
                2. Analysis Progress: Processing Subsystems...
              </span>
              <span className="text-[#667085] font-mono">Stage {currentStage} of 5</span>
            </div>

            {/* Stepper Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-5 gap-2">
              {STAGES.map((s) => {
                const isCompleted = s.id < currentStage;
                const isCurrent = s.id === currentStage;
                const Icon = s.icon;

                return (
                  <div
                    key={s.id}
                    className={`p-2.5 rounded-lg border text-center transition-all flex flex-col items-center justify-center gap-1 ${
                      isCompleted
                        ? 'bg-[#EBF4F1] border-[#C4E2DA] text-[#2E6B5B]'
                        : isCurrent
                        ? 'bg-white border-[#087F73] text-[#17202A] shadow-sm'
                        : 'bg-white border-[#E5E2D9] text-[#9BA3AF]'
                    }`}
                  >
                    {isCompleted ? (
                      <Check className="w-4 h-4 text-[#2E6B5B]" />
                    ) : (
                      <Icon className={`w-4 h-4 ${isCurrent ? 'text-[#087F73]' : ''}`} />
                    )}
                    <span className="text-[11px] font-medium leading-tight">{s.label}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Action Button Bar */}
        <div className="flex items-center justify-between pt-2 border-t border-[#E5E2D9]">
          <div className="flex items-center gap-2 text-xs text-[#667085]">
            <AlertCircle className="w-4 h-4 text-[#A8752B]" />
            <span>Buyer-Side Pre-Publication Requirement Verification</span>
          </div>

          <button
            type="submit"
            disabled={isAnalyzing}
            className="btn-accent"
          >
            {isAnalyzing ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                Analyzing Intelligence...
              </>
            ) : (
              <>
                Start Procurement Analysis
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
