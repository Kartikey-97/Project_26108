import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Filter,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ArrowUpRight,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Inbox
} from 'lucide-react';
import { MOCK_FULL_HISTORY_LIST, PRODUCT_CATEGORIES } from '../../data/mockData';

export default function AnalysisHistoryTable() {
  const navigate = useNavigate();
  const [historyList, setHistoryList] = useState(MOCK_FULL_HISTORY_LIST);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  const filteredList = useMemo(() => {
    return historyList.filter((item) => {
      const matchesSearch =
        item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.department.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.standards.some((s) => s.toLowerCase().includes(searchTerm.toLowerCase()));

      const matchesCategory =
        selectedCategory === 'ALL' || item.category === selectedCategory;

      const matchesStatus =
        selectedStatus === 'ALL' || item.status === selectedStatus;

      return matchesSearch && matchesCategory && matchesStatus;
    });
  }, [historyList, searchTerm, selectedCategory, selectedStatus]);

  const totalPages = Math.ceil(filteredList.length / itemsPerPage) || 1;
  const paginatedList = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage;
    return filteredList.slice(start, start + itemsPerPage);
  }, [filteredList, currentPage]);

  const handleDeleteEntry = (id) => {
    setHistoryList((prev) => prev.filter((item) => item.id !== id));
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'COMPLETED':
        return (
          <span className="badge badge-current text-[10px]">
            <CheckCircle2 className="w-3 h-3" /> Completed
          </span>
        );
      case 'WARNING_FLAGGED':
        return (
          <span className="badge badge-amended text-[10px]">
            <AlertTriangle className="w-3 h-3" /> Flagged Clause
          </span>
        );
      case 'IN_REVIEW':
        return (
          <span className="badge badge-qco text-[10px]">
            <Clock className="w-3 h-3" /> In Review
          </span>
        );
      default:
        return <span className="badge badge-current text-[10px]">{status}</span>;
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Search & Filters Bar */}
      <div className="surface-card p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Search Bar */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1);
            }}
            placeholder="Search by title, ref ID, department, or IS standard..."
            className="w-full rounded pl-9 pr-3 py-2 text-xs font-medium focus:outline-none transition-colors"
            style={{
              backgroundColor: 'var(--input-bg)',
              borderColor: 'var(--input-border)',
              borderWidth: '1px',
              color: 'var(--text-main)'
            }}
          />
        </div>

        {/* Filter Dropdowns */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto justify-end">
          
          {/* Category Filter */}
          <div
            className="flex items-center gap-1.5 px-3 py-1.5 rounded border text-xs"
            style={{
              backgroundColor: 'var(--bg-surface-secondary)',
              borderColor: 'var(--border-subtle)',
              color: 'var(--text-secondary)'
            }}
          >
            <Filter className="w-3.5 h-3.5" style={{ color: 'var(--text-secondary)' }} />
            <span style={{ color: 'var(--text-secondary)' }}>Category:</span>
            <select
              value={selectedCategory}
              onChange={(e) => {
                setSelectedCategory(e.target.value);
                setCurrentPage(1);
              }}
              className="bg-transparent font-medium outline-none cursor-pointer text-xs"
              style={{ color: 'var(--text-main)' }}
            >
              <option value="ALL">All Categories</option>
              {PRODUCT_CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div
            className="flex items-center gap-1.5 px-3 py-1.5 rounded border text-xs"
            style={{
              backgroundColor: 'var(--bg-surface-secondary)',
              borderColor: 'var(--border-subtle)',
              color: 'var(--text-secondary)'
            }}
          >
            <span style={{ color: 'var(--text-secondary)' }}>Status:</span>
            <select
              value={selectedStatus}
              onChange={(e) => {
                setSelectedStatus(e.target.value);
                setCurrentPage(1);
              }}
              className="bg-transparent font-medium outline-none cursor-pointer text-xs"
              style={{ color: 'var(--text-main)' }}
            >
              <option value="ALL">All Statuses</option>
              <option value="COMPLETED">Completed</option>
              <option value="WARNING_FLAGGED">Flagged Issues</option>
              <option value="IN_REVIEW">In Review</option>
            </select>
          </div>

        </div>

      </div>

      {/* Main Analysis Table / Empty State */}
      {paginatedList.length > 0 ? (
        <div className="surface-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs" style={{ color: 'var(--text-main)' }}>
              <thead
                className="uppercase font-semibold text-[11px] border-b"
                style={{
                  backgroundColor: 'var(--bg-surface-secondary)',
                  borderColor: 'var(--border-subtle)',
                  color: 'var(--text-secondary)'
                }}
              >
                <tr>
                  <th className="p-3.5">Analysis Ref / Title</th>
                  <th className="p-3.5">Department</th>
                  <th className="p-3.5">Mapped Standards</th>
                  <th className="p-3.5">Completeness</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody
                className="divide-y font-sans"
                style={{ borderColor: 'var(--border-subtle)' }}
              >
                {paginatedList.map((item) => (
                  <tr
                    key={item.id}
                    className="transition-colors hover:bg-[var(--bg-surface-hover)]"
                  >
                    
                    <td className="p-3.5 max-w-xs">
                      <span className="text-[10px] font-mono block mb-0.5" style={{ color: 'var(--text-muted)' }}>{item.id}</span>
                      <span className="font-semibold truncate block" style={{ color: 'var(--text-main)' }}>{item.title}</span>
                      <span className="text-[11px] block font-medium" style={{ color: 'var(--brand-primary)' }}>{item.category}</span>
                    </td>

                    <td className="p-3.5">
                      <span className="block truncate max-w-[180px] font-medium" style={{ color: 'var(--text-main)' }}>{item.department}</span>
                      <span className="text-[10px] font-mono" style={{ color: 'var(--text-muted)' }}>{item.date}</span>
                    </td>

                    <td className="p-3.5">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className="font-mono font-semibold" style={{ color: 'var(--brand-primary)' }}>
                          {item.standardsCount} Standards
                        </span>
                        {item.qcoMandatory && (
                          <span className="badge badge-qco text-[9px]">
                            QCO
                          </span>
                        )}
                      </div>
                      <p className="text-[10px] font-mono truncate max-w-[160px] mt-0.5" style={{ color: 'var(--text-secondary)' }}>
                        {item.standards.join(', ')}
                      </p>
                    </td>

                    <td className="p-3.5">
                      <div className="flex items-center gap-2">
                        <span className="font-bold font-mono" style={{ color: 'var(--text-main)' }}>{item.completenessScore}%</span>
                        <div
                          className="w-16 h-1.5 rounded-full overflow-hidden"
                          style={{ backgroundColor: 'var(--border-subtle)' }}
                        >
                          <div
                            className="h-full rounded-full"
                            style={{
                              width: `${item.completenessScore}%`,
                              backgroundColor:
                                item.completenessScore >= 90
                                  ? 'var(--brand-primary)'
                                  : item.completenessScore >= 80
                                  ? 'var(--brand-primary)'
                                  : 'var(--status-warning-text)'
                            }}
                          />
                        </div>
                      </div>
                    </td>

                    <td className="p-3.5">
                      {getStatusBadge(item.status)}
                    </td>

                    <td className="p-3.5 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          type="button"
                          onClick={() => navigate('/recommendations')}
                          className="btn-accent text-[11px] py-1 px-2.5 flex items-center gap-1 cursor-pointer text-white"
                        >
                          <span>Report</span>
                          <ArrowUpRight className="w-3 h-3 text-white" />
                        </button>

                        <button
                          type="button"
                          onClick={() => handleDeleteEntry(item.id)}
                          className="p-1 rounded transition-colors cursor-pointer border"
                          style={{
                            backgroundColor: 'var(--bg-surface-secondary)',
                            borderColor: 'var(--border-subtle)',
                            color: 'var(--text-secondary)'
                          }}
                          title="Delete Analysis"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>

                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer Bar */}
          <div
            className="p-4 border-t flex flex-col sm:flex-row items-center justify-between gap-3 text-xs"
            style={{
              backgroundColor: 'var(--bg-surface-secondary)',
              borderColor: 'var(--border-subtle)',
              color: 'var(--text-secondary)'
            }}
          >
            <span>
              Showing <span className="font-medium" style={{ color: 'var(--text-main)' }}>{(currentPage - 1) * itemsPerPage + 1}</span> to{' '}
              <span className="font-medium" style={{ color: 'var(--text-main)' }}>
                {Math.min(currentPage * itemsPerPage, filteredList.length)}
              </span>{' '}
              of <span className="font-medium" style={{ color: 'var(--text-main)' }}>{filteredList.length}</span> analyses
            </span>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
                disabled={currentPage === 1}
                className="btn-secondary p-1.5 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>

              <span className="font-mono px-2" style={{ color: 'var(--text-main)' }}>
                Page {currentPage} of {totalPages}
              </span>

              <button
                type="button"
                onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
                disabled={currentPage === totalPages}
                className="btn-secondary p-1.5 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* Empty State */
        <div className="surface-card p-12 text-center space-y-4">
          <div
            className="p-3 rounded-full w-12 h-12 flex items-center justify-center mx-auto border"
            style={{
              backgroundColor: 'var(--bg-surface-secondary)',
              borderColor: 'var(--border-subtle)',
              color: 'var(--text-secondary)'
            }}
          >
            <Inbox className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <h3 className="text-sm font-bold" style={{ color: 'var(--text-main)' }}>No Procurement Analyses Found</h3>
            <p className="text-xs max-w-sm mx-auto" style={{ color: 'var(--text-secondary)' }}>
              No matching records found for "{searchTerm}".
            </p>
          </div>
          <button
            type="button"
            onClick={() => {
              setSearchTerm('');
              setSelectedCategory('ALL');
              setSelectedStatus('ALL');
            }}
            className="btn-secondary text-xs py-2 px-4 cursor-pointer"
          >
            Clear Filters
          </button>
        </div>
      )}

    </div>
  );
}
