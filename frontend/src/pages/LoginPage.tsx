import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Shield, Lock, Mail, ArrowRight, AlertCircle, Eye, EyeOff } from 'lucide-react';
import { GlassCard } from '../components/common/GlassCard';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, selectedRoleForLogin, setSelectedRoleForLogin } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('demo123');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please provide both email and password.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const user = await login(email, password);
      // Route by user role
      if (user.role === 'PARENT') navigate('/parent');
      else if (user.role === 'CHILD') navigate('/child');
      else navigate('/contact');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = (demoEmail: string) => {
    setEmail(demoEmail);
    setPassword('demo123');
    setError(null);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-100 flex flex-col justify-center items-center p-6 cyber-bg">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center mx-auto mb-3 shadow-[0_0_20px_rgba(0,168,255,0.3)]">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white mb-1">
            System Sign In
          </h1>
          <p className="text-xs text-slate-400">
            Access the Child-Safe Digital Environment
          </p>

          {selectedRoleForLogin && (
            <div className="mt-3 inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-mono">
              <span>Signing in as: {selectedRoleForLogin}</span>
              <button
                onClick={() => setSelectedRoleForLogin(null)}
                className="text-[10px] underline text-slate-400 hover:text-white"
              >
                Change
              </button>
            </div>
          )}
        </div>

        {/* Login Form */}
        <GlassCard glow="blue" className="p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
                <span>{error}</span>
              </div>
            )}

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="user@example.com"
                  required
                  className="w-full glass-input rounded-xl pl-9 pr-4 py-2.5 text-xs text-slate-100 placeholder:text-slate-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full glass-input rounded-xl pl-9 pr-10 py-2.5 text-xs text-slate-100 placeholder:text-slate-500"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-2.5 text-slate-400 hover:text-cyan-400 transition-colors cursor-pointer"
                  title={showPassword ? 'Hide password' : 'Show password'}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-semibold text-xs transition-all shadow-[0_0_15px_rgba(0,168,255,0.3)] disabled:opacity-50 cursor-pointer"
            >
              <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Quick Demo Logins Helper */}
          <div className="mt-6 pt-5 border-t border-white/10">
            <p className="text-[11px] font-mono text-slate-400 text-center mb-2.5 uppercase tracking-wider">
              1-Click Demo Testing Credentials
            </p>
            <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
              <button
                type="button"
                onClick={() => fillDemo('parent@example.com')}
                className="p-2 rounded-lg bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 text-purple-300 transition-colors text-left"
              >
                Parent Account
              </button>
              <button
                type="button"
                onClick={() => fillDemo('child@example.com')}
                className="p-2 rounded-lg bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/30 text-cyan-300 transition-colors text-left"
              >
                Child Account
              </button>
              <button
                type="button"
                onClick={() => fillDemo('alice@example.com')}
                className="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 transition-colors text-left"
              >
                Contact: Alice
              </button>
              <button
                type="button"
                onClick={() => fillDemo('bob@example.com')}
                className="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 transition-colors text-left"
              >
                Contact: Bob
              </button>
              <button
                type="button"
                onClick={() => fillDemo('charlie@example.com')}
                className="p-2 rounded-lg bg-orange-500/10 hover:bg-orange-500/20 border border-orange-500/30 text-orange-300 transition-colors text-left"
              >
                Contact: Charlie
              </button>
              <button
                type="button"
                onClick={() => fillDemo('david@example.com')}
                className="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 transition-colors text-left"
              >
                Contact: David
              </button>
            </div>
          </div>
        </GlassCard>

        {/* Link to Register */}
        <p className="text-center text-xs text-slate-500 mt-6">
          Need an account?{' '}
          <Link to="/register" className="text-cyan-400 hover:underline">
            Register new account
          </Link>
        </p>
      </div>
    </div>
  );
};
