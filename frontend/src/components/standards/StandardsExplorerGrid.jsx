import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, BookOpen, ExternalLink, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { listStandards, searchStandards, toUiStandard } from '../../services/api';

export default function StandardsExplorerGrid() {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [catalog, setCatalog] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => {
      const loader = searchTerm.trim() ? searchStandards(searchTerm.trim()) : listStandards();
      loader.then((items) => setCatalog(items.map(toUiStandard))).catch((err) => setError(err.message));
    }, 200);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Search Header Banner */}
      <div className="surface-card p-6 space-y-4">
        <div>
          <h2 className="text-base font-bold tracking-tight" style={{ color: 'var(--text-main)' }}>
            Bureau of Indian Standards (BIS) Repository
          </h2>
          <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>
            Search across 384+ indexed Indian Standards, test protocols, amendments, and mandatory Quality Control Orders (QCO).
          </p>
        </div>

        {/* Search Input */}
        <div className="space-y-3">
          
          {/* Search Box */}
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by IS code (e.g., IS 10322), title, or technical scope keyword..."
              className="w-full rounded pl-9 pr-3 py-2.5 text-xs font-medium focus:outline-none transition-colors"
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

      {error && <p className="text-xs text-red-600">{error}</p>}

      {/* Catalog Standards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {catalog.map((item) => (
          <div
            key={item.id}
            className="surface-card p-5 flex flex-col justify-between space-y-3 transition-colors"
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-mono font-extrabold text-sm" style={{ color: 'var(--text-main)' }}>
                  {item.standardCode}
                </span>
                <span className="badge badge-current text-[10px]">{item.statusBadge}</span>
              </div>

              <h3 className="text-xs font-bold leading-snug line-clamp-2" style={{ color: 'var(--text-main)' }}>
                {item.title}
              </h3>

              <p className="text-[11px] line-clamp-3 leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                {item.scope}
              </p>
            </div>

            <div
              className="pt-3 border-t flex items-center justify-between text-xs"
              style={{ borderColor: 'var(--border-subtle)' }}
            >
              <span className="font-mono text-[10px]" style={{ color: 'var(--text-secondary)' }}>
                {item.currentVersion}
              </span>
              
              <button
                type="button"
                onClick={() => navigate(`/standards/${encodeURIComponent(item.id)}`)}
                className="text-xs font-semibold flex items-center gap-1 cursor-pointer"
                style={{ color: 'var(--brand-primary)' }}
              >
                <span>View Details</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}
