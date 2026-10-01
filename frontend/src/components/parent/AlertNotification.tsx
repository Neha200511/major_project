import React, { useEffect } from 'react';
import { useSocket } from '../../context/SocketContext';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, X, ShieldAlert, ArrowRight } from 'lucide-react';

export const AlertNotification: React.FC = () => {
  const { newParentAlert, dismissParentAlert } = useSocket();
  const navigate = useNavigate();

  useEffect(() => {
    if (newParentAlert) {
      const timer = setTimeout(() => {
        dismissParentAlert();
      }, 12000);
      return () => clearTimeout(timer);
    }
  }, [newParentAlert, dismissParentAlert]);

  if (!newParentAlert) return null;

  const isCritical = newParentAlert.severity === 'CRITICAL';

  return (
    <div className="fixed top-5 right-5 z-50 max-w-md w-full animate-slide-in">
      <div
        className={`glass-card p-4 border ${
          isCritical
            ? 'border-red-500/60 shadow-[0_0_25px_rgba(255,23,68,0.35)] bg-red-950/40'
            : 'border-orange-500/50 shadow-[0_0_20px_rgba(255,152,0,0.25)] bg-slate-900/90'
        } backdrop-blur-xl relative overflow-hidden`}
      >
        {/* Glow indicator line */}
        <div
          className={`absolute top-0 left-0 right-0 h-1 ${
            isCritical ? 'bg-red-500' : 'bg-orange-500'
          }`}
        />

        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <div
              className={`p-2 rounded-lg mt-0.5 ${
                isCritical ? 'bg-red-500/20 text-red-400' : 'bg-orange-500/20 text-orange-400'
              }`}
            >
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="font-bold text-xs tracking-wider uppercase text-slate-100 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-red-500 animate-ping inline-block" />
                  NEW {newParentAlert.severity} ALERT
                </span>
                <span className="text-[10px] text-slate-400 font-mono">
                  Risk: {newParentAlert.risk_score}%
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed mb-2">
                A potential safety concern was detected in the conversation with{' '}
                <strong className="text-white font-semibold">{newParentAlert.contact_name}</strong>.
              </p>
              {newParentAlert.categories && newParentAlert.categories.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mb-3">
                  {newParentAlert.categories.slice(0, 3).map((cat) => (
                    <span
                      key={cat}
                      className="px-2 py-0.5 rounded text-[10px] font-mono bg-white/5 border border-white/10 text-cyan-300"
                    >
                      {cat}
                    </span>
                  ))}
                </div>
              )}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    dismissParentAlert();
                    navigate(`/parent/risk/${newParentAlert.conversation_id}`);
                  }}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-semibold shadow-md transition-colors"
                >
                  <span>Review Analysis</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={dismissParentAlert}
                  className="px-2.5 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 text-xs font-medium transition-colors"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
          <button
            onClick={dismissParentAlert}
            className="text-slate-400 hover:text-white p-1 rounded-md transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
