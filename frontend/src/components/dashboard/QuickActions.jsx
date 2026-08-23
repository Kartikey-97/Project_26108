import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MOCK_QUICK_ACTIONS } from '../../data/mockData';
import { ArrowRight, PlusCircle, BookOpen, GitCompare } from 'lucide-react';

export default function QuickActions({ actions = MOCK_QUICK_ACTIONS }) {
  const navigate = useNavigate();

  const getActionIcon = (id) => {
    switch (id) {
      case 'act-1': return PlusCircle;
      case 'act-2': return BookOpen;
      case 'act-3': return GitCompare;
      default: return ArrowRight;
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {actions.map((act) => {
        const Icon = getActionIcon(act.id);
        return (
          <div
            key={act.id}
            className="surface-card p-5 flex flex-col justify-between space-y-3 transition-colors"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <div
                  className="p-2 rounded"
                  style={{
                    backgroundColor: 'var(--brand-tint)',
                    color: 'var(--brand-primary)'
                  }}
                >
                  <Icon className="w-5 h-5" />
                </div>
                <span
                  className="text-[10px] font-bold px-2 py-0.5 rounded uppercase font-mono border"
                  style={{
                    backgroundColor: 'var(--bg-surface-secondary)',
                    borderColor: 'var(--border-subtle)',
                    color: 'var(--text-secondary)'
                  }}
                >
                  {act.badge}
                </span>
              </div>
              <h3 className="text-sm font-bold mb-1" style={{ color: 'var(--text-main)' }}>{act.title}</h3>
              <p className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{act.description}</p>
            </div>

            <button
              onClick={() => navigate(act.link)}
              className="btn-secondary text-xs py-2 px-3 flex items-center justify-between w-full mt-2 cursor-pointer"
            >
              <span>{act.actionText}</span>
              <ArrowRight className="w-3.5 h-3.5" style={{ color: 'var(--text-secondary)' }} />
            </button>
          </div>
        );
      })}
    </div>
  );
}
