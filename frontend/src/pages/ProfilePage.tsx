import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { GlassCard } from '../components/common/GlassCard';
import { User, Mail, Shield, Lock, Check } from 'lucide-react';

export const ProfilePage: React.FC = () => {
  const { user } = useAuth();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [success, setSuccess] = useState(false);

  const handlePasswordChange = (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword && newPassword === confirmPassword) {
      setSuccess(true);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      setTimeout(() => setSuccess(false), 3000);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="pb-3 border-b border-white/10">
        <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
          User Account Profile
        </h1>
        <p className="text-xs text-slate-400">
          Manage your account credentials and system identity.
        </p>
      </div>

      {/* User Information Card */}
      <GlassCard glow="blue" className="p-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center font-bold text-2xl text-white shadow-lg">
            {user?.name?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">{user?.name}</h2>
            <div className="flex items-center gap-2 mt-1">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold bg-cyan-500/10 border border-cyan-500/30 text-cyan-300">
                {user?.role}
              </span>
              <span className="text-slate-500 text-xs">•</span>
              <span className="text-xs font-mono text-slate-400">ID: {user?._id}</span>
            </div>
          </div>
        </div>

        <div className="space-y-3 pt-4 border-t border-white/10 text-xs">
          <div className="flex items-center justify-between py-2 border-b border-white/5">
            <span className="text-slate-400 flex items-center gap-2">
              <Mail className="w-4 h-4 text-slate-500" />
              <span>Email Address</span>
            </span>
            <span className="font-mono text-slate-200">{user?.email}</span>
          </div>

          <div className="flex items-center justify-between py-2 border-b border-white/5">
            <span className="text-slate-400 flex items-center gap-2">
              <Shield className="w-4 h-4 text-slate-500" />
              <span>Access Level</span>
            </span>
            <span className="font-mono text-slate-200 uppercase">{user?.role} ACCESS</span>
          </div>

          <div className="flex items-center justify-between py-2">
            <span className="text-slate-400 flex items-center gap-2">
              <User className="w-4 h-4 text-slate-500" />
              <span>Current Status</span>
            </span>
            <span className="inline-flex items-center gap-1.5 text-emerald-400 font-mono">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              <span>Authenticated</span>
            </span>
          </div>
        </div>
      </GlassCard>

      {/* Change Password Form */}
      <GlassCard className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <Lock className="w-4 h-4 text-cyan-400" />
          <h2 className="text-sm font-semibold text-white">Security & Password</h2>
        </div>

        {success && (
          <div className="p-3 mb-4 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2 font-mono">
            <Check className="w-4 h-4" />
            <span>Password updated successfully.</span>
          </div>
        )}

        <form onSubmit={handlePasswordChange} className="space-y-3">
          <div>
            <label className="block text-xs text-slate-400 mb-1">Current Password</label>
            <input
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full glass-input rounded-xl px-3 py-2 text-xs text-white"
            />
          </div>

          <div>
            <label className="block text-xs text-slate-400 mb-1">New Password</label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full glass-input rounded-xl px-3 py-2 text-xs text-white"
            />
          </div>

          <div>
            <label className="block text-xs text-slate-400 mb-1">Confirm New Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full glass-input rounded-xl px-3 py-2 text-xs text-white"
            />
          </div>

          <button
            type="submit"
            className="mt-2 px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold text-slate-200 transition-colors cursor-pointer"
          >
            Update Password
          </button>
        </form>
      </GlassCard>
    </div>
  );
};
