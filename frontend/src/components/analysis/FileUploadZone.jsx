import React, { useState } from 'react';
import { Upload, FileText, X, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function FileUploadZone({ onStartFileAnalysis }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
  };

  const handleSampleSelect = (filename, size) => {
    setSelectedFile({
      name: filename,
      size: size,
      type: 'application/pdf',
      isSample: true
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedFile) return;
    if (onStartFileAnalysis) onStartFileAnalysis();
  };

  return (
    <div className="surface-card p-6 space-y-6">
      
      {/* Header */}
      <div className="pb-4 border-b" style={{ borderColor: 'var(--border-subtle)' }}>
        <h2 className="text-base font-bold tracking-tight" style={{ color: 'var(--text-main)' }}>
          Upload Procurement Tender Document
        </h2>
        <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>
          Upload tender PDF, DOCX, or TXT specification documents for automated AI requirement extraction.
        </p>

        {/* Sample Document Chips */}
        <div className="flex items-center gap-2 mt-3 flex-wrap">
          <span className="text-[11px] font-semibold" style={{ color: 'var(--text-secondary)' }}>Sample Documents:</span>
          <button
            type="button"
            onClick={() => handleSampleSelect('LED_Street_Lighting_Tender_2026.pdf', 2450000)}
            className="text-xs px-3 py-1 rounded transition-colors cursor-pointer border"
            style={{
              backgroundColor: 'var(--brand-tint)',
              borderColor: 'var(--brand-tint-border)',
              color: 'var(--brand-primary)'
            }}
          >
            LED_Street_Lighting_Tender_2026.pdf (2.4 MB)
          </button>
          <button
            type="button"
            onClick={() => handleSampleSelect('Solar_Water_Pump_Specs.docx', 1850000)}
            className="text-xs px-3 py-1 rounded transition-colors cursor-pointer border"
            style={{
              backgroundColor: 'var(--brand-tint)',
              borderColor: 'var(--brand-tint-border)',
              color: 'var(--brand-primary)'
            }}
          >
            Solar_Water_Pump_Specs.docx (1.8 MB)
          </button>
        </div>
      </div>

      {/* Drag & Drop Container */}
      {!selectedFile ? (
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className="border-2 border-dashed rounded-lg p-8 text-center space-y-3 transition-colors"
          style={{
            borderColor: dragActive ? 'var(--brand-primary)' : 'var(--border-strong)',
            backgroundColor: dragActive ? 'var(--brand-tint)' : 'var(--bg-surface-secondary)'
          }}
        >
          <div
            className="p-3 rounded-full w-12 h-12 flex items-center justify-center mx-auto border"
            style={{
              backgroundColor: 'var(--brand-tint)',
              borderColor: 'var(--brand-tint-border)',
              color: 'var(--brand-primary)'
            }}
          >
            <Upload className="w-6 h-6" />
          </div>

          <div className="space-y-1">
            <p className="text-xs font-semibold" style={{ color: 'var(--text-main)' }}>
              Drag and drop your specification document here
            </p>
            <p className="text-[11px]" style={{ color: 'var(--text-secondary)' }}>
              Supports PDF, DOCX, and TXT files up to 25MB
            </p>
          </div>

          <div>
            <label className="btn-secondary text-xs py-2 px-4 cursor-pointer">
              <span>Browse Local Files</span>
              <input
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={handleFileSelect}
                className="hidden"
              />
            </label>
          </div>
        </div>
      ) : (
        /* Selected File Card */
        <div
          className="p-4 rounded-lg border flex items-center justify-between"
          style={{
            backgroundColor: 'var(--bg-surface-secondary)',
            borderColor: 'var(--border-subtle)'
          }}
        >
          <div className="flex items-center gap-3">
            <div
              className="p-2.5 rounded border"
              style={{
                backgroundColor: 'var(--brand-tint)',
                borderColor: 'var(--brand-tint-border)',
                color: 'var(--brand-primary)'
              }}
            >
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="text-xs font-bold" style={{ color: 'var(--text-main)' }}>{selectedFile.name}</h4>
                <span className="badge badge-current text-[10px]">
                  <CheckCircle2 className="w-3 h-3" /> Ready
                </span>
              </div>
              <p className="text-[11px] font-mono mt-0.5" style={{ color: 'var(--text-secondary)' }}>
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB • {selectedFile.isSample ? 'Sample Demo File' : 'Uploaded File'}
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleRemoveFile}
            className="p-1.5 rounded transition-colors cursor-pointer"
            style={{ color: 'var(--text-secondary)' }}
            title="Remove File"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Action CTA */}
      <div className="pt-2 border-t flex items-center justify-end" style={{ borderColor: 'var(--border-subtle)' }}>
        <button
          type="button"
          onClick={handleSubmit}
          disabled={!selectedFile}
          className="btn-accent text-xs py-2.5 px-5 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed text-white"
        >
          <span>Analyze Document Specs</span>
          <ArrowRight className="w-4 h-4 text-white" />
        </button>
      </div>

    </div>
  );
}
