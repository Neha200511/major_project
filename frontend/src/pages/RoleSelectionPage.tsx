import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { UserRole } from '../types';
import { Shield, ShieldCheck, Users, ArrowRight } from 'lucide-react';
import { GlassCard } from '../components/common/GlassCard';

export const RoleSelectionPage: React.FC = () => {
  const navigate = useNavigate();
  const { setSelectedRoleForLogin } = useAuth();

  const handleSelectRole = (role: UserRole) => {
    setSelectedRoleForLogin(role);
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-100 flex flex-col justify-center items-center p-6 cyber-bg">
      <div className="max-w-4xl w-full text-center space-y-4 mb-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-mono mb-2">
          <Shield className="w-3.5 h-3.5" />
          <span>AUTHENTICATION GATEWAY</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white">
          Who are you?
        </h1>
        <p className="text-sm text-slate-400 max-w-lg mx-auto">
          Select your account role to access the dedicated interface and security profile.
        </p>
      </div>

      {/* Role Selection Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl w-full">
        {/* Card 1: CHILD */}
        <GlassCard hover glow="blue" className="flex flex-col justify-between text-left p-6">
          <div>
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-cyan-400 mb-5 shadow-[0_0_15px_rgba(0,168,255,0.2)]">
              <Shield className="w-6 h-6" />
            </div>
            <h2 className="text-lg font-bold text-white mb-2">CHILD</h2>
            <p className="text-xs text-slate-400 leading-relaxed mb-6">
              Access your conversations and communicate with verified contacts in a controlled, safe environment.
            </p>
          </div>
          <button
            onClick={() => handleSelectRole('CHILD')}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition-colors shadow-lg cursor-pointer"
          >
            <span>Continue as Child</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </GlassCard>

        {/* Card 2: PARENT */}
        <GlassCard hover glow="purple" className="flex flex-col justify-between text-left p-6">
          <div>
            <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 mb-5 shadow-[0_0_15px_rgba(124,58,237,0.2)]">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h2 className="text-lg font-bold text-white mb-2">PARENT</h2>
            <p className="text-xs text-slate-400 leading-relaxed mb-6">
              Monitor your child's digital safety, review behavioral trends, and receive explainable risk alerts.
            </p>
          </div>
          <button
            onClick={() => handleSelectRole('PARENT')}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs transition-colors shadow-lg cursor-pointer"
          >
            <span>Continue as Parent</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </GlassCard>

        {/* Card 3: CONTACT */}
        <GlassCard hover glow="green" className="flex flex-col justify-between text-left p-6">
          <div>
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-5 shadow-[0_0_15px_rgba(0,230,118,0.2)]">
              <Users className="w-6 h-6" />
            </div>
            <h2 className="text-lg font-bold text-white mb-2">CONTACT / FRIEND</h2>
            <p className="text-xs text-slate-400 leading-relaxed mb-6">
              Communicate with the child through the secure test environment from separate client computers.
            </p>
          </div>
          <button
            onClick={() => handleSelectRole('CONTACT')}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-colors shadow-lg cursor-pointer"
          >
            <span>Continue as Contact</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </GlassCard>
      </div>

      <div className="mt-12 text-center">
        <button
          onClick={() => navigate('/')}
          className="text-xs text-slate-500 hover:text-slate-300 transition-colors"
        >
          ← Return to Overview
        </button>
      </div>
    </div>
  );
};
