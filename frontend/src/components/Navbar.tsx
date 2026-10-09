import React from 'react';
import { Shield, LogOut, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface NavbarProps {
  demoMode?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ demoMode = false }) => {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 border-b border-slate-800 bg-[#0F172A]/90 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-40">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
          <Shield className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-base tracking-tight text-white">SentinelEDR</span>
            <span className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
              v1.0
            </span>
            {demoMode && (
              <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 animate-pulse">
                Demo
              </span>
            )}
          </div>
          <p className="text-[11px] text-slate-400 hidden sm:block">Endpoint Detection & Response Platform</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {user && (
          <div className="flex items-center gap-3 pl-4 border-l border-slate-800">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
                <User className="w-4 h-4" />
              </div>
              <div className="hidden sm:block text-left">
                <p className="text-xs font-semibold text-slate-200">{user.username}</p>
                <p className="text-[10px] uppercase tracking-wider text-slate-400 font-medium">{user.role}</p>
              </div>
            </div>

            <button
              onClick={logout}
              title="Sign Out"
              className="p-2 rounded-lg text-slate-400 hover:text-red-400 hover:bg-slate-800/80 transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
