import React, { useState } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
  ShieldCheck,
  Search,
  Bell,
  User,
  Settings,
  Menu,
  X,
  PlusCircle,
  LayoutDashboard,
  History,
  BookOpen,
  GitCompare,
  ExternalLink,
  ChevronDown,
  Moon,
  Sun
} from 'lucide-react';
import { useTheme } from '../../utils/ThemeContext';

export default function TopNavigation() {
  const navigate = useNavigate();
  const location = useLocation();
  const { theme, toggleTheme, isDark } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', aliasPaths: ['/app'], icon: LayoutDashboard },
    { name: 'New Analysis', path: '/analyze', aliasPaths: [], icon: PlusCircle },
    { name: 'Analysis History', path: '/history', aliasPaths: [], icon: History },
    { name: 'Standards Explorer', path: '/standards', aliasPaths: ['/standards/'], icon: BookOpen },
    { name: 'Compare Standards', path: '/compare', aliasPaths: [], icon: GitCompare },
  ];

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/standards?search=${encodeURIComponent(searchQuery.trim())}`);
      setSearchQuery('');
      setMobileMenuOpen(false);
    }
  };

  const isNavActive = (item) => {
    if (location.pathname === item.path) return true;
    if (item.aliasPaths.some((p) => location.pathname.startsWith(p))) return true;
    return false;
  };

  return (
    <header
      className="sticky top-0 z-40 border-b shadow-xs transition-colors duration-150"
      style={{
        backgroundColor: 'var(--header-bg)',
        borderColor: 'var(--border-subtle)'
      }}
    >
      
      {/* ═════════════════════════════════════════════════════════════
          ROW 1: Brand Logo + Search + Theme Toggle + Notifications + Officer Profile
      ═════════════════════════════════════════════════════════════ */}
      <div
        className="border-b transition-colors duration-150"
        style={{
          borderColor: 'var(--border-subtle)',
          backgroundColor: 'var(--header-bg)'
        }}
      >
        <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-10 h-16 flex items-center justify-between gap-4">
          
          {/* Left: Brand / Logo */}
          <div className="flex items-center gap-3">
            <NavLink
              to="/dashboard"
              className="flex items-center gap-3 group select-none cursor-pointer"
            >
              <div
                className="w-9 h-9 rounded-lg flex items-center justify-center shadow-xs transition-transform group-hover:scale-105"
                style={{
                  backgroundColor: isDark ? 'var(--brand-primary)' : '#11151C',
                  color: '#FFFFFF'
                }}
              >
                <ShieldCheck className="w-5 h-5 text-white" />
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-1.5">
                  <span
                    className="text-base font-bold tracking-tight leading-none font-sans"
                    style={{ color: 'var(--text-main)' }}
                  >
                    StandIQ
                  </span>
                  <span
                    className="text-[9px] font-bold px-1.5 py-0.2 rounded border font-mono leading-tight"
                    style={{
                      backgroundColor: 'var(--brand-tint)',
                      color: 'var(--brand-primary)',
                      borderColor: 'var(--brand-tint-border)'
                    }}
                  >
                    v2.4
                  </span>
                </div>
                <span
                  className="text-[10px] font-medium leading-tight mt-0.5"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  ProcureIntel BIS Engine
                </span>
              </div>
            </NavLink>
          </div>

          {/* Center / Right Utility: Search + Theme Toggle + Alerts + Officer Info */}
          <div className="flex items-center gap-2.5 sm:gap-3.5">
            
            {/* Search Input Box */}
            <form onSubmit={handleSearchSubmit} className="relative hidden md:block w-72 lg:w-80">
              <Search
                className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 transition-colors"
                style={{ color: 'var(--text-muted)' }}
              />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search standards (e.g. IS 10322)..."
                className="w-full rounded-lg pl-9 pr-3 py-1.5 text-xs focus:outline-none transition-colors duration-150"
                style={{
                  backgroundColor: 'var(--input-bg)',
                  borderColor: 'var(--input-border)',
                  borderWidth: '1px',
                  color: 'var(--text-main)'
                }}
              />
            </form>

            {/* Notification Bell */}
            <button
              type="button"
              onClick={() => alert('No new notifications.')}
              className="p-2 rounded-lg relative transition-colors duration-150 cursor-pointer"
              style={{
                color: 'var(--text-secondary)'
              }}
              title="System Notifications & Alerts"
            >
              <Bell className="w-4 h-4" />
              <span
                className="w-2 h-2 rounded-full absolute top-1.5 right-1.5 ring-2"
                style={{
                  backgroundColor: 'var(--brand-primary)',
                  borderColor: 'var(--header-bg)'
                }}
              />
            </button>

            {/* Theme Toggle Icon Button (Compact: Moon in Light, Sun in Dark) */}
            <button
              type="button"
              onClick={toggleTheme}
              className="p-2 rounded-lg transition-colors duration-150 cursor-pointer flex items-center justify-center"
              style={{
                color: 'var(--text-secondary)',
                backgroundColor: 'transparent'
              }}
              title={isDark ? "Switch to light mode" : "Switch to dark mode"}
              aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
            >
              {isDark ? (
                <Sun className="w-4 h-4 text-amber-400 hover:text-amber-300 transition-colors" />
              ) : (
                <Moon className="w-4 h-4 text-[#667085] hover:text-[#17202A] transition-colors" />
              )}
            </button>

            {/* Government Officer Profile Pill */}
            <div className="relative">
              <button
                type="button"
                onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
                className="flex items-center gap-2.5 p-1.5 pl-2.5 rounded-lg border transition-colors duration-150 cursor-pointer text-left"
                style={{
                  backgroundColor: 'var(--bg-surface)',
                  borderColor: 'var(--border-subtle)'
                }}
              >
                <div
                  className="w-7 h-7 rounded-full border font-bold text-xs flex items-center justify-center shrink-0"
                  style={{
                    backgroundColor: 'var(--brand-tint)',
                    borderColor: 'var(--brand-tint-border)',
                    color: 'var(--brand-primary)'
                  }}
                >
                  PO
                </div>
                <div className="hidden sm:block text-left pr-1">
                  <p
                    className="text-xs font-semibold leading-tight"
                    style={{ color: 'var(--text-main)' }}
                  >
                    Government Officer
                  </p>
                  <p
                    className="text-[10px] font-mono leading-tight font-medium"
                    style={{ color: 'var(--brand-primary)' }}
                  >
                    BIS Verified
                  </p>
                </div>
                <ChevronDown
                  className="w-3.5 h-3.5 hidden sm:block"
                  style={{ color: 'var(--text-muted)' }}
                />
              </button>

              {/* Profile / Settings Dropdown */}
              {profileDropdownOpen && (
                <div
                  className="absolute right-0 mt-2 w-56 border rounded-xl shadow-lg py-1.5 z-50 animate-fade-in text-xs"
                  style={{
                    backgroundColor: 'var(--bg-surface)',
                    borderColor: 'var(--border-subtle)'
                  }}
                >
                  <div
                    className="px-3.5 py-2.5 border-b"
                    style={{
                      backgroundColor: 'var(--bg-surface-secondary)',
                      borderColor: 'var(--border-subtle)'
                    }}
                  >
                    <p className="font-semibold" style={{ color: 'var(--text-main)' }}>Procurement Authority</p>
                    <p className="text-[10px]" style={{ color: 'var(--text-secondary)' }}>Public Works Dept / MoHUA</p>
                  </div>

                  {/* Theme Switcher inside Dropdown */}
                  <button
                    onClick={() => {
                      toggleTheme();
                      setProfileDropdownOpen(false);
                    }}
                    className="w-full px-3.5 py-2 text-left flex items-center justify-between cursor-pointer font-medium hover:opacity-80 transition-opacity"
                    style={{ color: 'var(--text-main)' }}
                  >
                    <span className="flex items-center gap-2">
                      {isDark ? <Sun className="w-3.5 h-3.5 text-amber-400" /> : <Moon className="w-3.5 h-3.5 text-[#667085]" />}
                      <span>Theme: {isDark ? 'Dark Mode' : 'Light Mode'}</span>
                    </span>
                    <span className="text-[10px] font-mono uppercase" style={{ color: 'var(--text-muted)' }}>
                      {isDark ? 'Dark' : 'Light'}
                    </span>
                  </button>

                  <button
                    onClick={() => {
                      navigate('/app/settings');
                      setProfileDropdownOpen(false);
                    }}
                    className="w-full px-3.5 py-2 text-left flex items-center gap-2 cursor-pointer font-medium hover:opacity-80 transition-opacity"
                    style={{ color: 'var(--text-main)' }}
                  >
                    <Settings className="w-3.5 h-3.5" style={{ color: 'var(--text-secondary)' }} />
                    <span>System Settings &amp; API Keys</span>
                  </button>
                  <button
                    onClick={() => {
                      navigate('/');
                      setProfileDropdownOpen(false);
                    }}
                    className="w-full px-3.5 py-2 text-left flex items-center gap-2 cursor-pointer font-medium hover:opacity-80 transition-opacity"
                    style={{ color: 'var(--text-main)' }}
                  >
                    <ExternalLink className="w-3.5 h-3.5" style={{ color: 'var(--text-secondary)' }} />
                    <span>StandIQ Landing Page</span>
                  </button>
                </div>
              )}
            </div>

            {/* Mobile Hamburger Menu Button */}
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg"
              style={{ color: 'var(--text-secondary)' }}
              aria-label="Toggle Navigation Menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>

          </div>

        </div>
      </div>

      {/* ═════════════════════════════════════════════════════════════
          ROW 2: Spacious Clean Primary Navigation
      ═════════════════════════════════════════════════════════════ */}
      <div
        className="hidden md:block transition-colors duration-150"
        style={{ backgroundColor: 'var(--header-bg)' }}
      >
        <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-10 flex items-center justify-between">
          
          {/* Main Nav Items with Generous Whitespace */}
          <nav className="flex items-center gap-7 lg:gap-8">
            {navItems.map((item) => {
              const active = isNavActive(item);
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className="flex items-center gap-2 py-3 text-xs tracking-tight transition-all relative font-sans"
                  style={{
                    color: active ? 'var(--brand-primary)' : 'var(--text-secondary)',
                    fontWeight: active ? 700 : 600
                  }}
                >
                  <Icon
                    className="w-3.5 h-3.5"
                    style={{ color: active ? 'var(--brand-primary)' : 'var(--text-secondary)' }}
                  />
                  <span>{item.name}</span>

                  {/* Active Indicator Underline */}
                  {active && (
                    <span
                      className="absolute bottom-0 left-0 right-0 h-[2px] rounded-t-full"
                      style={{ backgroundColor: 'var(--brand-primary)' }}
                    />
                  )}
                </NavLink>
              );
            })}
          </nav>

          {/* Right Side Status & Settings Link */}
          <div className="flex items-center gap-4 text-xs">
            <div
              className="hidden xl:flex items-center gap-1.5 text-[11px] font-mono"
              style={{ color: 'var(--text-secondary)' }}
            >
              <span
                className="w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: 'var(--brand-primary)' }}
              />
              <span>BIS Act 2016 &amp; QCO Repository Active</span>
            </div>

            <NavLink
              to="/settings"
              className="flex items-center gap-1.5 py-3 text-xs font-semibold transition-colors"
              style={({ isActive }) => ({
                color: isActive ? 'var(--brand-primary)' : 'var(--text-secondary)'
              })}
            >
              <Settings className="w-3.5 h-3.5" />
              <span>Settings</span>
            </NavLink>
          </div>

        </div>
      </div>

      {/* ═════════════════════════════════════════════════════════════
          MOBILE MENU DRAWER
      ═════════════════════════════════════════════════════════════ */}
      {mobileMenuOpen && (
        <div
          className="md:hidden border-b px-4 py-4 space-y-3 animate-fade-in shadow-md"
          style={{
            backgroundColor: 'var(--bg-surface)',
            borderColor: 'var(--border-subtle)'
          }}
        >
          
          {/* Mobile Search */}
          <form onSubmit={handleSearchSubmit} className="relative w-full">
            <Search
              className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2"
              style={{ color: 'var(--text-muted)' }}
            />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search standards (e.g. IS 10322)..."
              className="w-full rounded-lg pl-9 pr-3 py-2 text-xs focus:outline-none"
              style={{
                backgroundColor: 'var(--input-bg)',
                borderColor: 'var(--input-border)',
                borderWidth: '1px',
                color: 'var(--text-main)'
              }}
            />
          </form>

          {/* Mobile Navigation Links */}
          <div className="space-y-1 pt-1">
            {navItems.map((item) => {
              const active = isNavActive(item);
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition-colors"
                  style={{
                    backgroundColor: active ? 'var(--brand-tint)' : 'transparent',
                    color: active ? 'var(--brand-primary)' : 'var(--text-secondary)',
                    fontWeight: active ? 700 : 600
                  }}
                >
                  <Icon
                    className="w-4 h-4"
                    style={{ color: active ? 'var(--brand-primary)' : 'var(--text-secondary)' }}
                  />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}

            {/* Mobile Theme Toggle Item */}
            <button
              type="button"
              onClick={() => {
                toggleTheme();
                setMobileMenuOpen(false);
              }}
              className="w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold cursor-pointer"
              style={{ color: 'var(--text-secondary)' }}
            >
              <span className="flex items-center gap-3">
                {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-[#667085]" />}
                <span>Theme</span>
              </span>
              <span
                className="text-[10px] font-mono uppercase px-2 py-0.5 rounded border"
                style={{
                  backgroundColor: 'var(--brand-tint)',
                  borderColor: 'var(--brand-tint-border)',
                  color: 'var(--brand-primary)'
                }}
              >
                {isDark ? 'Dark Mode' : 'Light Mode'}
              </span>
            </button>

            <NavLink
              to="/settings"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold"
              style={{ color: 'var(--text-secondary)' }}
            >
              <Settings className="w-4 h-4" />
              <span>Settings</span>
            </NavLink>

            <NavLink
              to="/"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold"
              style={{ color: 'var(--text-secondary)' }}
            >
              <ExternalLink className="w-4 h-4" />
              <span>Landing Page</span>
            </NavLink>
          </div>

        </div>
      )}

    </header>
  );
}
