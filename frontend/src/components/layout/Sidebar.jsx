import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  PlusCircle,
  History,
  BookOpen,
  GitCompare,
  Settings,
  ShieldCheck,
  X
} from 'lucide-react';

export default function Sidebar({ isOpen, onClose }) {
  const mainNavItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'New Analysis', path: '/analyze', icon: PlusCircle },
    { name: 'Analysis History', path: '/history', icon: History },
    { name: 'Standards Explorer', path: '/standards', icon: BookOpen },
  ];

  const workspaceNavItems = [
    { name: 'Compare Standards', path: '/compare', icon: GitCompare },
  ];

  const systemNavItems = [
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/20 md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar Drawer */}
      <aside
        className={`fixed top-0 left-0 z-50 h-full w-64 bg-[#F7F6F1] border-r border-[#E5E2D9] text-[#11151C] flex flex-col transition-transform duration-200 ease-in-out md:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 px-5 flex items-center justify-between border-b border-[#E5E2D9] shrink-0 bg-[#F7F6F1]">
          <NavLink to="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div className="p-2 rounded bg-[#11151C] text-white">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-[#11151C] tracking-wide">StandIQ</h1>
              <p className="text-[10px] text-[#5F6368] font-medium">ProcureIntel BIS Engine</p>
            </div>
          </NavLink>

          <button
            onClick={onClose}
            className="md:hidden p-1.5 rounded text-[#5F6368] hover:text-[#11151C] hover:bg-[#E5E3DC]"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Navigation Sections */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
          
          {/* MAIN Section */}
          <div>
            <p className="px-3 text-[10px] font-bold text-[#5F6368] uppercase tracking-wider mb-2">
              MAIN
            </p>
            <nav className="space-y-1">
              {mainNavItems.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    onClick={onClose}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2 rounded text-xs font-medium transition-colors ${
                        isActive
                          ? 'bg-[#176B63]/10 text-[#176B63] font-semibold border-l-2 border-[#176B63]'
                          : 'text-[#5F6368] hover:text-[#11151C] hover:bg-[#E5E3DC]/60'
                      }`
                    }
                  >
                    <Icon className="w-4 h-4 shrink-0 text-[#5F6368]" />
                    <span>{item.name}</span>
                  </NavLink>
                );
              })}
            </nav>
          </div>

          {/* WORKSPACE Section */}
          <div>
            <p className="px-3 text-[10px] font-bold text-[#5F6368] uppercase tracking-wider mb-2">
              WORKSPACE
            </p>
            <nav className="space-y-1">
              {workspaceNavItems.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    onClick={onClose}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2 rounded text-xs font-medium transition-colors ${
                        isActive
                          ? 'bg-[#176B63]/10 text-[#176B63] font-semibold border-l-2 border-[#176B63]'
                          : 'text-[#5F6368] hover:text-[#11151C] hover:bg-[#E5E3DC]/60'
                      }`
                    }
                  >
                    <Icon className="w-4 h-4 shrink-0 text-[#5F6368]" />
                    <span>{item.name}</span>
                  </NavLink>
                );
              })}
            </nav>
          </div>

          {/* SYSTEM Section */}
          <div>
            <p className="px-3 text-[10px] font-bold text-[#5F6368] uppercase tracking-wider mb-2">
              SYSTEM
            </p>
            <nav className="space-y-1">
              {systemNavItems.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    onClick={onClose}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2 rounded text-xs font-medium transition-colors ${
                        isActive
                          ? 'bg-[#176B63]/10 text-[#176B63] font-semibold border-l-2 border-[#176B63]'
                          : 'text-[#5F6368] hover:text-[#11151C] hover:bg-[#E5E3DC]/60'
                      }`
                    }
                  >
                    <Icon className="w-4 h-4 shrink-0 text-[#5F6368]" />
                    <span>{item.name}</span>
                  </NavLink>
                );
              })}
            </nav>
          </div>

        </div>

        {/* Bottom Profile Info Card */}
        <div className="p-3 border-t border-[#E5E3DC] bg-[#F7F6F1]">
          <div className="flex items-center gap-3 p-2 rounded bg-white border border-[#E5E3DC]">
            <div className="w-8 h-8 rounded bg-[#EDF6F5] border border-[#C0E3DF] text-[#176B63] font-bold text-xs flex items-center justify-center shrink-0">
              PO
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-[#11151C] truncate">Procurement Officer</p>
              <p className="text-[10px] text-[#5F6368] truncate">Public Works Dept</p>
            </div>
          </div>
        </div>

      </aside>
    </>
  );
}
