import React from 'react';
import { ShieldCheck, Lock, HeartHandshake, EyeOff, CheckCircle } from 'lucide-react';
import { GlassCard } from '../../components/common/GlassCard';

export const SafetyStatus: React.FC = () => {
  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="p-6 glass-card border-emerald-500/20 shadow-[0_0_25px_rgba(0,230,118,0.1)] text-center">
        <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mx-auto mb-4 shadow-[0_0_20px_rgba(0,230,118,0.25)]">
          <ShieldCheck className="w-8 h-8" />
        </div>
        <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight mb-2">
          Your Account is Protected
        </h1>
        <p className="text-xs sm:text-sm text-slate-300 max-w-md mx-auto leading-relaxed">
          You are using a controlled, safe environment designed to ensure digital conversations remain friendly, respectful, and secure.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <GlassCard glow="green" className="p-5">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 shrink-0">
              <Lock className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white mb-1">Encrypted Transit</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Messages between you and your verified contacts are delivered through secure authenticated channels.
              </p>
            </div>
          </div>
        </GlassCard>

        <GlassCard glow="blue" className="p-5">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-lg bg-blue-500/10 text-cyan-400 shrink-0">
              <EyeOff className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white mb-1">Privacy Preserving</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Our safety platform is privacy-first, protecting your personal data and preventing unauthorized access.
              </p>
            </div>
          </div>
        </GlassCard>
      </div>

      <GlassCard className="p-5">
        <h3 className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
          <HeartHandshake className="w-4 h-4 text-cyan-400" />
          <span>Community Guidelines for Digital Well-Being</span>
        </h3>
        <ul className="space-y-2 text-xs text-slate-300">
          <li className="flex items-center gap-2">
            <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span>Never share passwords, home address, or personal identifying information.</span>
          </li>
          <li className="flex items-center gap-2">
            <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span>Be respectful and supportive in all interactions with friends.</span>
          </li>
          <li className="flex items-center gap-2">
            <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span>If any message makes you uncomfortable, inform a parent or trusted adult immediately.</span>
          </li>
        </ul>
      </GlassCard>
    </div>
  );
};
