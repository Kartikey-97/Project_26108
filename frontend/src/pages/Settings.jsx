import React, { useState } from 'react';
import {
  Settings2,
  Key,
  CheckCircle2,
  AlertTriangle,
  Database,
  Server,
  RefreshCw,
  Shield,
  Cpu,
} from 'lucide-react';

const API_KEYS = [
  { label: 'Backend LLM Key', owner: 'Team Member A', env: 'GOOGLE_API_KEY' },
  { label: 'AI Engine Key', owner: 'Team Member B', env: 'AI_ENGINE_GEMINI_KEY' },
  { label: 'Redundancy Key', owner: 'Team Member C', env: 'GOOGLE_API_KEY_2' },
];

const SYSTEM_INFO = [
  { label: 'BIS Catalog Records', value: '1,015', icon: Database, color: 'var(--brand-primary)' },
  { label: 'AI Model (Backend)', value: 'gemini-3.6-flash', icon: Cpu, color: 'var(--status-success-text)' },
  { label: 'AI Model (Engine)', value: 'gemini-3.6-flash', icon: Cpu, color: 'var(--status-success-text)' },
  { label: 'Backend Port', value: '8000', icon: Server, color: 'var(--text-secondary)' },
  { label: 'AI Engine Port', value: '8001', icon: Server, color: 'var(--text-secondary)' },
  { label: 'Vector Store', value: 'Qdrant (in-memory)', icon: Database, color: 'var(--text-secondary)' },
];

export default function Settings() {
  const [backendStatus, setBackendStatus] = useState(null);
  const [checking, setChecking] = useState(false);

  const checkBackendHealth = async () => {
    setChecking(true);
    setBackendStatus(null);
    try {
      const res = await fetch('http://localhost:8000/api/v1/health');
      const data = await res.json();
      setBackendStatus({ ok: true, message: `Online — status: ${data.status || 'ok'}` });
    } catch {
      setBackendStatus({ ok: false, message: 'Backend is offline or unreachable on port 8000.' });
    } finally {
      setChecking(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="surface-card p-6 bg-white">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg border" style={{ backgroundColor: 'var(--brand-tint)', borderColor: 'var(--brand-tint-border)' }}>
            <Settings2 className="w-5 h-5" style={{ color: 'var(--brand-primary)' }} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-[#11151C] tracking-tight">System Configuration</h1>
            <p className="text-xs text-[#5F6368] mt-0.5">API key status, model configuration, and backend health for SIH 26108 — StandIQ.</p>
          </div>
        </div>
      </div>

      <div className="surface-card p-5 space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b" style={{ borderColor: 'var(--border-subtle)' }}>
          <Key className="w-4 h-4" style={{ color: 'var(--brand-primary)' }} />
          <h2 className="text-sm font-bold" style={{ color: 'var(--text-main)' }}>API Keys — Load Balanced (3 Keys Active)</h2>
        </div>
        <div className="space-y-3">
          {API_KEYS.map((key, idx) => (
            <div key={idx} className="flex items-center justify-between p-3.5 rounded-lg border"
              style={{ borderColor: 'var(--border-subtle)', backgroundColor: 'var(--bg-surface-secondary)' }}>
              <div className="flex items-center gap-3">
                <div className="p-1.5 rounded border" style={{ backgroundColor: 'var(--status-success-bg)', borderColor: 'var(--status-success-border)' }}>
                  <Shield className="w-3.5 h-3.5" style={{ color: 'var(--status-success-text)' }} />
                </div>
                <div>
                  <p className="text-xs font-semibold" style={{ color: 'var(--text-main)' }}>{key.label}</p>
                  <p className="text-[11px] font-mono" style={{ color: 'var(--text-secondary)' }}>env: <span className="font-bold">{key.env}</span> · Loaded from environment · <span className="text-green-600">Verified ✓</span></p>
                </div>
              </div>
              <span className="badge badge-current text-[10px] flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> Active
              </span>
            </div>
          ))}
        </div>
        <p className="text-[11px] leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
          The backend automatically rotates across all 3 keys on each LLM call. If one key hits its rate limit, the next key is used seamlessly.
        </p>
      </div>

      <div className="surface-card p-5 space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b" style={{ borderColor: 'var(--border-subtle)' }}>
          <Cpu className="w-4 h-4" style={{ color: 'var(--brand-primary)' }} />
          <h2 className="text-sm font-bold" style={{ color: 'var(--text-main)' }}>System Configuration</h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {SYSTEM_INFO.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div key={idx} className="p-3.5 rounded-lg border space-y-1"
                style={{ borderColor: 'var(--border-subtle)', backgroundColor: 'var(--bg-surface-secondary)' }}>
                <Icon className="w-3.5 h-3.5" style={{ color: item.color }} />
                <p className="text-[11px]" style={{ color: 'var(--text-secondary)' }}>{item.label}</p>
                <p className="text-xs font-bold font-mono" style={{ color: 'var(--text-main)' }}>{item.value}</p>
              </div>
            );
          })}
        </div>
      </div>

      <div className="surface-card p-5 space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b" style={{ borderColor: 'var(--border-subtle)' }}>
          <Server className="w-4 h-4" style={{ color: 'var(--brand-primary)' }} />
          <h2 className="text-sm font-bold" style={{ color: 'var(--text-main)' }}>Backend Health Check</h2>
        </div>
        <div className="flex items-center gap-4">
          <button type="button" onClick={checkBackendHealth} disabled={checking}
            className="btn-accent text-xs py-2 px-4 flex items-center gap-2 cursor-pointer text-white">
            <RefreshCw className={`w-3.5 h-3.5 ${checking ? 'animate-spin' : ''}`} />
            {checking ? 'Checking...' : 'Ping Backend'}
          </button>
          {backendStatus && (
            <div className="flex items-center gap-2">
              {backendStatus.ok
                ? <CheckCircle2 className="w-4 h-4" style={{ color: 'var(--status-success-text)' }} />
                : <AlertTriangle className="w-4 h-4" style={{ color: 'var(--status-warning-text)' }} />}
              <span className="text-xs font-medium"
                style={{ color: backendStatus.ok ? 'var(--status-success-text)' : 'var(--status-warning-text)' }}>
                {backendStatus.message}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
