import React from 'react';
import { PlusCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function WelcomeBanner() {
  const navigate = useNavigate();

  return (
    <div className="surface-card p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
      <div>
        <h1 className="text-xl font-bold tracking-tight" style={{ color: 'var(--text-main)' }}>
          Procurement Intelligence Dashboard
        </h1>
        <p className="text-xs mt-1 max-w-2xl leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
          Automated recommendation system for identifying governing Indian Standards (BIS) and Quality Control Orders (QCO) for government tender specifications.
        </p>
      </div>

      <div className="flex items-center gap-3 shrink-0">
        <button
          onClick={() => navigate('/analyze')}
          className="btn-accent text-xs py-2.5 px-4 flex items-center gap-2 cursor-pointer text-white"
        >
          <PlusCircle className="w-4 h-4 text-white" />
          <span>New Specification Analysis</span>
        </button>
      </div>
    </div>
  );
}
