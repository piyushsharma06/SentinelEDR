import React from 'react';
import {
  LayoutDashboard,
  Server,
  Activity,
  AlertOctagon,
  ShieldAlert,
  FileCode,
  ScrollText,
  Settings,
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onTabChange: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onTabChange }) => {
  const navItems = [
    { id: 'overview', label: 'Security Overview', icon: LayoutDashboard },
    { id: 'endpoints', label: 'Endpoints', icon: Server },
    { id: 'events', label: 'Event Explorer', icon: Activity },
    { id: 'alerts', label: 'Alerts', icon: AlertOctagon },
    { id: 'incidents', label: 'Incidents', icon: ShieldAlert },
    { id: 'rules', label: 'Detection Rules', icon: FileCode },
    { id: 'audit', label: 'Audit Logs', icon: ScrollText },
    { id: 'settings', label: 'Agent Setup', icon: Settings },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-[#0B0F19] flex flex-col shrink-0">
      <div className="p-4 space-y-1">
        <p className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          SOC Operations
        </p>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      <div className="mt-auto p-4 border-t border-slate-800/60">
        <div className="rounded-lg bg-slate-900/60 border border-slate-800 p-3 text-xs">
          <div className="flex items-center gap-2 text-slate-300 font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>Detection Engine Active</span>
          </div>
          <p className="mt-1 text-[11px] text-slate-400">
            Rules continuously evaluating endpoint telemetry streams.
          </p>
        </div>
      </div>
    </aside>
  );
};
