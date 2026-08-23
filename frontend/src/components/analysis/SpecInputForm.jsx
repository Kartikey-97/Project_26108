import React, { useState } from 'react';
import {
  PRODUCT_CATEGORIES,
  INDUSTRY_DOMAINS,
  PRESET_SPEC_SAMPLES
} from '../../data/mockData';
import { ArrowRight, RotateCcw } from 'lucide-react';

export default function SpecInputForm({ onSubmitSpec }) {
  const [selectedCategory, setSelectedCategory] = useState(PRODUCT_CATEGORIES[0]);
  const [selectedDomain, setSelectedDomain] = useState(INDUSTRY_DOMAINS[0]);
  const [department, setDepartment] = useState('Public Works Department (PWD)');
  const [specText, setSpecText] = useState(PRESET_SPEC_SAMPLES[0].text);

  const handleLoadSample = (sample) => {
    setSelectedCategory(sample.category);
    setSelectedDomain(sample.domain);
    setDepartment(sample.department);
    setSpecText(sample.text);
  };

  const handleClear = () => {
    setSpecText('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!specText.trim()) return;

    onSubmitSpec({
      category: selectedCategory,
      domain: selectedDomain,
      department,
      specText
    });
  };

  return (
    <form onSubmit={handleSubmit} className="surface-card p-6 space-y-6">
      
      {/* Form Header */}
      <div className="pb-4 border-b" style={{ borderColor: 'var(--border-subtle)' }}>
        <h2 className="text-base font-bold tracking-tight" style={{ color: 'var(--text-main)' }}>
          Enter Specification Details
        </h2>
        <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>
          Enter technical specifications, operating parameters, material standards, or select a sample preset below.
        </p>

        {/* Preset Loader Chips */}
        <div className="flex items-center gap-2 mt-3 flex-wrap">
          <span className="text-[11px] font-semibold" style={{ color: 'var(--text-secondary)' }}>Sample Presets:</span>
          {PRESET_SPEC_SAMPLES.map((sample) => (
            <button
              key={sample.id}
              type="button"
              onClick={() => handleLoadSample(sample)}
              className="text-xs px-3 py-1 rounded transition-colors cursor-pointer border"
              style={{
                backgroundColor: 'var(--brand-tint)',
                borderColor: 'var(--brand-tint-border)',
                color: 'var(--brand-primary)'
              }}
            >
              {sample.label}
            </button>
          ))}
        </div>
      </div>

      {/* Section 1: Basic Information */}
      <div className="space-y-4">
        <h3
          className="text-xs font-bold uppercase tracking-wider"
          style={{ color: 'var(--text-secondary)' }}
        >
          1. Basic Information & Metadata
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          
          {/* Category Dropdown */}
          <div>
            <label className="block text-xs font-medium mb-1.5" style={{ color: 'var(--text-main)' }}>
              Product Category <span style={{ color: 'var(--status-error-text)' }}>*</span>
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full rounded px-3 py-2 text-xs font-medium cursor-pointer focus:outline-none transition-colors"
              style={{
                backgroundColor: 'var(--input-bg)',
                borderColor: 'var(--input-border)',
                borderWidth: '1px',
                color: 'var(--text-main)'
              }}
            >
              {PRODUCT_CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* Industry Domain Dropdown */}
          <div>
            <label className="block text-xs font-medium mb-1.5" style={{ color: 'var(--text-main)' }}>
              Industry Domain <span style={{ color: 'var(--status-error-text)' }}>*</span>
            </label>
            <select
              value={selectedDomain}
              onChange={(e) => setSelectedDomain(e.target.value)}
              className="w-full rounded px-3 py-2 text-xs font-medium cursor-pointer focus:outline-none transition-colors"
              style={{
                backgroundColor: 'var(--input-bg)',
                borderColor: 'var(--input-border)',
                borderWidth: '1px',
                color: 'var(--text-main)'
              }}
            >
              {INDUSTRY_DOMAINS.map((dom) => (
                <option key={dom} value={dom}>
                  {dom}
                </option>
              ))}
            </select>
          </div>

          {/* Department Name Input */}
          <div>
            <label className="block text-xs font-medium mb-1.5" style={{ color: 'var(--text-main)' }}>
              Procuring Department / Authority
            </label>
            <input
              type="text"
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              placeholder="e.g. Ministry of Jal Shakti, PWD"
              className="w-full rounded px-3 py-2 text-xs font-medium focus:outline-none transition-colors"
              style={{
                backgroundColor: 'var(--input-bg)',
                borderColor: 'var(--input-border)',
                borderWidth: '1px',
                color: 'var(--text-main)'
              }}
            />
          </div>

        </div>
      </div>

      {/* Section 2: Technical Specification Textarea */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <label
            className="block text-xs font-bold uppercase tracking-wider"
            style={{ color: 'var(--text-secondary)' }}
          >
            2. Technical Specification & Performance Clauses <span style={{ color: 'var(--status-error-text)' }}>*</span>
          </label>

          <span className="text-[11px] font-mono" style={{ color: 'var(--text-muted)' }}>
            {specText.length} characters
          </span>
        </div>

        <textarea
          rows={7}
          value={specText}
          onChange={(e) => setSpecText(e.target.value)}
          placeholder="Describe the product, intended application, operating voltage, luminous efficacy, IP ingress rating, surge protection, material grade, and performance expectations..."
          className="w-full rounded p-3.5 text-xs font-mono leading-relaxed resize-y focus:outline-none transition-colors"
          style={{
            backgroundColor: 'var(--input-bg)',
            borderColor: 'var(--input-border)',
            borderWidth: '1px',
            color: 'var(--text-main)'
          }}
          required
        />
      </div>

      {/* Form Action Controls */}
      <div className="pt-2 border-t flex items-center justify-between" style={{ borderColor: 'var(--border-subtle)' }}>
        <button
          type="button"
          onClick={handleClear}
          className="btn-secondary text-xs py-2 px-3 flex items-center gap-1.5"
        >
          <RotateCcw className="w-3.5 h-3.5" style={{ color: 'var(--text-secondary)' }} />
          <span>Clear Text</span>
        </button>

        <button
          type="submit"
          className="btn-accent text-xs py-2.5 px-5 flex items-center gap-2 cursor-pointer text-white"
        >
          <span>Run AI Recommendation Analysis</span>
          <ArrowRight className="w-4 h-4 text-white" />
        </button>
      </div>

    </form>
  );
}
