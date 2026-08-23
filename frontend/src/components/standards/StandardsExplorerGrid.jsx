import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, BookOpen, ExternalLink, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { MOCK_BIS_CATALOG_FULL, PRODUCT_CATEGORIES } from '../../data/mockData';

export default function StandardsExplorerGrid() {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');

  const filteredCatalog = useMemo(() => {
    return MOCK_BIS_CATALOG_FULL.filter((item) => {
      const matchesSearch =
        item.standardCode.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.scope.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesCategory =
        selectedCategory === 'ALL' || item.category === selectedCategory;

      return matchesSearch && matchesCategory;
    });
  }, [searchTerm, selectedCategory]);

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

        {/* Search Input & Category Filter Chips */}
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

          {/* Category Chips */}
          <div className="flex flex-wrap items-center gap-2 pt-1">
            <button
              type="button"
              onClick={() => setSelectedCategory('ALL')}
              className="text-xs px-3 py-1 rounded transition-colors cursor-pointer border"
              style={{
                backgroundColor: selectedCategory === 'ALL' ? 'var(--brand-primary)' : 'var(--bg-surface-secondary)',
                color: selectedCategory === 'ALL' ? '#FFFFFF' : 'var(--text-secondary)',
                borderColor: selectedCategory === 'ALL' ? 'var(--brand-primary)' : 'var(--border-subtle)',
                fontWeight: selectedCategory === 'ALL' ? 600 : 500
              }}
            >
              All Categories
            </button>
            {PRODUCT_CATEGORIES.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => setSelectedCategory(cat)}
                className="text-xs px-3 py-1 rounded transition-colors cursor-pointer border"
                style={{
                  backgroundColor: selectedCategory === cat ? 'var(--brand-primary)' : 'var(--bg-surface-secondary)',
                  color: selectedCategory === cat ? '#FFFFFF' : 'var(--text-secondary)',
                  borderColor: selectedCategory === cat ? 'var(--brand-primary)' : 'var(--border-subtle)',
                  fontWeight: selectedCategory === cat ? 600 : 500
                }}
              >
                {cat}
              </button>
            ))}
          </div>

        </div>
      </div>

      {/* Catalog Standards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredCatalog.map((item) => (
          <div
            key={item.standardCode}
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
                {item.reaffirmedYear} Reaffirmed
              </span>
              
              <button
                type="button"
                onClick={() => navigate(`/standards/${encodeURIComponent(item.standardCode)}`)}
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
