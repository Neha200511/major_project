import React, { useState } from 'react';
import { GlassCard } from '../../components/common/GlassCard';
import { Settings, Shield, Bell, Clock, Sliders, Check } from 'lucide-react';

export const ParentSettings: React.FC = () => {
  const [sensitivity, setSensitivity] = useState<'low' | 'balanced' | 'high'>('balanced');
  const [threshold, setThreshold] = useState<number>(60);
  const [realtimeAlerts, setRealtimeAlerts] = useState<boolean>(true);
  const [cooldown, setCooldown] = useState<number>(30);
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="pb-4 border-b border-white/10">
        <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <Settings className="w-5 h-5 text-cyan-400" />
          <span>Parental Monitoring Settings</span>
        </h1>
        <p className="text-xs text-slate-400">
          Configure risk detection sensitivity, threshold bounds, and alert notification policies.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-5">
        {/* Risk Sensitivity */}
        <GlassCard className="p-5 space-y-4">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-semibold text-white">Detection Engine Sensitivity</h2>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Controls how aggressively pattern convergence and power dynamics trigger risk elevation.
          </p>
          <div className="grid grid-cols-3 gap-3 pt-1">
            {(['low', 'balanced', 'high'] as const).map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => setSensitivity(s)}
                className={`py-2 px-3 rounded-xl capitalize text-xs font-semibold border transition-all cursor-pointer ${
                  sensitivity === s
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 shadow-[0_0_12px_rgba(0,168,255,0.2)]'
                    : 'bg-white/[0.02] text-slate-400 border-white/10 hover:bg-white/[0.05]'
                }`}
              >
                {s} Mode
              </button>
            ))}
          </div>
        </GlassCard>

        {/* Severity Threshold */}
        <GlassCard className="p-5 space-y-4">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-semibold text-white">Parent Alert Severity Cutoff</h2>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Minimum composite risk index score required before triggering an immediate notification to the parent dashboard.
          </p>
          <div className="flex items-center gap-4">
            <input
              type="range"
              min="30"
              max="80"
              step="5"
              value={threshold}
              onChange={(e) => setThreshold(Number(e.target.value))}
              className="flex-1 accent-cyan-400 cursor-pointer"
            />
            <span className="font-mono font-bold text-sm text-cyan-300 px-3 py-1 rounded-lg bg-black/40 border border-white/10">
              {threshold}%
            </span>
          </div>
          <div className="flex justify-between text-[11px] text-slate-500 font-mono">
            <span>30% (Moderate)</span>
            <span>60% (High - Recommended)</span>
            <span>80% (Critical Only)</span>
          </div>
        </GlassCard>

        {/* Cooldown & Realtime */}
        <GlassCard className="p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bell className="w-4 h-4 text-cyan-400" />
              <div>
                <h3 className="text-sm font-semibold text-white">Real-Time WebSocket Push Alerts</h3>
                <p className="text-xs text-slate-400">Receive instant pop-up notifications when a peer channel is flagged</p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={realtimeAlerts}
                onChange={(e) => setRealtimeAlerts(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-500" />
            </label>
          </div>

          <div className="pt-3 border-t border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-cyan-400" />
              <div>
                <h3 className="text-sm font-semibold text-white">Alert Deduplication Cooldown</h3>
                <p className="text-xs text-slate-400">Suppresses repeated identical alerts for the same conversation</p>
              </div>
            </div>
            <div className="flex items-center gap-1.5 font-mono text-xs">
              <input
                type="number"
                value={cooldown}
                onChange={(e) => setCooldown(Number(e.target.value))}
                min="5"
                max="120"
                className="w-16 glass-input rounded-lg p-1.5 text-center text-white"
              />
              <span className="text-slate-400">mins</span>
            </div>
          </div>
        </GlassCard>

        {/* Submit */}
        <div className="flex items-center justify-between pt-2">
          {saved && (
            <span className="inline-flex items-center gap-1.5 text-xs text-emerald-400 font-mono">
              <Check className="w-4 h-4" />
              <span>Monitoring policies updated successfully.</span>
            </span>
          )}
          <button
            type="submit"
            className="ml-auto px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-semibold text-xs shadow-md transition-all cursor-pointer"
          >
            Apply Settings
          </button>
        </div>
      </form>
    </div>
  );
};
