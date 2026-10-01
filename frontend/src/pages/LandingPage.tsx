import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Shield,
  Lock,
  Cpu,
  Eye,
  Activity,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Users,
} from 'lucide-react';
import { GlassCard } from '../components/common/GlassCard';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-100 flex flex-col cyber-bg selection:bg-cyan-500 selection:text-black">
      {/* Top Navigation */}
      <header className="px-6 py-5 flex items-center justify-between border-b border-white/5 backdrop-blur-md sticky top-0 z-40 bg-[#0a0a0f]/80">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-[0_0_20px_rgba(0,168,255,0.4)]">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-widest uppercase text-white font-mono leading-none">
              CHILD-SAFE
            </h1>
            <span className="text-[10px] text-cyan-400 font-mono tracking-wider">AI ENVIRONMENT</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/select-role')}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/5 border border-white/10 transition-all cursor-pointer"
          >
            Role Selection
          </button>
          <button
            onClick={() => navigate('/login')}
            className="px-5 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white shadow-[0_0_15px_rgba(0,168,255,0.3)] transition-all cursor-pointer"
          >
            Login
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center text-center px-6 py-16 md:py-24 max-w-5xl mx-auto">
        {/* Security Tag */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-mono mb-8 shadow-[0_0_15px_rgba(0,168,255,0.15)]">
          <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
          <span>MULTI-LAYER CONVERSATIONAL RISK MONITORING</span>
        </div>

        {/* Title */}
        <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white max-w-4xl leading-tight mb-6">
          CHILD-SAFE DIGITAL <br />
          <span className="text-gradient-cyan">ENVIRONMENT MANAGER</span>
        </h1>

        {/* Subtitle */}
        <p className="text-base sm:text-lg text-slate-300 font-medium max-w-2xl mb-4 leading-relaxed">
          Privacy-first intelligent protection for safer digital conversations.
        </p>

        {/* Supporting text */}
        <p className="text-xs sm:text-sm text-slate-400 max-w-2xl mb-10 leading-relaxed">
          Analyze peer communication for meaningful child safety risks using contextual AI, behavioral
          trend tracking, and privacy-preserving multi-layer risk fusion. False positive protected.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 mb-16">
          <button
            onClick={() => navigate('/select-role')}
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-400 hover:from-blue-500 hover:to-cyan-300 text-slate-950 shadow-[0_0_25px_rgba(0,168,255,0.4)] transition-all transform hover:-translate-y-0.5 cursor-pointer"
          >
            <span>Get Started</span>
            <ArrowRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => navigate('/login')}
            className="px-6 py-3 rounded-xl text-sm font-semibold text-slate-200 hover:text-white bg-slate-900/80 hover:bg-slate-800/80 border border-white/10 transition-all cursor-pointer"
          >
            Access Dashboard
          </button>
        </div>

        {/* Futuristic Abstract Visualization (Requirement #3) */}
        <div className="w-full max-w-3xl mb-16">
          <div className="glass-card p-6 md:p-8 border-cyan-500/20 shadow-[0_0_30px_rgba(0,168,255,0.1)] relative">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
              {/* Node 1: Child */}
              <div className="flex flex-col items-center p-4 rounded-xl bg-slate-900/60 border border-white/5">
                <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 mb-2 shadow-[0_0_15px_rgba(0,168,255,0.2)]">
                  <Users className="w-6 h-6" />
                </div>
                <span className="text-xs font-semibold text-slate-200">Child Account</span>
                <span className="text-[10px] text-slate-500 font-mono">Live Messaging</span>
              </div>

              {/* Node 2: Secure Channel */}
              <div className="flex flex-col items-center p-4 rounded-xl bg-slate-900/60 border border-white/5">
                <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 mb-2 shadow-[0_0_15px_rgba(0,229,255,0.2)]">
                  <Lock className="w-6 h-6" />
                </div>
                <span className="text-xs font-semibold text-slate-200">Secure Channel</span>
                <span className="text-[10px] text-slate-500 font-mono">Conversation ID</span>
              </div>

              {/* Node 3: AI Engine */}
              <div className="flex flex-col items-center p-4 rounded-xl bg-slate-900/60 border border-purple-500/30">
                <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/40 flex items-center justify-center text-purple-400 mb-2 shadow-[0_0_15px_rgba(124,58,237,0.2)]">
                  <Cpu className="w-6 h-6" />
                </div>
                <span className="text-xs font-semibold text-slate-200">AI Risk Engine</span>
                <span className="text-[10px] text-purple-300 font-mono">4-Layer Analysis</span>
              </div>

              {/* Node 4: Parent Protection */}
              <div className="flex flex-col items-center p-4 rounded-xl bg-slate-900/60 border border-white/5">
                <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-2 shadow-[0_0_15px_rgba(0,230,118,0.2)]">
                  <ShieldCheck className="w-6 h-6" />
                </div>
                <span className="text-xs font-semibold text-slate-200">Parent Dashboard</span>
                <span className="text-[10px] text-emerald-400 font-mono">Privacy-First Alerts</span>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-white/5 flex flex-wrap items-center justify-between text-xs text-slate-400">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>False-positive mitigation (e.g. movie & sports slang protected)</span>
              </span>
              <span className="font-mono text-cyan-400 text-[11px]">WebSocket Latency &lt; 20ms</span>
            </div>
          </div>
        </div>

        {/* Feature Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full text-left">
          <GlassCard hover glow="blue">
            <div className="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-cyan-400 mb-4">
              <Activity className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-semibold text-white mb-2">Contextual Multi-Layer AI</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Combines fast pattern rules, trained TF-IDF & Logistic Regression ML classifier, conversation history,
              and behavioural trends. Not a simplistic single-word detector.
            </p>
          </GlassCard>

          <GlassCard hover glow="purple">
            <div className="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 mb-4">
              <Eye className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-semibold text-white mb-2">Privacy-First Architecture</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              The parent dashboard summarizes risk scores, severities, and explainable safety reasons without
              unnecessarily exposing the raw private message stream.
            </p>
          </GlassCard>

          <GlassCard hover glow="green">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-4">
              <Lock className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-semibold text-white mb-2">Multi-Computer Real-Time Chat</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Child and friends (Alice, Bob, Charlie, David) log in independently across different computers
              using isolated conversation IDs and WebSocket sessions.
            </p>
          </GlassCard>
        </div>
      </main>

      {/* Footer (Requirements #72) */}
      <footer className="py-8 border-t border-white/5 text-center text-xs text-slate-500 backdrop-blur-md">
        <p className="font-semibold text-slate-400 mb-1">
          "Understand the conversation. Detect the risk. Protect the child."
        </p>
        <p className="text-[11px] text-slate-600 font-mono">
          Child-Safe Digital Environment Manager — Academic Major Project
        </p>
      </footer>
    </div>
  );
};
