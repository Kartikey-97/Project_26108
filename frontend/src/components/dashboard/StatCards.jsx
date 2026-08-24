import React from 'react';
import { FileText, BookOpen, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function StatCards({ stats = [] }) {
  const getIcon = (idx) => {
    switch (idx) {
      case 0: return FileText;
      case 1: return BookOpen;
      case 2: return CheckCircle2;
      case 3: return AlertTriangle;
      default: return FileText;
    }
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, idx) => {
        const Icon = getIcon(idx);
        return (
          <div
            key={stat.id}
            className="surface-card p-5 flex flex-col justify-between space-y-2"
          >
            <div className="flex items-center justify-between">
              <span
                className="text-xs font-semibold uppercase tracking-wider"
                style={{ color: 'var(--text-secondary)' }}
              >
                {stat.title}
              </span>
              <div
                className="p-1.5 rounded"
                style={{
                  backgroundColor: 'var(--brand-tint)',
                  color: 'var(--brand-primary)'
                }}
              >
                <Icon className="w-4 h-4" />
              </div>
            </div>

            <div className="flex items-baseline justify-between pt-1">
              <span
                className="text-2xl font-extrabold font-mono"
                style={{ color: 'var(--text-main)' }}
              >
                {stat.value}
              </span>
              <span
                className="text-[11px] font-semibold"
                style={{
                  color:
                    stat.trend === 'up'
                      ? 'var(--status-success-text)'
                      : stat.trend === 'alert'
                      ? 'var(--status-warning-text)'
                      : 'var(--text-secondary)'
                }}
              >
                {stat.change}
              </span>
            </div>

            <p
              className="text-[11px] truncate"
              style={{ color: 'var(--text-secondary)' }}
            >
              {stat.description}
            </p>
          </div>
        );
      })}
    </div>
  );
}
