import React, { useState } from 'react';
import { Shield, Lock, User, AlertCircle, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Login: React.FC = () => {
  const { login } = useAuth();
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('SentinelAdmin!2026Secure');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login(username, password);
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0F19] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Brand header */}
        <div className="text-center mb-8">
          <div className="inline-flex w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-500 items-center justify-center text-white shadow-xl shadow-blue-500/20 mb-4">
            <Shield className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">SentinelEDR</h1>
          <p className="mt-1 text-xs text-slate-400">Endpoint Detection & Threat Response Console</p>
        </div>

        {/* Login Card */}
        <div className="bg-[#111827] border border-slate-800 rounded-2xl p-8 shadow-2xl backdrop-blur-xl">
          <h2 className="text-lg font-semibold text-slate-100 mb-6">Analyst Sign In</h2>

          {error && (
            <div className="mb-6 p-3.5 rounded-xl bg-red-500/10 border border-red-500/20 flex items-start gap-3 text-red-400 text-xs">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Username</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <User className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-900 border border-slate-700/80 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
                  placeholder="analyst_username"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-900 border border-slate-700/80 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
                  placeholder="••••••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold shadow-lg shadow-blue-600/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>{loading ? 'Authenticating...' : 'Sign In to Console'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Educational credential helper */}
          <div className="mt-6 pt-6 border-t border-slate-800 text-xs text-slate-400">
            <p className="font-semibold text-slate-300 mb-1.5">Default Bootstrap Administrator:</p>
            <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800/80 font-mono text-[11px] text-slate-400 space-y-1">
              <p>Username: <span className="text-blue-400">admin</span></p>
              <p>Password: <span className="text-blue-400">SentinelAdmin!2026Secure</span></p>
            </div>
          </div>
        </div>

        <p className="text-center text-xs text-slate-400 mt-6">
          SentinelEDR Educational Prototype — SOC Training & Research
        </p>
      </div>
    </div>
  );
};
