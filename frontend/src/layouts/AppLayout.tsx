import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useSocket } from '../context/SocketContext';
import { DemoBanner } from '../components/common/States';
import { AlertNotification } from '../components/parent/AlertNotification';
import {
  Shield,
  ShieldCheck,
  MessageSquare,
  Users,
  AlertTriangle,
  BarChart3,
  TrendingUp,
  FileText,
  Settings,
  User as UserIcon,
  LogOut,
  Menu,
  X,
  Wifi,
  WifiOff,
  Code2,
} from 'lucide-react';
import clsx from 'clsx';

export const AppLayout: React.FC = () => {
  const { user, logout, isChild, isParent, isContact } = useAuth();
  const { connectionState } = useSocket();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Nav links per role
  const childLinks = [
    { to: '/child', label: 'Conversations', icon: <MessageSquare className="w-4 h-4" /> },
    { to: '/child/contacts', label: 'My Contacts', icon: <Users className="w-4 h-4" /> },
    { to: '/child/safety', label: 'Safety Status', icon: <ShieldCheck className="w-4 h-4" /> },
    { to: '/child/profile', label: 'Profile', icon: <UserIcon className="w-4 h-4" /> },
  ];

  const parentLinks = [
    { to: '/parent', label: 'Overview', icon: <BarChart3 className="w-4 h-4" /> },
    { to: '/parent/conversations', label: 'Conversations', icon: <MessageSquare className="w-4 h-4" /> },
    { to: '/parent/alerts', label: 'Alert Center', icon: <AlertTriangle className="w-4 h-4" /> },
    { to: '/parent/trends', label: 'Behaviour Trends', icon: <TrendingUp className="w-4 h-4" /> },
    { to: '/parent/reports', label: 'Safety Reports', icon: <FileText className="w-4 h-4" /> },
    { to: '/parent/settings', label: 'Monitoring Settings', icon: <Settings className="w-4 h-4" /> },
    { to: '/parent/profile', label: 'Profile', icon: <UserIcon className="w-4 h-4" /> },
    { to: '/dev', label: 'Dev Panel', icon: <Code2 className="w-4 h-4" /> },
  ];

  const contactLinks = [
    { to: '/contact', label: 'My Conversations', icon: <MessageSquare className="w-4 h-4" /> },
    { to: '/contact/profile', label: 'Profile', icon: <UserIcon className="w-4 h-4" /> },
  ];

  const currentLinks = isParent ? parentLinks : isChild ? childLinks : contactLinks;

  const roleBadge = () => {
    if (isParent) return { label: 'PARENT', color: 'bg-purple-500/20 text-purple-300 border-purple-500/30' };
    if (isChild) return { label: 'CHILD', color: 'bg-blue-500/20 text-cyan-300 border-cyan-500/30' };
    return { label: 'CONTACT', color: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' };
  };

  const badge = roleBadge();

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-100 flex flex-col font-sans">
      <DemoBanner />
      <AlertNotification />

      <div className="flex-1 flex overflow-hidden">
        {/* Desktop Sidebar */}
        <aside className="hidden md:flex flex-col w-64 bg-[#0d0d15]/90 border-r border-white/10 p-4 justify-between backdrop-blur-xl">
          <div className="space-y-6">
            {/* Brand Logo */}
            <div className="flex items-center gap-3 px-2 py-1">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-[0_0_15px_rgba(0,168,255,0.3)]">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xs font-bold tracking-wider uppercase text-white font-mono leading-none">
                  CHILD-SAFE
                </h1>
                <span className="text-[10px] text-slate-400 font-mono tracking-tight">AI ENVIRONMENT</span>
              </div>
            </div>

            {/* User role card */}
            <div className="glass-card p-3 bg-white/[0.02] border-white/5 flex items-center justify-between">
              <div className="flex items-center gap-2.5 overflow-hidden">
                <div className="w-8 h-8 rounded-full bg-slate-800 border border-white/10 flex items-center justify-center font-bold text-xs text-cyan-300 shrink-0">
                  {user?.name?.charAt(0).toUpperCase()}
                </div>
                <div className="overflow-hidden">
                  <p className="text-xs font-medium text-slate-200 truncate">{user?.name}</p>
                  <p className="text-[10px] text-slate-500 truncate">{user?.email}</p>
                </div>
              </div>
              <span className={clsx('text-[9px] font-mono px-2 py-0.5 rounded-full border', badge.color)}>
                {badge.label}
              </span>
            </div>

            {/* Navigation Links */}
            <nav className="space-y-1">
              {currentLinks.map((link) => {
                const isActive = location.pathname === link.to;
                return (
                  <NavLink
                    key={link.to}
                    to={link.to}
                    className={clsx(
                      'flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all duration-200',
                      isActive
                        ? 'bg-gradient-to-r from-blue-600/30 to-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-[0_0_12px_rgba(0,168,255,0.15)] font-semibold'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                    )}
                  >
                    {link.icon}
                    <span>{link.label}</span>
                  </NavLink>
                );
              })}
            </nav>
          </div>

          {/* Footer & Connection Status */}
          <div className="space-y-3 pt-4 border-t border-white/10">
            {/* Live Connection state */}
            <div className="flex items-center justify-between px-2 text-[11px] font-mono text-slate-400">
              <span className="flex items-center gap-1.5">
                {connectionState === 'connected' ? (
                  <>
                    <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(0,230,118,0.6)]" />
                    <span>Socket Active</span>
                  </>
                ) : (
                  <>
                    <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                    <span className="capitalize">{connectionState}</span>
                  </>
                )}
              </span>
              {connectionState === 'connected' ? (
                <Wifi className="w-3.5 h-3.5 text-emerald-400" />
              ) : (
                <WifiOff className="w-3.5 h-3.5 text-amber-400" />
              )}
            </div>

            <button
              onClick={handleLogout}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-red-400 hover:bg-red-500/10 border border-transparent hover:border-red-500/20 transition-all cursor-pointer"
            >
              <LogOut className="w-4 h-4" />
              <span>Sign Out</span>
            </button>
          </div>
        </aside>

        {/* Mobile Header & Content */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          {/* Top Bar on Mobile */}
          <header className="md:hidden flex items-center justify-between px-4 py-3 bg-[#0d0d15] border-b border-white/10">
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-cyan-400" />
              <span className="font-bold text-xs tracking-wider text-white font-mono">CHILD-SAFE</span>
            </div>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-1.5 rounded-lg bg-white/5 text-slate-300"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </header>

          {/* Mobile dropdown menu */}
          {mobileMenuOpen && (
            <div className="md:hidden bg-[#0d0d15] border-b border-white/10 p-4 space-y-2 z-50">
              {currentLinks.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium text-slate-300 hover:bg-white/5"
                >
                  {link.icon}
                  <span>{link.label}</span>
                </NavLink>
              ))}
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-3 px-3 py-2 text-xs font-medium text-red-400 hover:bg-red-500/10 rounded-lg text-left"
              >
                <LogOut className="w-4 h-4" />
                <span>Sign Out</span>
              </button>
            </div>
          )}

          {/* Main View Area */}
          <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 cyber-bg">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
};
